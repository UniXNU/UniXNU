/*
 * umi-atone: a freestanding ALSA mixer + tone player for a RAM-booted Linux on the Mi 10 (stock kernel + TWRP
 * ramdisk), to hear the speaker path work under Linux as a reference for the iOS port. No libc: raw aarch64
 * syscalls. Build: tools/umi-atone-build.sh. Usage on the phone:
 *   umi-atone list                          control names, types and enum items
 *   umi-atone set "Control Name" VALUE      integer / boolean, or an enum item by name
 *   umi-atone tone [SECONDS] [AMPLITUDE]    1 kHz sine, S16_LE stereo 48 kHz on /dev/snd/pcmC0D0p (MultiMedia1)
 * Struct layouts: include/uapi/sound/asound.h (64-bit).
 */
typedef unsigned long u64;
typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;
typedef long s64;
typedef int s32;
typedef short s16;

static long
sys6(long n, long a, long b, long c, long d, long e, long f)
{
	register long x8 __asm__("x8") = n, x0 __asm__("x0") = a, x1 __asm__("x1") = b, x2 __asm__("x2") = c;
	register long x3 __asm__("x3") = d, x4 __asm__("x4") = e, x5 __asm__("x5") = f;
	__asm__ volatile ("svc #0" : "+r"(x0) : "r"(x8), "r"(x1), "r"(x2), "r"(x3), "r"(x4), "r"(x5) : "memory");
	return x0;
}
#define SYS_openat 56
#define SYS_close 57
#define SYS_ioctl 29
#define SYS_write 64
#define SYS_exit_group 94
#define SYS_nanosleep 101
#define AT_FDCWD (-100)
#define O_RDWR 2

void *
memset(void *d, int c, u64 n)
{
	u8 *p = d;
	while (n--) {
		*p++ = (u8)c;
	}
	return d;
}

void *
memcpy(void *d, const void *s, u64 n)
{
	u8 *p = d;
	const u8 *q = s;
	while (n--) {
		*p++ = *q++;
	}
	return d;
}

static u64
slen(const char *s)
{
	u64 n = 0;
	while (s[n]) {
		n++;
	}
	return n;
}

static int
seq(const char *a, const char *b)
{
	while (*a && *a == *b) {
		a++, b++;
	}
	return *a == *b;
}

static void
out(const char *s)
{
	sys6(SYS_write, 1, (long)s, (long)slen(s), 0, 0, 0);
}

static void
outn(long v)
{
	char b[24];
	int i = 23;
	int neg = v < 0;
	u64 u = neg ? (u64)(-v) : (u64)v;
	b[i] = 0;
	do {
		b[--i] = (char)('0' + u % 10);
		u /= 10;
	} while (u && i > 1);
	if (neg) {
		b[--i] = '-';
	}
	out(b + i);
}

static long
num(const char *s, int *ok)
{
	long v = 0, sign = 1;
	*ok = 0;
	if (*s == '-') {
		sign = -1, s++;
	}
	if (!*s) {
		return 0;
	}
	while (*s >= '0' && *s <= '9') {
		v = v * 10 + (*s++ - '0');
	}
	*ok = *s == 0;
	return v * sign;
}

#define IOC(dir, type, nr, size) (((u64)(dir) << 30) | ((u64)(size) << 16) | ((u64)(type) << 8) | (u64)(nr))
#define IOWR(t, n, s) IOC(3, t, n, s)
#define IOW(t, n, s) IOC(1, t, n, s)
#define IO(t, n) IOC(0, t, n, 0)

/* ---- control interface ---- */

struct elem_id {
	u32 numid;
	s32 iface;
	u32 device, subdevice;
	char name[44];
	u32 index;
};

struct elem_list {
	u32 offset, space, used, count;
	struct elem_id *pids;
	u8 reserved[50];
};

struct elem_info {
	struct elem_id id;
	s32 type;
	u32 access, count;
	s32 owner;
	union {
		struct {
			s64 min, max, step;
		} integer;
		struct {
			u32 items, item;
			char name[64];
			u64 names_ptr;
			u32 names_length;
		} enumerated;
		u8 reserved[128];
	} value;
	u16 dimen[4];
	u8 reserved[56];
};

struct elem_value {
	struct elem_id id;
	u32 indirect;
	u32 pad;
	union {
		s64 integer[128];
		u32 enumerated[128];
		u8 bytes[512];
	} value;
	u8 reserved[128];
};

#define CTL_ELEM_LIST IOWR('U', 0x10, sizeof(struct elem_list))
#define CTL_ELEM_INFO IOWR('U', 0x11, sizeof(struct elem_info))
#define CTL_ELEM_READ IOWR('U', 0x12, sizeof(struct elem_value))
#define CTL_ELEM_WRITE IOWR('U', 0x13, sizeof(struct elem_value))
#define TYPE_BOOLEAN 1
#define TYPE_INTEGER 2
#define TYPE_ENUMERATED 3

static int ctl = -1;

static int
ctl_open(void)
{
	if (ctl < 0) {
		ctl = (int)sys6(SYS_openat, AT_FDCWD, (long)"/dev/snd/controlC0", O_RDWR, 0, 0, 0);
	}
	return ctl;
}

static int
info_by_name(const char *name, struct elem_info *info)
{
	memset(info, 0, sizeof(*info));
	info->id.iface = 2;             /* SNDRV_CTL_ELEM_IFACE_MIXER */
	memcpy(info->id.name, name, slen(name) < 43 ? slen(name) : 43);
	return (int)sys6(SYS_ioctl, ctl, (long)CTL_ELEM_INFO, (long)info, 0, 0, 0);
}

static void
print_enum_items(struct elem_info *info)
{
	u32 n = info->value.enumerated.items;
	for (u32 i = 0; i < n && i < 64; i++) {
		struct elem_info e = *info;
		e.value.enumerated.item = i;
		if (sys6(SYS_ioctl, ctl, (long)CTL_ELEM_INFO, (long)&e, 0, 0, 0) == 0) {
			out(i ? ", " : " {");
			out(e.value.enumerated.name);
		}
	}
	out("}");
}

static int
cmd_list(void)
{
	static struct elem_id ids[2048];
	struct elem_list l;
	memset(&l, 0, sizeof(l));
	l.space = 2048;
	l.pids = ids;
	if (sys6(SYS_ioctl, ctl, (long)CTL_ELEM_LIST, (long)&l, 0, 0, 0) != 0) {
		out("ELEM_LIST failed\n");
		return 1;
	}
	for (u32 i = 0; i < l.used; i++) {
		struct elem_info info;
		memset(&info, 0, sizeof(info));
		info.id = ids[i];
		if (sys6(SYS_ioctl, ctl, (long)CTL_ELEM_INFO, (long)&info, 0, 0, 0) != 0) {
			continue;
		}
		outn(ids[i].numid);
		out(" '");
		out(ids[i].name);
		out("' type ");
		outn(info.type);
		out(" count ");
		outn(info.count);
		if (info.type == TYPE_ENUMERATED) {
			print_enum_items(&info);
		} else if (info.type == TYPE_INTEGER) {
			out(" [");
			outn(info.value.integer.min);
			out("..");
			outn(info.value.integer.max);
			out("]");
		}
		out("\n");
	}
	return 0;
}

static int
cmd_set(const char *name, const char *val)
{
	struct elem_info info;
	if (info_by_name(name, &info) != 0) {
		out("no control '");
		out(name);
		out("'\n");
		return 1;
	}
	struct elem_value v;
	memset(&v, 0, sizeof(v));
	v.id = info.id;
	int ok = 0;
	long n = num(val, &ok);
	if (info.type == TYPE_ENUMERATED) {
		long found = -1;
		for (u32 i = 0; i < info.value.enumerated.items && found < 0; i++) {
			struct elem_info e = info;
			e.value.enumerated.item = i;
			if (sys6(SYS_ioctl, ctl, (long)CTL_ELEM_INFO, (long)&e, 0, 0, 0) == 0 && seq(e.value.enumerated.name, val)) {
				found = i;
			}
		}
		if (found < 0 && ok) {
			found = n;
		}
		if (found < 0) {
			out("'");
			out(name);
			out("': no item '");
			out(val);
			out("' in");
			print_enum_items(&info);
			out("\n");
			return 1;
		}
		for (u32 c = 0; c < info.count && c < 128; c++) {
			v.value.enumerated[c] = (u32)found;
		}
	} else {
		if (!ok) {
			out("value must be a number\n");
			return 1;
		}
		for (u32 c = 0; c < info.count && c < 128; c++) {
			v.value.integer[c] = n;
		}
	}
	long r = sys6(SYS_ioctl, ctl, (long)CTL_ELEM_WRITE, (long)&v, 0, 0, 0);
	out("set '");
	out(name);
	out("' = ");
	out(val);
	out(" -> ");
	outn(r);
	out("\n");
	return r < 0;
}

/* ---- PCM playback ---- */

struct interval {
	u32 min, max, flags;
};

struct hw_params {
	u32 flags;
	u32 masks[3][8];
	u32 mres[5][8];
	struct interval intervals[12];
	struct interval ires[9];
	u32 rmask, cmask, info, msbits, rate_num, rate_den;
	u64 fifo_size;
	u8 reserved[64];
};

struct xferi {
	s64 result;
	void *buf;
	u64 frames;
};

#define PCM_HW_PARAMS IOWR('A', 0x11, sizeof(struct hw_params))
#define PCM_PREPARE IO('A', 0x40)
#define PCM_DROP IO('A', 0x43)
#define PCM_DRAIN IO('A', 0x44)
#define PCM_WRITEI IOW('A', 0x50, sizeof(struct xferi))
/* masks: 0 access, 1 format, 2 subformat; intervals from SAMPLE_BITS (8) */
#define I_SAMPLE_BITS 0
#define I_FRAME_BITS 1
#define I_CHANNELS 2
#define I_RATE 3
#define I_PERIOD_TIME 4
#define I_PERIOD_SIZE 5
#define I_PERIOD_BYTES 6
#define I_PERIODS 7
#define I_BUFFER_TIME 8
#define I_BUFFER_SIZE 9
#define I_BUFFER_BYTES 10
#define I_TICK_TIME 11

static void
iv(struct hw_params *p, int i, u32 v)
{
	p->intervals[i].min = v;
	p->intervals[i].max = v;
	p->intervals[i].flags = 4;      /* integer */
}

/* sin(2 pi k / 48) for 1 kHz at 48 kHz, scaled to 32767 */
static const s32 sine48[48] = {
	0, 4277, 8481, 12539, 16384, 19947, 23170, 25996, 28378, 30273, 31651, 32487,
	32767, 32487, 31651, 30273, 28378, 25996, 23170, 19947, 16384, 12539, 8481, 4277,
	0, -4277, -8481, -12539, -16384, -19947, -23170, -25996, -28378, -30273, -31651, -32487,
	-32767, -32487, -31651, -30273, -28378, -25996, -23170, -19947, -16384, -12539, -8481, -4277,
};

static int
cmd_tone(long secs, long amp)
{
	int fd = (int)sys6(SYS_openat, AT_FDCWD, (long)"/dev/snd/pcmC0D0p", O_RDWR, 0, 0, 0);
	if (fd < 0) {
		out("open pcmC0D0p -> ");
		outn(fd);
		out("\n");
		return 1;
	}
	static struct hw_params p;
	memset(&p, 0, sizeof(p));
	for (int m = 0; m < 3; m++) {
		for (int w = 0; w < 8; w++) {
			p.masks[m][w] = 0;
		}
	}
	p.masks[0][0] = 1u << 3;        /* RW_INTERLEAVED */
	p.masks[1][0] = 1u << 2;        /* S16_LE */
	p.masks[2][0] = 1u << 0;        /* STD */
	for (int i = 0; i < 12; i++) {
		p.intervals[i].min = 0;
		p.intervals[i].max = 0xffffffffu;
	}
	iv(&p, I_SAMPLE_BITS, 16);
	iv(&p, I_FRAME_BITS, 32);
	iv(&p, I_CHANNELS, 2);
	iv(&p, I_RATE, 48000);
	iv(&p, I_PERIOD_SIZE, 960);
	iv(&p, I_PERIODS, 4);
	p.rmask = 0xffffffffu;
	long r = sys6(SYS_ioctl, fd, (long)PCM_HW_PARAMS, (long)&p, 0, 0, 0);
	out("hw_params -> ");
	outn(r);
	out("\n");
	if (r != 0) {
		return 1;
	}
	r = sys6(SYS_ioctl, fd, (long)PCM_PREPARE, 0, 0, 0, 0);
	out("prepare -> ");
	outn(r);
	out("\n");
	if (r != 0) {
		return 1;
	}
	static s16 buf[960 * 2];
	long periods = secs * 50, k = 0;
	for (long n = 0; n < periods; n++) {
		for (int f = 0; f < 960; f++) {
			s16 s = (s16)(sine48[k] * amp / 32767);
			buf[2 * f] = s;
			buf[2 * f + 1] = s;
			k = (k + 1) % 48;
		}
		struct xferi x = { 0, buf, 960 };
		r = sys6(SYS_ioctl, fd, (long)PCM_WRITEI, (long)&x, 0, 0, 0);
		if (r != 0) {
			out("writei -> ");
			outn(r);
			out(" at period ");
			outn(n);
			out("\n");
			if (n == 0) {
				return 1;
			}
			sys6(SYS_ioctl, fd, (long)PCM_PREPARE, 0, 0, 0, 0);
		}
	}
	sys6(SYS_ioctl, fd, (long)PCM_DRAIN, 0, 0, 0, 0);
	out("tone done\n");
	sys6(SYS_close, fd, 0, 0, 0, 0, 0);
	return 0;
}

int
umain(int argc, char **argv)
{
	if (argc < 2) {
		out("usage: umi-atone list | set NAME VALUE | tone [SECONDS] [AMPLITUDE]\n");
		return 2;
	}
	if (ctl_open() < 0) {
		out("cannot open /dev/snd/controlC0\n");
		return 1;
	}
	if (seq(argv[1], "list")) {
		return cmd_list();
	}
	if (seq(argv[1], "set") && argc >= 4) {
		return cmd_set(argv[2], argv[3]);
	}
	if (seq(argv[1], "tone")) {
		int ok = 0;
		long secs = argc >= 3 ? num(argv[2], &ok) : 3, amp = argc >= 4 ? num(argv[3], &ok) : 6000;
		return cmd_tone(secs > 0 ? secs : 3, amp > 0 && amp <= 32767 ? amp : 6000);
	}
	out("unknown command\n");
	return 2;
}

__attribute__((naked, noreturn)) void
_start(void)
{
	__asm__ volatile (
		"ldr x0, [sp]\n"
		"add x1, sp, #8\n"
		"bl umain\n"
		"mov x8, #94\n"
		"svc #0\n");
}
