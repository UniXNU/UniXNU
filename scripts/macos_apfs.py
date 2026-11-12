"""Native APFS.framework operations used by macOS Apple Software Restore."""
import ctypes as C
import re
import sys
import uuid


class APFS:
    def __init__(self):
        if sys.platform != 'darwin':
            raise RuntimeError('APFS.framework requires macOS')
        self.cf = C.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
        self.apfs = C.CDLL('/System/Library/PrivateFrameworks/APFS.framework/Versions/A/APFS')
        self.cf.CFNumberCreate.argtypes = [C.c_void_p, C.c_int, C.c_void_p]
        self.cf.CFNumberCreate.restype = C.c_void_p
        self.cf.CFArrayCreate.argtypes = [C.c_void_p, C.POINTER(C.c_void_p), C.c_long, C.c_void_p]
        self.cf.CFArrayCreate.restype = C.c_void_p
        self.cf.CFRelease.argtypes = [C.c_void_p]
        self.apfs.APFSContainerVolumeGroupAdd.argtypes = [C.c_char_p, C.c_void_p, C.c_void_p]
        self.apfs.APFSContainerVolumeGroupAdd.restype = C.c_int

    def number(self, value):
        value = C.c_int(value)
        result = self.cf.CFNumberCreate(None, 9, C.byref(value))
        if not result:
            raise MemoryError('CFNumberCreate')
        return result

    def group(self, container, volumes):
        container = container.removeprefix('/dev/')
        if not re.fullmatch(r'disk\d+', container):
            raise ValueError('invalid APFS container device')
        indices = []
        for device in volumes:
            match = re.fullmatch(re.escape(container) + r's(\d+)', device.removeprefix('/dev/'))
            if not match:
                raise ValueError('volume is not in the selected APFS container')
            indices.append(int(match[1]))
        numbers = [self.number(index) for index in indices]
        array = self.cf.CFArrayCreate(None, (C.c_void_p * len(numbers))(*numbers), len(numbers), None)
        if not array:
            for number in numbers:
                self.cf.CFRelease(number)
            raise MemoryError('CFArrayCreate')
        identity = (C.c_ubyte * 16)()
        try:
            status = self.apfs.APFSContainerVolumeGroupAdd(container.encode(), array, identity)
            if status:
                raise RuntimeError(f'APFSContainerVolumeGroupAdd failed: {status:#x}')
            return str(uuid.UUID(bytes=bytes(identity))).upper()
        finally:
            self.cf.CFRelease(array)
            for number in numbers:
                self.cf.CFRelease(number)
