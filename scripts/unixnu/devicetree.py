"""FDT hardware descriptions and Apple device-tree payloads."""
from dataclasses import dataclass, field
from pathlib import Path
import os
import re
import struct
import uuid
import zlib

from .util import Error, run, tool


def node(name, properties=(), children=()):
    properties = [('name', name.encode() + b'\0'), *properties]
    result = struct.pack('<II', len(properties), len(children))
    for key, data in properties:
        if len(key.encode()) > 31:
            raise Error(f'ADT property name exceeds 31 bytes: {key}')
        result += struct.pack('<32sI', key.encode(), len(data))
        result += data + bytes(-len(data) % 4)
    return result + b''.join(children)


def empty_nvram_proxy():
    """Encode the volatile CHRP bank consumed by IODTNVRAM."""
    def header(name, size):
        raw = bytearray(struct.pack('<BBH12s', 0x70, 0, size // 16, name))
        checksum = sum(raw)
        while checksum > 255:
            checksum = (checksum & 255) + (checksum >> 8)
        raw[1] = checksum
        return raw

    image = bytearray(8192)
    image[:16] = header(b'nvram', 32)
    image[32:48] = header(b'common', 16 + 2048)
    free_at = 32 + 16 + 2048
    image[free_at:free_at + 16] = header(b'free', len(image) - free_at)
    struct.pack_into('<I', image, 16, zlib.adler32(image[20:]))
    return [('nvram-bank-size', struct.pack('<I', len(image))),
            ('nvram-bank-count', struct.pack('<I', 1)),
            ('nvram-current-bank', struct.pack('<I', 0)),
            ('nvram-proxy-data', bytes(image))]


@dataclass
class FdtNode:
    name: str
    parent: object = None
    properties: dict = field(default_factory=dict)
    children: list = field(default_factory=list)

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()

    def strings(self, key):
        raw = self.properties.get(key, b'')
        if raw and not raw.endswith(b'\0'):
            raise Error(f'{self.name}: {key} requires terminated strings')
        return [value.decode() for value in raw.rstrip(b'\0').split(b'\0')] if raw else []

    def cells(self, key):
        raw = self.properties.get(key, b'')
        if len(raw) % 4:
            raise Error(f'{self.name}: {key} requires 32-bit FDT cells')
        return list(struct.unpack(f'>{len(raw) // 4}I', raw))

    def scalar(self, key, default=None):
        values = self.cells(key)
        if not values and default is not None:
            return default
        if len(values) != 1:
            raise Error(f'{self.name}: {key} requires one cell')
        return values[0]

    def enabled(self):
        return self.strings('status') in ([], ['okay'], ['ok']) and (self.parent is None or self.parent.enabled())


def read_fdt(blob):
    """Read the version-17 flattened tree token stream."""
    if len(blob) < 40:
        raise Error('FDT header is truncated')
    magic, total, structure, strings, _, version, _, _, string_bytes, structure_bytes = struct.unpack_from('>10I', blob)
    if (magic != 0xd00dfeed or total > len(blob) or version != 17 or
            strings + string_bytes > total or structure + structure_bytes > total):
        raise Error('Invalid FDT header')
    stack, root = [], None
    cursor, limit = structure, structure + structure_bytes
    while cursor + 4 <= limit:
        tag = struct.unpack_from('>I', blob, cursor)[0]
        cursor += 4
        if tag == 1:
            end = blob.find(b'\0', cursor, limit)
            if end < 0:
                raise Error('Unterminated FDT node')
            entry = FdtNode(blob[cursor:end].decode(), stack[-1] if stack else None)
            if stack:
                stack[-1].children.append(entry)
            elif root is None:
                root = entry
            else:
                raise Error('FDT has multiple roots')
            stack.append(entry)
            cursor = (end + 4) & ~3
        elif tag == 2:
            if not stack:
                raise Error('Unbalanced FDT node')
            stack.pop()
        elif tag == 3:
            if not stack or cursor + 8 > limit:
                raise Error('Invalid FDT property')
            length, offset = struct.unpack_from('>II', blob, cursor)
            cursor += 8
            end = blob.find(b'\0', strings + offset, strings + string_bytes)
            if offset >= string_bytes or end < 0 or cursor + length > limit:
                raise Error('Truncated FDT property')
            name = blob[strings + offset:end].decode()
            if name in stack[-1].properties:
                raise Error(f'Duplicate FDT property: {name}')
            stack[-1].properties[name] = blob[cursor:cursor + length]
            cursor = (cursor + length + 3) & ~3
        elif tag == 9:
            if root is None or stack:
                raise Error('Incomplete FDT tree')
            return root
        elif tag != 4:
            raise Error(f'Unknown FDT token: {tag}')
    raise Error('FDT end token is missing')


def number(cells):
    value = 0
    for cell in cells:
        value = (value << 32) | cell
    return value


def cell_count(bus, key, default):
    count = bus.scalar(key, default)
    if count not in (0, 1, 2):
        raise Error(f'{bus.name}: unsupported {key}={count}')
    return count


def registers(entry):
    bus = entry.parent
    address_cells = cell_count(bus, '#address-cells', 2)
    size_cells = cell_count(bus, '#size-cells', 1)
    stride = address_cells + size_cells
    cells = entry.cells('reg')
    if not stride or len(cells) % stride:
        raise Error(f'{entry.name}: invalid register ranges')
    return [(number(cells[i:i + address_cells]), number(cells[i + address_cells:i + stride]))
            for i in range(0, len(cells), stride)]


def physical(bus, address, size):
    """Translate a register range through each parent bus."""
    while bus.parent is not None:
        if 'ranges' not in bus.properties:
            raise Error(f'{bus.name}: ranges is required for address translation')
        cells = bus.cells('ranges')
        if cells:
            child_n = cell_count(bus, '#address-cells', 2)
            parent_n = cell_count(bus.parent, '#address-cells', 2)
            size_n = cell_count(bus, '#size-cells', 1)
            width = child_n + parent_n + size_n
            if not width or len(cells) % width:
                raise Error(f'{bus.name}: malformed ranges')
            matches = []
            for i in range(0, len(cells), width):
                child = number(cells[i:i + child_n])
                parent = number(cells[i + child_n:i + child_n + parent_n])
                length = number(cells[i + child_n + parent_n:i + width])
                if child <= address and address + size <= child + length:
                    matches.append(parent + address - child)
            if len(matches) != 1:
                raise Error(f'{bus.name}: register range needs one matching translation')
            address = matches[0]
        bus = bus.parent
    if address < 0 or size < 0 or address + size > 1 << 64:
        raise Error('Register range exceeds the 64-bit address space')
    return address


ARM_IO_ALIGN = 1 << 24


def arm_io_window(hardware):
    """The arm-io window: child registers are offsets from its base, which XNU reads as the SoC base and requires to be non-zero."""
    spans = [(physical(entry.parent, address, size), size) for entry in hardware if 'reg' in entry.properties
             for address, size in registers(entry)]
    if not spans:
        return ARM_IO_ALIGN, ARM_IO_ALIGN
    base = min(address for address, _ in spans) & ~(ARM_IO_ALIGN - 1)
    top = -(-max(address + size for address, size in spans) // ARM_IO_ALIGN) * ARM_IO_ALIGN
    if not base:
        raise Error('arm-io needs a non-zero base: an exported register lies below 16 MiB')
    return base, top - base


STRINGS = {'compatible', 'device_type', 'reg-names', 'interrupt-names', 'clock-names', 'method'}
U32 = {'phandle', 'linux,phandle', '#interrupt-cells', '#iommu-cells', '#clock-cells', 'clock-frequency', 'timebase-frequency'}
U64 = {'redistributor-stride'}
FLAGS = {'interrupt-controller', 'dma-coherent'}
REFERENCES = {'interrupt-parent': None, 'iommus': '#iommu-cells', 'clocks': '#clock-cells'}


def hardware_properties(entry, handles, base=0):
    properties = []
    for key, raw in entry.properties.items():
        if key in STRINGS:
            entry.strings(key)
            properties.append((key, raw))
        elif key in U32:
            properties.append((key, struct.pack('<I', entry.scalar(key))))
        elif key in U64:
            cells = entry.cells(key)
            if len(cells) not in (1, 2):
                raise Error(f'{entry.name}: {key} requires one or two cells')
            properties.append((key, struct.pack('<Q', number(cells))))
        elif key in FLAGS:
            if raw:
                raise Error(f'{entry.name}: {key} is a flag')
            properties.append((key, b''))
        elif key in REFERENCES:
            cells, index = entry.cells(key), 0
            while index < len(cells):
                target = handles.get(cells[index])
                if target is None or not target.enabled():
                    raise Error(f'{entry.name}: unresolved {key} reference')
                count = target.scalar(REFERENCES[key]) if REFERENCES[key] else 0
                index += count + 1
            if index != len(cells) or not cells:
                raise Error(f'{entry.name}: invalid {key} arguments')
            properties.append((key, struct.pack(f'<{len(cells)}I', *cells)))
        elif key == 'interrupts':
            provider = entry
            while provider and 'interrupt-parent' not in provider.properties:
                provider = provider.parent
            handle = provider.scalar('interrupt-parent') if provider else None
            controller = handles.get(handle)
            cells = entry.cells(key)
            width = controller.scalar('#interrupt-cells') if controller else 0
            if not width or len(cells) % width:
                raise Error(f'{entry.name}: interrupt provider or specifier is invalid')
            properties.append((key, struct.pack(f'<{len(cells)}I', *cells)))
            if 'interrupt-parent' not in entry.properties:
                properties.append(('interrupt-parent', struct.pack('<I', handle)))
        elif key == 'reg':
            pairs = [(physical(entry.parent, address, size) - base, size) for address, size in registers(entry)]
            properties.append((key, b''.join(struct.pack('<QQ', *pair) for pair in pairs)))
    return properties


def typed_properties(table):
    result = []
    for kind, properties in table.items():
        if kind not in ('string', 'strings', 'u32', 'u64', 'bytes'):
            raise Error(f'Unknown ADT property type: {kind}')
        for key, value in properties.items():
            if kind == 'string':
                raw = value.encode() + b'\0'
            elif kind == 'strings':
                raw = b''.join(item.encode() + b'\0' for item in value)
            elif kind == 'bytes':
                raw = bytes.fromhex(value)
            else:
                raw = struct.pack('<I' if kind == 'u32' else '<Q', int(value, 0) if isinstance(value, str) else value)
            result.append((key, raw))
    return result


def generate(dtb, config, *, unique_chip_id=None, data=False, trust=False, addon=False):
    root = read_fdt(Path(dtb).read_bytes())
    entries = list(root.walk())
    handles = {}
    for entry in entries:
        if 'phandle' in entry.properties:
            handle = entry.scalar('phandle')
            if not handle or handle in handles:
                raise Error('FDT phandles must be unique and nonzero')
            handles[handle] = entry
    payload, platform = config.get('payload', {}), config.get('adt', {})
    options = payload.get('adt', {})
    memory = [entry for entry in root.children if entry.strings('device_type') == ['memory'] and entry.enabled()]
    if len(memory) != 1 or len(registers(memory[0])) != 1:
        raise Error('ADT handoff requires one contiguous DRAM range')
    dram_base, dram_size = registers(memory[0])[0]
    if payload.get('dram_size') is not None and int(str(payload['dram_size']), 0) != dram_size:
        raise Error('payload.dram_size differs from the hardware DTS')
    chosen = [('random-seed', os.urandom(64)), ('dram-base', struct.pack('<Q', dram_base)),
              ('dram-size', struct.pack('<Q', dram_size)), *empty_nvram_proxy()]
    if unique_chip_id:
        seed = int(str(unique_chip_id), 16)
        chip = int(str(options['chip_id']), 16)
        if not 0 < seed < 1 << 64 or not 0 < chip < 1 << 32:
            raise Error('Platform identity requires a nonzero u64 seed and u32 chip ID')
        chosen += [('unique-chip-id', struct.pack('<Q', seed)), ('chip-id', struct.pack('<I', chip))]
    elif options.get('unique_chip_id') == 'required':
        raise Error('Pass --unique-chip-id HEX for this board')
    if options.get('owned_memory_size'):
        size = int(str(options['owned_memory_size']), 0)
        if not 0x10000000 <= size <= 0x200000000 or size % 0x200000:
            raise Error('Owned memory must be 256 MiB to 8 GiB in 2 MiB steps')
        chosen.append(('darwinboot-memory-size', struct.pack('<Q', size)))
    if options.get('root_match_volume_uuid'):
        volume = str(uuid.UUID(options['root_match_volume_uuid'])).upper()
        chosen.append(('root-matching', ('<dict><key>IOProviderClass</key><string>IOMedia</string>'
                       '<key>IOPropertyMatch</key><dict><key>UUID</key><string>' + volume + '</string></dict></dict>\0').encode()))
    if data and not options.get('persistent_data'):
        chosen.append(('ephemeral-storage', struct.pack('<I', 1)))
    if payload.get('text_fixups'):
        for value in payload['text_fixups']:
            if not re.fullmatch(r'[A-Za-z0-9_.\-]{1,63},[0-9a-fA-F]{1,16},(?:[0-9a-fA-F]{2}){1,16},(?:[0-9a-fA-F]{2}){1,16}', value) or len(value) >= 160:
                raise Error(f'Malformed text fixup: {value}')
        chosen.append(('text-fixups', b''.join(value.encode() + b'\0' for value in payload['text_fixups'])))
    chosen += typed_properties(platform.get('chosen', {}))
    mappings = [('PackedRAMDisk' if options.get('packed_data_ramdisk') else 'RAMDisk', bytes(16))] if data else []
    mappings += [('TrustCache', bytes(16))] if trust else []
    mappings += [('GpuAddon', bytes(16))] if addon else []
    children = [node('chosen', chosen, [node('memory-map', mappings), node('manifest-properties')])]
    cpus = next((entry for entry in root.children if entry.name == 'cpus'), None)
    if cpus is None:
        raise Error('Hardware DTS requires /cpus')
    cpu_nodes = []
    for entry in cpus.children:
        if not entry.enabled():
            continue
        values = registers(entry)
        if len(values) != 1 or values[0][0] > 0xffffffff:
            raise Error(f'{entry.name}: CPU affinity must fit a u32')
        cpu_nodes.append(node(f'cpu{len(cpu_nodes)}', [('reg', struct.pack('<I', values[0][0])),
                         ('state', b'running\0' if not cpu_nodes else b'waiting\0'), ('device_type', b'cpu\0'),
                         ('compatible', entry.properties['compatible']),
                         ('timebase-frequency', struct.pack('<I', cpus.scalar('timebase-frequency')))]))
    if not cpu_nodes:
        raise Error('Hardware DTS requires an enabled boot CPU')
    children.append(node('cpus', children=cpu_nodes))
    psci = next((entry for entry in root.children if entry.name == 'psci'), None)
    if len(cpu_nodes) > 1:
        if psci is None or psci.strings('method') not in (['smc'], ['hvc']):
            raise Error('Multiple CPUs require a PSCI method')
        children.append(node('psci', hardware_properties(psci, handles)))
    hardware = [entry for entry in entries if 'unixnu,adt-name' in entry.properties and entry.enabled()]
    names = [entry.strings('unixnu,adt-name')[0] for entry in hardware]
    if len(set(names)) != len(names):
        raise Error('Exported ADT hardware names must be unique')
    base, size = arm_io_window(hardware)
    children.append(node('arm-io', [('device_type', b'arm-io\0'), ('#address-cells', struct.pack('<I', 2)),
                         ('#size-cells', struct.pack('<I', 2)), ('ranges', struct.pack('<QQQ', 0, base, size))],
                         [node(name, hardware_properties(entry, handles, base)) for name, entry in zip(names, hardware)]))
    for name in ('defaults', 'options', 'product', 'buttons'):
        if name in platform or name in ('defaults', 'options', 'product'):
            children.append(node(name, typed_properties(platform.get(name, {}))))
    root_properties = [('compatible', root.properties['compatible']), ('#address-cells', struct.pack('<I', 2)),
                       ('#size-cells', struct.pack('<I', 2)), *typed_properties(platform.get('root', {}))]
    if not any(key == 'model' for key, _ in root_properties):
        root_properties.append(('model', root.properties['model']))
    return node('device-tree', root_properties, children)


def compile_hardware(ctx):
    from .profiles import resolve_path
    spec = ctx.board.get('device_tree', {})
    source = resolve_path(ctx, spec['source'])
    output = ctx.work / 'device-tree/hardware.dtb'
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [tool('dtc', 'brew install dtc'), '-I', 'dts', '-O', 'dtb', '-o', output]
    for directory in spec.get('include_dirs', []):
        command += ['-i', resolve_path(ctx, directory)]
    run([*command, source], log_file=ctx.logs / 'device-tree.log')
    return output
