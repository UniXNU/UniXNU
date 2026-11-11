#!/usr/bin/env python3
# Usage: put Linux v6.6 drivers/net/wireless/ath/ath11k/{hal.h,hal_desc.h,hal_rx.h,dp.h,hw.c,hal.c} next to this
# script and run it with python3 -I; it prints the qca6390 DP ring table used in bsd/dev/sweet_wldp.c.
"""Evaluate ath11k (Linux v6.6) definitions for qca6390 and print the DP ring table for sweet_wldp.c."""
import re, sys, os

D = os.path.dirname(os.path.abspath(__file__))
src = {f: open(os.path.join(D, f)).read() for f in ['hal.h', 'hal_desc.h', 'dp.h', 'hw.c', 'hal.c', 'hal_rx.h' if os.path.exists(os.path.join(D, 'hal_rx.h')) else 'hal.h']}

def strip(s):
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
    return re.sub(r'//[^\n]*', '', s)

ALL = strip(src['hal.h'] + '\n' + src['hal_desc.h'] + '\n' + src['dp.h'])

# qca6390_regs
m = re.search(r'const struct ath11k_hw_regs qca6390_regs = \{(.*?)\n\};', src['hw.c'], re.S)
REGS = {k: int(v, 0) for k, v in re.findall(r'\.(\w+)\s*=\s*(0x[0-9a-fA-F]+|\d+)', m.group(1))}

ENUM = {}
# defines (single-line)
DEF = {}
for name, args, body in re.findall(r'#define\s+(\w+)(\([^)]*\))?[ \t]+((?:[^\n\\]|\\\n)*)', ALL):
    if not args:
        DEF[name] = body.replace('\\\n', ' ').strip()

def ev(x, depth=0):
    x = x.strip()
    if depth > 40:
        raise ValueError(x)
    x = re.sub(r'ab->hw_params\.regs->(\w+)', lambda mm: str(REGS[mm.group(1)]), x)
    x = re.sub(r'\b(\w+)\(ab\)', lambda mm: mm.group(1), x)
    x = re.sub(r'GENMASK\((\d+),\s*(\d+)\)', lambda mm: str(((1 << (int(mm.group(1)) + 1)) - 1) & ~((1 << int(mm.group(2))) - 1)), x)
    x = re.sub(r'BIT\((\d+)\)', lambda mm: str(1 << int(mm.group(1))), x)
    x = re.sub(r'sizeof\(struct (\w+)\)', lambda mm: str(sizeof(mm.group(1))), x)
    def name(mm):
        n = mm.group(0)
        if n in ENUM:
            return str(ENUM[n])
        if n in DEF:
            return '(' + str(ev(DEF[n], depth + 1)) + ')'
        return n
    x = re.sub(r'\b[A-Za-z_]\w*\b', name, x)
    x = re.sub(r'(\d+)[uUlL]+\b', r'\1', x)
    return int(eval(x.replace('/', '//')))

# enums (parsed after ev() exists, so BIT()/GENMASK() values evaluate)
for body in re.findall(r'enum \w+ \{(.*?)\};', ALL, re.S):
    v = -1
    for e in body.split(','):
        e = e.strip()
        if not e or e.startswith('#'):
            continue
        if '=' in e:
            k, x = [t.strip() for t in e.split('=', 1)]
            try:
                v = ev(x)
            except Exception:
                try:
                    v = int(x, 0)
                except Exception:
                    v = ENUM.get(x, 0)
        else:
            k = e
            v += 1
        if re.match(r'^\w+$', k):
            ENUM[k] = v

STRUCTS = {}
for nm, body in re.findall(r'struct (\w+) \{([^{}]*)\}\s*__packed;', ALL):
    STRUCTS[nm] = strip(body)

TSZ = {'u8': 1, 'u16': 2, 'u32': 4, 'u64': 8, '__le16': 2, '__le32': 4, '__le64': 8, 'int': 4}

def sizeof(nm):
    body = STRUCTS[nm]
    total = 0
    for line in body.split(';'):
        line = ' '.join(line.split())
        if not line:
            continue
        if line.startswith('union'):
            raise ValueError('union in ' + nm)
        mm = re.match(r'(struct (\w+)|(\w+)) (\w+)(\[(.*?)\])?(\s*:\s*\d+)?$', line)
        if not mm:
            raise ValueError(nm + ': ' + line)
        sz = sizeof(mm.group(2)) if mm.group(2) else TSZ[mm.group(3)]
        n = ev(mm.group(6)) if mm.group(6) else 1
        if mm.group(6) == '':
            n = 0
        total += sz * n
    return total

def esz(*structs):
    return sum(sizeof(s) for s in structs) >> 2

UMAC_REO, UMAC_TCL, UMAC_WBM = 0xa38000, 0xa44000, 0xa34000
R = REGS
rings = []
def ring(name, typ, num, r0, r2, rid, e, n, dirsrc, int0, int1=0):
    rings.append((name, typ, num, r0, r2, rid, e, n, dirsrc, int0, int1))

# interrupt thresholds (ath11k_dp_srng_setup): src rings: IX0 = timer<<16 | batch*esz; dst: (timer>>3)<<16 | batch*esz
B_OTH, T_OTH = ev('HAL_SRNG_INT_BATCH_THRESHOLD_OTHER'), ev('HAL_SRNG_INT_TIMER_THRESHOLD_OTHER')
B_TX, T_TX = ev('HAL_SRNG_INT_BATCH_THRESHOLD_TX'), ev('HAL_SRNG_INT_TIMER_THRESHOLD_TX')
B_RX, T_RX = ev('HAL_SRNG_INT_BATCH_THRESHOLD_RX'), ev('HAL_SRNG_INT_TIMER_THRESHOLD_RX')
def isrc(b, t, e): return (t << 16) | (b * e)
def idst(b, t, e): return ((t >> 3) << 16) | (b * e)

# n_link_desc (ath11k_wbm_idle_ring_setup)
nm_l = ev('(DP_NUM_TIDS_MAX * DP_AVG_MPDUS_PER_TID_MAX) / HAL_NUM_MPDUS_PER_LINK_DESC')
nq = nm_l // ev('HAL_NUM_MPDU_LINKS_PER_QUEUE_DESC')
ntx = ev('(DP_NUM_TIDS_MAX * DP_AVG_FLOWS_PER_TID * DP_AVG_MSDUS_PER_FLOW) / HAL_NUM_TX_MSDUS_PER_LINK_DESC')
nrx = ev('(DP_NUM_TIDS_MAX * DP_AVG_MPDUS_PER_TID_MAX * DP_AVG_MSDUS_PER_MPDU) / HAL_NUM_RX_MSDUS_PER_LINK_DESC')
nlink = nm_l + nq + ntx + nrx
if nlink & (nlink - 1):
    nlink = 1 << nlink.bit_length()

e = esz('hal_wbm_link_desc')
ring('wbm_idle', 'HAL_WBM_IDLE_LINK', 0, UMAC_WBM + R['hal_wbm_idle_link_ring_base_lsb'], UMAC_WBM + ev('HAL_WBM_IDLE_LINK_RING_HP'),
     ENUM['HAL_SRNG_RING_ID_WBM_IDLE_LINK'], e, nlink, 1, isrc(B_OTH, T_OTH, e))
e = esz('hal_wbm_release_ring')
ring('sw2wbm_rel', 'HAL_SW2WBM_RELEASE', 0, UMAC_WBM + R['hal_wbm_release_ring_base_lsb'], UMAC_WBM + ev('HAL_WBM_RELEASE_RING_HP'),
     ENUM['HAL_SRNG_RING_ID_WBM_SW_RELEASE'], e, ev('DP_WBM_RELEASE_RING_SIZE'), 1, isrc(B_OTH, T_OTH, e))
e = esz('hal_tlv_hdr', 'hal_tcl_gse_cmd')
ring('tcl_cmd', 'HAL_TCL_CMD', 0, UMAC_TCL + R['hal_tcl_ring_base_lsb'], UMAC_TCL + ev('HAL_TCL_RING_HP'),
     ENUM['HAL_SRNG_RING_ID_SW2TCL_CMD'], e, ev('DP_TCL_CMD_RING_SIZE'), 1, isrc(B_OTH, T_OTH, e))
e = esz('hal_tlv_hdr', 'hal_tcl_status_ring')
ring('tcl_status', 'HAL_TCL_STATUS', 0, UMAC_TCL + R['hal_tcl_status_ring_base_lsb'], UMAC_TCL + ev('HAL_TCL_STATUS_RING_HP'),
     ENUM['HAL_SRNG_RING_ID_TCL_STATUS'], e, ev('DP_TCL_STATUS_RING_SIZE'), 0, idst(B_OTH, T_OTH, e))
# tcl2wbm map ipq8074 entry 0: tcl 0, wbm 0
e = esz('hal_tlv_hdr', 'hal_tcl_data_cmd')
ring('tcl_data0', 'HAL_TCL_DATA', 0, UMAC_TCL + R['hal_tcl1_ring_base_lsb'], UMAC_TCL + ev('HAL_TCL1_RING_HP'),
     ENUM['HAL_SRNG_RING_ID_SW2TCL1'], e, ev('DP_TCL_DATA_RING_SIZE'), 1, isrc(B_OTH, T_OTH, e))
e = esz('hal_wbm_release_ring')
w0, w0hp = R['hal_wbm0_release_ring_base_lsb'], ev('HAL_WBM0_RELEASE_RING_HP')
wst, wst2 = R['hal_wbm1_release_ring_base_lsb'] - w0, ev('HAL_WBM1_RELEASE_RING_HP') - w0hp
ring('tx_comp0', 'HAL_WBM2SW_RELEASE', 0, UMAC_WBM + w0, UMAC_WBM + w0hp,
     ENUM['HAL_SRNG_RING_ID_WBM2SW0_RELEASE'], e, ev('DP_TX_COMP_RING_SIZE'), 0, idst(B_TX, T_TX, e))
e = esz('hal_reo_entrance_ring')
ring('reo_reinject', 'HAL_REO_REINJECT', 0, UMAC_REO + R['hal_sw2reo_ring_base_lsb'], UMAC_REO + R['hal_sw2reo_ring_hp'],
     ENUM['HAL_SRNG_RING_ID_SW2REO'], e, ev('DP_REO_REINJECT_RING_SIZE'), 1, isrc(B_OTH, T_OTH, e))
e = esz('hal_wbm_release_ring')
n3 = ev('DP_RX_RELEASE_RING_NUM')
ring('rx_rel', 'HAL_WBM2SW_RELEASE', n3, UMAC_WBM + w0 + n3 * wst, UMAC_WBM + w0hp + n3 * wst2,
     ENUM['HAL_SRNG_RING_ID_WBM2SW0_RELEASE'] + n3, e, ev('DP_RX_RELEASE_RING_SIZE'), 0, idst(B_OTH, T_OTH, e))
e = esz('hal_reo_dest_ring')
ring('reo_except', 'HAL_REO_EXCEPTION', 0, UMAC_REO + R['hal_reo_tcl_ring_base_lsb'], UMAC_REO + R['hal_reo_tcl_ring_hp'],
     ENUM['HAL_SRNG_RING_ID_REO2TCL'], e, ev('DP_REO_EXCEPTION_RING_SIZE'), 0, idst(B_OTH, T_OTH, e))
e = esz('hal_tlv_hdr', 'hal_reo_get_queue_stats')
ring('reo_cmd', 'HAL_REO_CMD', 0, UMAC_REO + R['hal_reo_cmd_ring_base_lsb'], UMAC_REO + R['hal_reo_cmd_ring_hp'],
     ENUM['HAL_SRNG_RING_ID_REO_CMD'], e, ev('DP_REO_CMD_RING_SIZE'), 1, isrc(B_OTH, T_OTH, e))
e = esz('hal_tlv_hdr', 'hal_reo_get_queue_stats_status')
ring('reo_status', 'HAL_REO_STATUS', 0, UMAC_REO + R['hal_reo_status_ring_base_lsb'], UMAC_REO + R['hal_reo_status_hp'],
     ENUM['HAL_SRNG_RING_ID_REO_STATUS'], e, ev('DP_REO_STATUS_RING_SIZE'), 0, idst(B_OTH, T_OTH, e))
e = esz('hal_reo_dest_ring')
r1, r1hp = R['hal_reo1_ring_base_lsb'], R['hal_reo1_ring_hp']
rs, rs2 = R['hal_reo2_ring_base_lsb'] - r1, R['hal_reo2_ring_hp'] - r1hp
for i in range(ev('DP_REO_DST_RING_MAX')):
    ring('reo_dst%d' % i, 'HAL_REO_DST', i, UMAC_REO + r1 + i * rs, UMAC_REO + r1hp + i * rs2,
         ENUM['HAL_SRNG_RING_ID_REO2SW1'] + i, e, ev('DP_REO_DST_RING_SIZE'), 0, idst(B_RX, T_RX, e))

print('/* generated by gen_dp.py from ath11k v6.6 hal.h/hal_desc.h/dp.h/hw.c (qca6390) */')
print('/* name                 R0          R2          id  esz  entries src int0 */')
for (nm, typ, num, r0, r2, rid, e, n, s, i0, i1) in rings:
    print('\t{ "%s", 0x%06x, 0x%06x, %3d, %2d, %5d, %d, 0x%08x },' % (nm, r0, r2, rid, e, n, s, i0))
tot = sum(e * 4 * n for (_, _, _, _, _, _, e, n, _, _, _) in rings)
print('/* ring bytes %#x; link descs %d x %d bytes; HAL_LINK_DESC_ALIGN %d; DP_LINK_DESC_ALLOC_SIZE_THRESH %#x */' % (
    tot, nlink, ev('HAL_LINK_DESC_SIZE'), ev('HAL_LINK_DESC_ALIGN'), ev('DP_LINK_DESC_ALLOC_SIZE_THRESH')))
for k in ['HAL_RING_BASE_ALIGN', 'HAL_REO1_GEN_ENABLE', 'HAL_REO1_GEN_ENABLE_FRAG_DST_RING', 'HAL_REO1_GEN_ENABLE_AGING_LIST_ENABLE',
          'HAL_REO1_GEN_ENABLE_AGING_FLUSH_ENABLE', 'HAL_DEFAULT_REO_TIMEOUT_USEC', 'HAL_REO_DEST_RING_CTRL_HASH_RING_MAP',
          'HAL_HASH_ROUTING_RING_SW1', 'HAL_HASH_ROUTING_RING_SW2', 'HAL_HASH_ROUTING_RING_SW3', 'HAL_HASH_ROUTING_RING_SW4',
          'HAL_REO1_DEST_RING_CTRL_IX_0', 'HAL_TLV_HDR_TAG', 'HAL_TLV_HDR_LEN', 'HAL_TCL_DATA_CMD',
          'HAL_REO_CMD_HDR_INFO0_CMD_NUMBER', 'HAL_TCL1_RING_CMN_CTRL_REG', 'HAL_TCL1_RING_CMN_CTRL_DSCP_TID_MAP_PROG_EN',
          'HAL_TCL1_RING_DSCP_TID_MAP', 'HAL_DSCP_TID_MAP_TBL_NUM_ENTRIES_MAX', 'HAL_DSCP_TID_TBL_SIZE',
          'BUFFER_ADDR_INFO0_ADDR', 'BUFFER_ADDR_INFO1_ADDR', 'BUFFER_ADDR_INFO1_RET_BUF_MGR', 'BUFFER_ADDR_INFO1_SW_COOKIE',
          'HAL_SRNG_RING_ID_REO2SW1']:
    try:
        print('/* %-45s %#x */' % (k, ev(k)))
    except Exception as ex:
        print('/* %-45s ? %s */' % (k, ex))
for k in ['hal_reo1_aging_thresh_ix_0', 'hal_reo1_aging_thresh_ix_1', 'hal_reo1_aging_thresh_ix_2', 'hal_reo1_aging_thresh_ix_3',
          'hal_wbm_idle_link_ring_misc', 'hal_reo1_misc_ctl']:
    print('/* %-45s %#x */' % (k, R.get(k, -1)))
print('/* sizeof hal_tcl_data_cmd %d, hal_reo_get_queue_stats %d, hal_tlv_hdr %d */' % (
    sizeof('hal_tcl_data_cmd'), sizeof('hal_reo_get_queue_stats'), sizeof('hal_tlv_hdr')))

MAXSZ = {'HAL_WBM_IDLE_LINK': 'HAL_WBM_IDLE_LINK_RING_BASE_MSB_RING_SIZE', 'HAL_SW2WBM_RELEASE': 'HAL_SW2WBM_RELEASE_RING_BASE_MSB_RING_SIZE',
         'HAL_TCL_CMD': 'HAL_SW2TCL1_CMD_RING_BASE_MSB_RING_SIZE', 'HAL_TCL_STATUS': 'HAL_TCL_STATUS_RING_BASE_MSB_RING_SIZE',
         'HAL_TCL_DATA': 'HAL_SW2TCL1_RING_BASE_MSB_RING_SIZE', 'HAL_WBM2SW_RELEASE': 'HAL_WBM2SW_RELEASE_RING_BASE_MSB_RING_SIZE',
         'HAL_REO_REINJECT': 'HAL_REO_SW2REO_RING_BASE_MSB_RING_SIZE', 'HAL_REO_EXCEPTION': 'HAL_REO_REO2TCL_RING_BASE_MSB_RING_SIZE',
         'HAL_REO_CMD': 'HAL_REO_CMD_RING_BASE_MSB_RING_SIZE', 'HAL_REO_STATUS': 'HAL_REO_STATUS_RING_BASE_MSB_RING_SIZE',
         'HAL_REO_DST': 'HAL_REO_REO2SW1_RING_BASE_MSB_RING_SIZE'}
print('/* max entries per ring (max_size / entry_size): */')
for (nm, typ, num, r0, r2, rid, e, n, s, i0, i1) in rings:
    print('/*   %-14s max %6d (requested %d) */' % (nm, ev(MAXSZ[typ]) // e, n))
