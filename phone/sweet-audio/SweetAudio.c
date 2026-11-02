/*
 * SweetAudio.driver: the umi port's built-in audio devices for iOS's audio server.
 *
 * An AudioServerPlugIn (CoreAudio's documented user-space driver interface, header from the iPhoneOS SDK).
 * iOS's VirtualAudio.plugin builds its routes over physical devices it knows by UID, the ones an iPhone's own audio
 * plug-in publishes, and builds the speaker route only when all of them exist. So this publishes the iPhone set:
 *   "Speaker"   2 ch out (-> /dev/sweet-audio) + 2 ch silent in, a volume control (-48..0 dB)
 *   "Hawking"   1 ch silent in
 *   "Actuator"  1 ch out (haptics: discarded for now)
 *   "Codec"     1 ch silent in, a data-source control with the one source 'imic' ("Bottom")
 * all 16-bit signed PCM at 48 kHz. The Speaker's output goes to the kernel's /dev/sweet-audio (bsd/dev/sweet_adsp.c),
 * which feeds the ADSP's ASM stream -> TERT_MI2S_RX -> the CS35L41 amps. The I/O thread never waits on the kernel:
 * it copies into a lock-free ring that a writer thread drains into the node every 5 ms (the node takes at most 160 ms
 * ahead and never blocks). The device clock is mach_absolute_time at 48000 frames per second.
 *
 * The device set follows what the HackiOS / iOSPlus10 plug-ins describe for the D22 identity; this code is written
 * for this port. A bring-up trace of every property the server asks goes to the kernel log through the node.
 */
#include <CoreAudio/AudioServerPlugIn.h>
#include <CoreFoundation/CoreFoundation.h>
#include <mach/mach_time.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>

#define SA_NODE                 "/dev/sweet-audio"
#define SA_SET_GAIN             _IOW('A', 1, int32_t)
#define SA_LOG_IOCTL            _IOW('A', 3, char[120])
#define SA_RATE                 48000.0
#define SA_PERIOD               16384u          /* zero time stamp period, frames */
#define SA_RING                 16384u          /* frames, ~341 ms */
#define SA_WRITER_NS            5000000ull
#define SA_DB_MIN               (-48.0f)

enum {
	kObjPlugIn = kAudioObjectPlugInObject,
	kObjSpeaker = 2, kObjSpeakerOut = 3, kObjSpeakerIn = 4,
	kObjHawking = 5, kObjHawkingIn = 6,
	kObjActuator = 7, kObjActuatorOut = 8,
	kObjCodec = 9, kObjCodecIn = 10,
	kObjVolume = 11, kObjSource = 12,
};

/* the devices and their streams */
struct sa_dev {
	AudioObjectID id;
	CFStringRef uid;
	AudioObjectID out, in;                  /* stream objects, 0 = none */
	UInt32 out_ch, in_ch;
	AudioObjectID control;                  /* 0 = none */
	bool can_default;
};
static const struct sa_dev sa_devs[] = {
	{ kObjSpeaker, CFSTR("Speaker"), kObjSpeakerOut, kObjSpeakerIn, 2, 2, kObjVolume, true },
	{ kObjHawking, CFSTR("Hawking"), 0, kObjHawkingIn, 0, 1, 0, false },
	{ kObjActuator, CFSTR("Actuator"), kObjActuatorOut, 0, 1, 0, 0, true },
	{ kObjCodec, CFSTR("Codec"), 0, kObjCodecIn, 0, 1, kObjSource, false },
};
#define SA_NDEVS                (sizeof(sa_devs) / sizeof(sa_devs[0]))

static const struct sa_dev *
sa_dev_of(AudioObjectID obj)
{
	for (unsigned i = 0; i < SA_NDEVS; i++) {
		if (sa_devs[i].id == obj) {
			return &sa_devs[i];
		}
	}
	return NULL;
}

/* the device owning a stream or control, and the stream's direction and channels */
static const struct sa_dev *
sa_owner_of(AudioObjectID obj, bool *input, UInt32 *ch)
{
	for (unsigned i = 0; i < SA_NDEVS; i++) {
		const struct sa_dev *d = &sa_devs[i];
		if (obj == d->out && d->out != 0) {
			*input = false;
			*ch = d->out_ch;
			return d;
		}
		if (obj == d->in && d->in != 0) {
			*input = true;
			*ch = d->in_ch;
			return d;
		}
		if (obj == d->control && d->control != 0) {
			*input = obj == kObjSource;
			*ch = 0;
			return d;
		}
	}
	return NULL;
}

static const AudioServerPlugInHostInterface *sa_host;
static UInt32 sa_refs;
static pthread_mutex_t sa_lock = PTHREAD_MUTEX_INITIALIZER;
static UInt32 sa_io_clients[SA_NDEVS];
static Float64 sa_host_ticks_per_frame;
static UInt64 sa_anchor_host[SA_NDEVS], sa_seed[SA_NDEVS], sa_ts_count[SA_NDEVS];
static Float32 sa_volume = 1.0f;                /* scalar 0..1 */

/* single-producer (I/O thread) single-consumer (writer) ring of S16 stereo frames */
static uint32_t sa_ring[SA_RING];
static _Atomic uint64_t sa_head, sa_tail;
static _Atomic bool sa_run;
static pthread_t sa_writer;
static int sa_fd = -1;

static unsigned
sa_dev_index(AudioObjectID dev)
{
	for (unsigned i = 0; i < SA_NDEVS; i++) {
		if (sa_devs[i].id == dev) {
			return i;
		}
	}
	return 0;
}

/* ---- bring-up trace: to the kernel log through the node, kept here until it exists ---- */

static pthread_mutex_t sa_tlock = PTHREAD_MUTEX_INITIALIZER;
static char sa_tbuf[3000][120];
static unsigned sa_tn, sa_tsent;
static int sa_tfd = -1;

static void
sa_trace_flush_locked(void)
{
	if (sa_tfd < 0) {
		return;
	}
	while (sa_tsent < sa_tn) {
		(void)ioctl(sa_tfd, SA_LOG_IOCTL, sa_tbuf[sa_tsent]);
		sa_tsent++;
	}
}

static void
sa_trace(const char *fmt, ...)
{
	pthread_mutex_lock(&sa_tlock);
	if (sa_tn < 3000) {
		va_list ap;
		va_start(ap, fmt);
		vsnprintf(sa_tbuf[sa_tn], sizeof(sa_tbuf[0]), fmt, ap);
		va_end(ap);
		sa_tn++;
		sa_trace_flush_locked();
	}
	pthread_mutex_unlock(&sa_tlock);
}

static const char *
sa_cc(UInt32 v, char out[8])
{
	for (int i = 0; i < 4; i++) {
		char c = (char)(v >> (24 - 8 * i));
		out[i] = c >= 32 && c < 127 ? c : '.';
	}
	out[4] = 0;
	return out;
}

/* each (object, selector, scope) once, with our answer */
static void
sa_trace_prop(const char *what, AudioObjectID obj, pid_t pid, const AudioObjectPropertyAddress *a, OSStatus r)
{
	static struct { AudioObjectID o; UInt32 sel, scope; } seen[800];
	static unsigned nseen;
	pthread_mutex_lock(&sa_tlock);
	for (unsigned i = 0; i < nseen; i++) {
		if (seen[i].o == obj && seen[i].sel == a->mSelector && seen[i].scope == a->mScope) {
			pthread_mutex_unlock(&sa_tlock);
			return;
		}
	}
	if (nseen < 800) {
		seen[nseen].o = obj;
		seen[nseen].sel = a->mSelector;
		seen[nseen].scope = a->mScope;
		nseen++;
	}
	pthread_mutex_unlock(&sa_tlock);
	char c1[8], c2[8], c3[8];
	sa_trace("%s obj %u '%s' scope '%s' elem %u pid %d -> %s", what, obj, sa_cc(a->mSelector, c1),
	    sa_cc(a->mScope, c2), a->mElement, pid, r == 0 ? "ok" : sa_cc((UInt32)r, c3));
}

/* a "loaded" signal for the kernel log: open the node once it exists (it appears when the ADSP stream runs) */
static void *
sa_probe_main(void *arg)
{
	(void)arg;
	for (int i = 0; i < 300; i++) {
		int fd = open(SA_NODE, O_WRONLY | O_NONBLOCK);
		if (fd >= 0) {
			pthread_mutex_lock(&sa_tlock);
			sa_tfd = fd;                    /* kept open for the trace */
			sa_trace_flush_locked();
			pthread_mutex_unlock(&sa_tlock);
			return NULL;
		}
		sleep(2);
	}
	return NULL;
}

/* ---- writer: ring -> /dev/sweet-audio ---- */

static void
sa_apply_gain(void)
{
	if (sa_fd >= 0) {
		/* the control's dB (-48..0) as a linear gain */
		Float32 db = SA_DB_MIN * (1.0f - sa_volume);
		int32_t g = sa_volume <= 0.0f ? 0 : (int32_t)(__builtin_powf(10.0f, db / 20.0f) * 65536.0f);
		(void)ioctl(sa_fd, SA_SET_GAIN, &g);
	}
}

static void *
sa_writer_main(void *arg)
{
	(void)arg;
	uint64_t last_open = 0;
	while (atomic_load(&sa_run)) {
		if (sa_fd < 0) {
			uint64_t now = mach_absolute_time();
			if (last_open == 0 || now - last_open > (uint64_t)(2.0 * sa_host_ticks_per_frame * SA_RATE)) {
				last_open = now;
				sa_fd = open(SA_NODE, O_WRONLY | O_NONBLOCK);
				if (sa_fd >= 0) {
					sa_trace("writer: opened " SA_NODE);
					sa_apply_gain();
				}
			}
		}
		uint64_t head = atomic_load_explicit(&sa_head, memory_order_acquire);
		uint64_t tail = atomic_load_explicit(&sa_tail, memory_order_relaxed);
		while (sa_fd >= 0 && head != tail) {
			uint64_t n = head - tail, at = tail % SA_RING;
			if (n > SA_RING - at) {
				n = SA_RING - at;
			}
			ssize_t w = write(sa_fd, &sa_ring[at], (size_t)n * 4);
			if (w < 0) {
				if (errno != EAGAIN) {
					close(sa_fd);
					sa_fd = -1;
				}
				break;
			}
			tail += (uint64_t)w / 4;
			atomic_store_explicit(&sa_tail, tail, memory_order_release);
			if ((uint64_t)w < n * 4) {
				break;                  /* the kernel is 160 ms ahead: later */
			}
		}
		struct timespec ts = { 0, (long)SA_WRITER_NS };
		nanosleep(&ts, NULL);
	}
	if (sa_fd >= 0) {
		close(sa_fd);
		sa_fd = -1;
	}
	return NULL;
}

/* I/O thread: S16 stereo frames into the ring; drops when full (the writer lost the node) */
static void
sa_push(const uint32_t *in, UInt32 frames)
{
	uint64_t head = atomic_load_explicit(&sa_head, memory_order_relaxed);
	uint64_t tail = atomic_load_explicit(&sa_tail, memory_order_acquire);
	for (UInt32 i = 0; i < frames && head - tail < SA_RING; i++) {
		sa_ring[head % SA_RING] = in[i];
		head++;
	}
	atomic_store_explicit(&sa_head, head, memory_order_release);
}

/* ---- the interface ---- */

static HRESULT sa_QueryInterface(void *drv, REFIID iid, LPVOID *out);
static ULONG sa_AddRef(void *drv);
static ULONG sa_Release(void *drv);
static OSStatus sa_Initialize(AudioServerPlugInDriverRef drv, AudioServerPlugInHostRef host);
static OSStatus sa_CreateDevice(AudioServerPlugInDriverRef drv, CFDictionaryRef desc,
    const AudioServerPlugInClientInfo *client, AudioObjectID *out);
static OSStatus sa_DestroyDevice(AudioServerPlugInDriverRef drv, AudioObjectID dev);
static OSStatus sa_AddDeviceClient(AudioServerPlugInDriverRef drv, AudioObjectID dev,
    const AudioServerPlugInClientInfo *client);
static OSStatus sa_RemoveDeviceClient(AudioServerPlugInDriverRef drv, AudioObjectID dev,
    const AudioServerPlugInClientInfo *client);
static OSStatus sa_PerformConfigurationChange(AudioServerPlugInDriverRef drv, AudioObjectID dev, UInt64 action,
    void *info);
static OSStatus sa_AbortConfigurationChange(AudioServerPlugInDriverRef drv, AudioObjectID dev, UInt64 action,
    void *info);
static Boolean sa_HasProperty(AudioServerPlugInDriverRef drv, AudioObjectID obj, pid_t pid,
    const AudioObjectPropertyAddress *addr);
static OSStatus sa_IsPropertySettable(AudioServerPlugInDriverRef drv, AudioObjectID obj, pid_t pid,
    const AudioObjectPropertyAddress *addr, Boolean *out);
static OSStatus sa_GetPropertyDataSize(AudioServerPlugInDriverRef drv, AudioObjectID obj, pid_t pid,
    const AudioObjectPropertyAddress *addr, UInt32 qsize, const void *qdata, UInt32 *out);
static OSStatus sa_GetPropertyData(AudioServerPlugInDriverRef drv, AudioObjectID obj, pid_t pid,
    const AudioObjectPropertyAddress *addr, UInt32 qsize, const void *qdata, UInt32 insize, UInt32 *outsize,
    void *out);
static OSStatus sa_SetPropertyData(AudioServerPlugInDriverRef drv, AudioObjectID obj, pid_t pid,
    const AudioObjectPropertyAddress *addr, UInt32 qsize, const void *qdata, UInt32 insize, const void *in);
static OSStatus sa_StartIO(AudioServerPlugInDriverRef drv, AudioObjectID dev, UInt32 client);
static OSStatus sa_StopIO(AudioServerPlugInDriverRef drv, AudioObjectID dev, UInt32 client);
static OSStatus sa_GetZeroTimeStamp(AudioServerPlugInDriverRef drv, AudioObjectID dev, UInt32 client,
    Float64 *sample, UInt64 *host, UInt64 *seed);
static OSStatus sa_WillDoIOOperation(AudioServerPlugInDriverRef drv, AudioObjectID dev, UInt32 client, UInt32 op,
    Boolean *will, Boolean *inplace);
static OSStatus sa_BeginIOOperation(AudioServerPlugInDriverRef drv, AudioObjectID dev, UInt32 client, UInt32 op,
    UInt32 frames, const AudioServerPlugInIOCycleInfo *cycle);
static OSStatus sa_DoIOOperation(AudioServerPlugInDriverRef drv, AudioObjectID dev, AudioObjectID stream,
    UInt32 client, UInt32 op, UInt32 frames, const AudioServerPlugInIOCycleInfo *cycle, void *main, void *second);
static OSStatus sa_EndIOOperation(AudioServerPlugInDriverRef drv, AudioObjectID dev, UInt32 client, UInt32 op,
    UInt32 frames, const AudioServerPlugInIOCycleInfo *cycle);

static AudioServerPlugInDriverInterface sa_vtable = {
	NULL,
	sa_QueryInterface, sa_AddRef, sa_Release,
	sa_Initialize, sa_CreateDevice, sa_DestroyDevice, sa_AddDeviceClient, sa_RemoveDeviceClient,
	sa_PerformConfigurationChange, sa_AbortConfigurationChange,
	sa_HasProperty, sa_IsPropertySettable, sa_GetPropertyDataSize, sa_GetPropertyData, sa_SetPropertyData,
	sa_StartIO, sa_StopIO, sa_GetZeroTimeStamp, sa_WillDoIOOperation, sa_BeginIOOperation, sa_DoIOOperation,
	sa_EndIOOperation,
};
static AudioServerPlugInDriverInterface *sa_vtable_ptr = &sa_vtable;
static AudioServerPlugInDriverRef sa_driver = &sa_vtable_ptr;

void *SweetAudio_Create(CFAllocatorRef alloc, CFUUIDRef type);

void *
SweetAudio_Create(CFAllocatorRef alloc, CFUUIDRef type)
{
	(void)alloc;
	if (!CFEqual(type, kAudioServerPlugInTypeUUID)) {
		return NULL;
	}
	sa_trace("factory");
	return sa_driver;
}

static HRESULT
sa_QueryInterface(void *drv, REFIID iid, LPVOID *out)
{
	(void)drv;
	CFUUIDRef req = CFUUIDCreateFromUUIDBytes(NULL, iid);
	HRESULT r = E_NOINTERFACE;
	if (CFEqual(req, IUnknownUUID) || CFEqual(req, kAudioServerPlugInDriverInterfaceUUID)) {
		pthread_mutex_lock(&sa_lock);
		sa_refs++;
		pthread_mutex_unlock(&sa_lock);
		*out = sa_driver;
		r = S_OK;
	}
	CFRelease(req);
	return r;
}

static ULONG
sa_AddRef(void *drv)
{
	(void)drv;
	pthread_mutex_lock(&sa_lock);
	ULONG r = ++sa_refs;
	pthread_mutex_unlock(&sa_lock);
	return r;
}

static ULONG
sa_Release(void *drv)
{
	(void)drv;
	pthread_mutex_lock(&sa_lock);
	ULONG r = sa_refs > 0 ? --sa_refs : 0;
	pthread_mutex_unlock(&sa_lock);
	return r;
}

static OSStatus
sa_Initialize(AudioServerPlugInDriverRef drv, AudioServerPlugInHostRef host)
{
	(void)drv;
	pthread_t probe;
	if (pthread_create(&probe, NULL, sa_probe_main, NULL) == 0) {
		pthread_detach(probe);
	}
	sa_host = host;
	mach_timebase_info_data_t tb;
	mach_timebase_info(&tb);
	sa_host_ticks_per_frame = (1e9 / SA_RATE) * (Float64)tb.denom / (Float64)tb.numer;
	for (unsigned i = 0; i < SA_NDEVS; i++) {
		sa_seed[i] = 1;
	}
	sa_trace("initialized: Speaker Hawking Actuator Codec; Speaker -> " SA_NODE);
	return kAudioHardwareNoError;
}

static OSStatus
sa_CreateDevice(AudioServerPlugInDriverRef drv, CFDictionaryRef desc, const AudioServerPlugInClientInfo *client,
    AudioObjectID *out)
{
	(void)drv; (void)desc; (void)client; (void)out;
	return kAudioHardwareUnsupportedOperationError;
}

static OSStatus
sa_DestroyDevice(AudioServerPlugInDriverRef drv, AudioObjectID dev)
{
	(void)drv; (void)dev;
	return kAudioHardwareUnsupportedOperationError;
}

static OSStatus
sa_AddDeviceClient(AudioServerPlugInDriverRef drv, AudioObjectID dev, const AudioServerPlugInClientInfo *client)
{
	(void)drv;
	char bid[96] = "?";
	if (client != NULL && client->mBundleID != NULL) {
		CFStringGetCString(client->mBundleID, bid, sizeof(bid), kCFStringEncodingUTF8);
	}
	sa_trace("client add: dev %u id %u pid %d %s", dev, client ? client->mClientID : 0,
	    client ? client->mProcessID : -1, bid);
	return sa_dev_of(dev) != NULL ? kAudioHardwareNoError : kAudioHardwareBadObjectError;
}

static OSStatus
sa_RemoveDeviceClient(AudioServerPlugInDriverRef drv, AudioObjectID dev, const AudioServerPlugInClientInfo *client)
{
	(void)drv; (void)client;
	return sa_dev_of(dev) != NULL ? kAudioHardwareNoError : kAudioHardwareBadObjectError;
}

static OSStatus
sa_PerformConfigurationChange(AudioServerPlugInDriverRef drv, AudioObjectID dev, UInt64 action, void *info)
{
	(void)drv; (void)dev; (void)action; (void)info;
	return kAudioHardwareNoError;
}

static OSStatus
sa_AbortConfigurationChange(AudioServerPlugInDriverRef drv, AudioObjectID dev, UInt64 action, void *info)
{
	(void)drv; (void)dev; (void)action; (void)info;
	return kAudioHardwareNoError;
}

/* ---- properties ---- */

static AudioStreamBasicDescription
sa_format(UInt32 ch)
{
	AudioStreamBasicDescription f = { 0 };
	f.mSampleRate = SA_RATE;
	f.mFormatID = kAudioFormatLinearPCM;
	f.mFormatFlags = kAudioFormatFlagIsSignedInteger | kAudioFormatFlagsNativeEndian | kAudioFormatFlagIsPacked;
	f.mBytesPerPacket = 2 * ch;
	f.mFramesPerPacket = 1;
	f.mBytesPerFrame = 2 * ch;
	f.mChannelsPerFrame = ch;
	f.mBitsPerChannel = 16;
	return f;
}

static OSStatus sa_property(AudioObjectID obj, const AudioObjectPropertyAddress *a, UInt32 insize, UInt32 *outsize,
    void *data);

static Boolean
sa_HasProperty(AudioServerPlugInDriverRef drv, AudioObjectID obj, pid_t pid, const AudioObjectPropertyAddress *a)
{
	(void)drv;
	UInt32 size;
	OSStatus r = sa_property(obj, a, 0, &size, NULL);
	sa_trace_prop("has", obj, pid, a, r);
	return r == kAudioHardwareNoError;
}

static OSStatus
sa_IsPropertySettable(AudioServerPlugInDriverRef drv, AudioObjectID obj, pid_t pid,
    const AudioObjectPropertyAddress *a, Boolean *out)
{
	(void)drv; (void)pid;
	bool input;
	UInt32 ch;
	bool stream = sa_owner_of(obj, &input, &ch) != NULL && obj != kObjVolume && obj != kObjSource;
	*out = (sa_dev_of(obj) != NULL && a->mSelector == kAudioDevicePropertyNominalSampleRate) ||
	    (stream && (a->mSelector == kAudioStreamPropertyVirtualFormat ||
	    a->mSelector == kAudioStreamPropertyPhysicalFormat)) ||
	    (obj == kObjVolume && (a->mSelector == kAudioLevelControlPropertyScalarValue ||
	    a->mSelector == kAudioLevelControlPropertyDecibelValue)) ||
	    (obj == kObjSource && a->mSelector == kAudioSelectorControlPropertyCurrentItem);
	return kAudioHardwareNoError;
}

#define OUT(type, value) do { \
		*outsize = sizeof(type); \
		if (data != NULL) { \
			if (insize < sizeof(type)) { \
				return kAudioHardwareBadPropertySizeError; \
			} \
			*(type *)data = (value); \
		} \
		return kAudioHardwareNoError; \
} while (0)

static OSStatus
sa_out_ids(const AudioObjectID *list, UInt32 n, UInt32 insize, UInt32 *outsize, void *data)
{
	if (data != NULL) {
		UInt32 room = insize / (UInt32)sizeof(AudioObjectID);
		n = n < room ? n : room;
		memcpy(data, list, n * sizeof(AudioObjectID));
	}
	*outsize = n * (UInt32)sizeof(AudioObjectID);
	return kAudioHardwareNoError;
}

static OSStatus
sa_device_property(const struct sa_dev *d, const AudioObjectPropertyAddress *a, UInt32 insize, UInt32 *outsize,
    void *data)
{
	bool out_scope = a->mScope == kAudioObjectPropertyScopeOutput;
	bool in_scope = a->mScope == kAudioObjectPropertyScopeInput;
	AudioObjectID ids[3];
	UInt32 n = 0;
	switch (a->mSelector) {
	case kAudioObjectPropertyBaseClass: OUT(AudioClassID, kAudioObjectClassID);
	case kAudioObjectPropertyClass: OUT(AudioClassID, kAudioDeviceClassID);
	case kAudioObjectPropertyOwner: OUT(AudioObjectID, kObjPlugIn);
	case kAudioObjectPropertyName: OUT(CFStringRef, d->uid);
	case kAudioObjectPropertyModelName: OUT(CFStringRef, d->uid);
	case kAudioObjectPropertyManufacturer: OUT(CFStringRef, CFSTR("umi port"));
	case kAudioObjectPropertyOwnedObjects:
	case kAudioDevicePropertyStreams:
		if (d->in != 0 && !out_scope) {
			ids[n++] = d->in;
		}
		if (d->out != 0 && !in_scope) {
			ids[n++] = d->out;
		}
		if (a->mSelector == kAudioObjectPropertyOwnedObjects && d->control != 0 &&
		    (a->mScope == kAudioObjectPropertyScopeGlobal || (out_scope && d->control == kObjVolume) ||
		    (in_scope && d->control == kObjSource))) {
			ids[n++] = d->control;
		}
		return sa_out_ids(ids, n, insize, outsize, data);
	case kAudioObjectPropertyControlList:
		if (d->control != 0) {
			ids[n++] = d->control;
		}
		return sa_out_ids(ids, n, insize, outsize, data);
	case kAudioDevicePropertyDeviceUID: OUT(CFStringRef, d->uid);
	case kAudioDevicePropertyModelUID: OUT(CFStringRef, d->uid);
	case kAudioDevicePropertyTransportType: OUT(UInt32, kAudioDeviceTransportTypeBuiltIn);
	case kAudioDevicePropertyRelatedDevices: ids[0] = d->id; return sa_out_ids(ids, 1, insize, outsize, data);
	case kAudioDevicePropertyClockDomain: OUT(UInt32, 0);
	case kAudioDevicePropertyDeviceIsAlive: OUT(UInt32, 1);
	case kAudioDevicePropertyDeviceIsRunning: OUT(UInt32, sa_io_clients[sa_dev_index(d->id)] > 0);
	case kAudioDevicePropertyDeviceCanBeDefaultDevice: OUT(UInt32, d->can_default);
	case kAudioDevicePropertyDeviceCanBeDefaultSystemDevice: OUT(UInt32, d->can_default);
	case kAudioDevicePropertyLatency: OUT(UInt32, 0);
	case kAudioDevicePropertySafetyOffset: OUT(UInt32, 0);
	case kAudioDevicePropertyNominalSampleRate: OUT(Float64, SA_RATE);
	case kAudioDevicePropertyAvailableNominalSampleRates: {
		AudioValueRange r = { SA_RATE, SA_RATE };
		OUT(AudioValueRange, r);
	}
	case kAudioDevicePropertyIsHidden: OUT(UInt32, 0);
	case kAudioDevicePropertyZeroTimeStampPeriod: OUT(UInt32, SA_PERIOD);
	case kAudioDevicePropertyPreferredChannelsForStereo: {
		*outsize = 2 * sizeof(UInt32);
		if (data != NULL) {
			if (insize < 2 * sizeof(UInt32)) {
				return kAudioHardwareBadPropertySizeError;
			}
			((UInt32 *)data)[0] = 1;
			((UInt32 *)data)[1] = (d->out_ch >= 2 || d->in_ch >= 2) ? 2 : 1;
		}
		return kAudioHardwareNoError;
	}
	default:
		return kAudioHardwareUnknownPropertyError;
	}
}

static OSStatus
sa_property(AudioObjectID obj, const AudioObjectPropertyAddress *a, UInt32 insize, UInt32 *outsize, void *data)
{
	if (obj == kObjPlugIn) {
		AudioObjectID ids[SA_NDEVS];
		switch (a->mSelector) {
		case kAudioObjectPropertyBaseClass: OUT(AudioClassID, kAudioObjectClassID);
		case kAudioObjectPropertyClass: OUT(AudioClassID, kAudioPlugInClassID);
		case kAudioObjectPropertyOwner: OUT(AudioObjectID, kAudioObjectUnknown);
		case kAudioObjectPropertyManufacturer: OUT(CFStringRef, CFSTR("umi port"));
		case kAudioObjectPropertyOwnedObjects:
		case kAudioPlugInPropertyDeviceList:
			for (unsigned i = 0; i < SA_NDEVS; i++) {
				ids[i] = sa_devs[i].id;
			}
			return sa_out_ids(ids, SA_NDEVS, insize, outsize, data);
		case kAudioPlugInPropertyBoxList:
			*outsize = 0;
			return kAudioHardwareNoError;
		case kAudioPlugInPropertyTranslateUIDToDevice: OUT(AudioObjectID, kAudioObjectUnknown);
		case kAudioPlugInPropertyTranslateUIDToBox: OUT(AudioObjectID, kAudioObjectUnknown);
		case kAudioPlugInPropertyResourceBundle: OUT(CFStringRef, CFSTR(""));
		default: return kAudioHardwareUnknownPropertyError;
		}
	}
	const struct sa_dev *d = sa_dev_of(obj);
	if (d != NULL) {
		return sa_device_property(d, a, insize, outsize, data);
	}
	bool input;
	UInt32 ch;
	d = sa_owner_of(obj, &input, &ch);
	if (d == NULL) {
		return kAudioHardwareBadObjectError;
	}
	if (obj == kObjVolume) {
		switch (a->mSelector) {
		case kAudioObjectPropertyBaseClass: OUT(AudioClassID, kAudioLevelControlClassID);
		case kAudioObjectPropertyClass: OUT(AudioClassID, kAudioVolumeControlClassID);
		case kAudioObjectPropertyOwner: OUT(AudioObjectID, kObjSpeaker);
		case kAudioObjectPropertyOwnedObjects: *outsize = 0; return kAudioHardwareNoError;
		case kAudioControlPropertyScope: OUT(AudioObjectPropertyScope, kAudioObjectPropertyScopeOutput);
		case kAudioControlPropertyElement: OUT(AudioObjectPropertyElement, kAudioObjectPropertyElementMain);
		case kAudioLevelControlPropertyScalarValue: OUT(Float32, sa_volume);
		case kAudioLevelControlPropertyDecibelValue: OUT(Float32, SA_DB_MIN * (1.0f - sa_volume));
		case kAudioLevelControlPropertyDecibelRange: {
			AudioValueRange r = { SA_DB_MIN, 0.0 };
			OUT(AudioValueRange, r);
		}
		default: return kAudioHardwareUnknownPropertyError;
		}
	}
	if (obj == kObjSource) {
		switch (a->mSelector) {
		case kAudioObjectPropertyBaseClass: OUT(AudioClassID, kAudioSelectorControlClassID);
		case kAudioObjectPropertyClass: OUT(AudioClassID, kAudioDataSourceControlClassID);
		case kAudioObjectPropertyOwner: OUT(AudioObjectID, kObjCodec);
		case kAudioObjectPropertyOwnedObjects: *outsize = 0; return kAudioHardwareNoError;
		case kAudioControlPropertyScope: OUT(AudioObjectPropertyScope, kAudioObjectPropertyScopeInput);
		case kAudioControlPropertyElement: OUT(AudioObjectPropertyElement, kAudioObjectPropertyElementMain);
		case kAudioSelectorControlPropertyCurrentItem:
		case kAudioSelectorControlPropertyAvailableItems:
			OUT(UInt32, 'imic');
		case kAudioSelectorControlPropertyItemName: OUT(CFStringRef, CFSTR("Bottom"));
		default: return kAudioHardwareUnknownPropertyError;
		}
	}
	switch (a->mSelector) {                 /* a stream */
	case kAudioObjectPropertyBaseClass: OUT(AudioClassID, kAudioObjectClassID);
	case kAudioObjectPropertyClass: OUT(AudioClassID, kAudioStreamClassID);
	case kAudioObjectPropertyOwner: OUT(AudioObjectID, d->id);
	case kAudioObjectPropertyOwnedObjects: *outsize = 0; return kAudioHardwareNoError;
	case kAudioStreamPropertyIsActive: OUT(UInt32, 1);
	case kAudioStreamPropertyDirection: OUT(UInt32, input ? 1 : 0);
	case kAudioStreamPropertyTerminalType:
		OUT(UInt32, input ? kAudioStreamTerminalTypeMicrophone : kAudioStreamTerminalTypeSpeaker);
	case kAudioStreamPropertyStartingChannel: OUT(UInt32, 1);
	case kAudioStreamPropertyLatency: OUT(UInt32, 0);
	case kAudioStreamPropertyVirtualFormat:
	case kAudioStreamPropertyPhysicalFormat:
		OUT(AudioStreamBasicDescription, sa_format(ch));
	case kAudioStreamPropertyAvailableVirtualFormats:
	case kAudioStreamPropertyAvailablePhysicalFormats: {
		AudioStreamRangedDescription r = { sa_format(ch), { SA_RATE, SA_RATE } };
		OUT(AudioStreamRangedDescription, r);
	}
	default:
		return kAudioHardwareUnknownPropertyError;
	}
}
#undef OUT

static OSStatus
sa_GetPropertyDataSize(AudioServerPlugInDriverRef drv, AudioObjectID obj, pid_t pid,
    const AudioObjectPropertyAddress *a, UInt32 qsize, const void *qdata, UInt32 *out)
{
	(void)drv; (void)qsize; (void)qdata;
	OSStatus r = sa_property(obj, a, 0, out, NULL);
	sa_trace_prop("size", obj, pid, a, r);
	return r;
}

static bool
sa_is_cfstring_selector(AudioObjectPropertySelector s)
{
	return s == kAudioObjectPropertyName || s == kAudioObjectPropertyModelName ||
	       s == kAudioObjectPropertyManufacturer || s == kAudioDevicePropertyDeviceUID ||
	       s == kAudioDevicePropertyModelUID || s == kAudioPlugInPropertyResourceBundle ||
	       s == kAudioSelectorControlPropertyItemName;
}

static OSStatus
sa_GetPropertyData(AudioServerPlugInDriverRef drv, AudioObjectID obj, pid_t pid,
    const AudioObjectPropertyAddress *a, UInt32 qsize, const void *qdata, UInt32 insize, UInt32 *outsize, void *out)
{
	(void)drv;
	if (obj == kObjPlugIn && a->mSelector == kAudioPlugInPropertyTranslateUIDToDevice) {
		if (insize < sizeof(AudioObjectID) || qsize < sizeof(CFStringRef) || qdata == NULL) {
			return kAudioHardwareBadPropertySizeError;
		}
		CFStringRef uid = *(const CFStringRef *)qdata;
		AudioObjectID found = kAudioObjectUnknown;
		for (unsigned i = 0; i < SA_NDEVS; i++) {
			if (CFEqual(uid, sa_devs[i].uid)) {
				found = sa_devs[i].id;
			}
		}
		*(AudioObjectID *)out = found;
		*outsize = sizeof(AudioObjectID);
		sa_trace_prop("get", obj, pid, a, 0);
		return kAudioHardwareNoError;
	}
	OSStatus r = sa_property(obj, a, insize, outsize, out);
	sa_trace_prop("get", obj, pid, a, r);
	/* CFStrings are returned retained: the caller releases them */
	if (r == kAudioHardwareNoError && sa_is_cfstring_selector(a->mSelector) && *outsize == sizeof(CFStringRef)) {
		CFRetain(*(CFStringRef *)out);
	}
	return r;
}

static OSStatus
sa_SetPropertyData(AudioServerPlugInDriverRef drv, AudioObjectID obj, pid_t pid,
    const AudioObjectPropertyAddress *a, UInt32 qsize, const void *qdata, UInt32 insize, const void *in)
{
	(void)drv; (void)qsize; (void)qdata;
	sa_trace_prop("set", obj, pid, a, 0);
	if (obj == kObjVolume && insize >= sizeof(Float32)) {
		Float32 v = *(const Float32 *)in;
		if (a->mSelector == kAudioLevelControlPropertyDecibelValue) {
			v = 1.0f - v / SA_DB_MIN;
		} else if (a->mSelector != kAudioLevelControlPropertyScalarValue) {
			return kAudioHardwareUnknownPropertyError;
		}
		sa_volume = v < 0.0f ? 0.0f : v > 1.0f ? 1.0f : v;
		sa_apply_gain();
		sa_trace("volume %d%%", (int)(sa_volume * 100.0f));
		if (sa_host != NULL) {
			AudioObjectPropertyAddress ch[2] = {
				{ kAudioLevelControlPropertyScalarValue, kAudioObjectPropertyScopeGlobal,
				  kAudioObjectPropertyElementMain },
				{ kAudioLevelControlPropertyDecibelValue, kAudioObjectPropertyScopeGlobal,
				  kAudioObjectPropertyElementMain },
			};
			sa_host->PropertiesChanged(sa_host, kObjVolume, 2, ch);
		}
		return kAudioHardwareNoError;
	}
	if (obj == kObjSource && a->mSelector == kAudioSelectorControlPropertyCurrentItem) {
		return insize >= sizeof(UInt32) && *(const UInt32 *)in == 'imic' ? kAudioHardwareNoError :
		       kAudioHardwareIllegalOperationError;
	}
	bool input;
	UInt32 ch;
	if (sa_dev_of(obj) != NULL && a->mSelector == kAudioDevicePropertyNominalSampleRate) {
		return kAudioHardwareNoError;          /* one rate only */
	}
	if (sa_owner_of(obj, &input, &ch) != NULL && (a->mSelector == kAudioStreamPropertyVirtualFormat ||
	    a->mSelector == kAudioStreamPropertyPhysicalFormat)) {
		return kAudioHardwareNoError;          /* one format only */
	}
	return kAudioHardwareUnknownPropertyError;
}

/* ---- I/O ---- */

static OSStatus
sa_StartIO(AudioServerPlugInDriverRef drv, AudioObjectID dev, UInt32 client)
{
	(void)drv;
	if (sa_dev_of(dev) == NULL) {
		return kAudioHardwareBadObjectError;
	}
	unsigned i = sa_dev_index(dev);
	sa_trace("StartIO dev %u client %u", dev, client);
	pthread_mutex_lock(&sa_lock);
	if (sa_io_clients[i]++ == 0) {
		sa_anchor_host[i] = mach_absolute_time();
		sa_ts_count[i] = 0;
		sa_seed[i]++;
		if (dev == kObjSpeaker) {
			atomic_store(&sa_run, true);
			if (pthread_create(&sa_writer, NULL, sa_writer_main, NULL) != 0) {
				atomic_store(&sa_run, false);
			}
		}
	}
	pthread_mutex_unlock(&sa_lock);
	return kAudioHardwareNoError;
}

static OSStatus
sa_StopIO(AudioServerPlugInDriverRef drv, AudioObjectID dev, UInt32 client)
{
	(void)drv;
	if (sa_dev_of(dev) == NULL) {
		return kAudioHardwareBadObjectError;
	}
	unsigned i = sa_dev_index(dev);
	sa_trace("StopIO dev %u client %u", dev, client);
	pthread_mutex_lock(&sa_lock);
	if (sa_io_clients[i] > 0 && --sa_io_clients[i] == 0 && dev == kObjSpeaker && atomic_load(&sa_run)) {
		atomic_store(&sa_run, false);
		pthread_mutex_unlock(&sa_lock);
		pthread_join(sa_writer, NULL);
		return kAudioHardwareNoError;
	}
	pthread_mutex_unlock(&sa_lock);
	return kAudioHardwareNoError;
}

static OSStatus
sa_GetZeroTimeStamp(AudioServerPlugInDriverRef drv, AudioObjectID dev, UInt32 client, Float64 *sample, UInt64 *host,
    UInt64 *seed)
{
	(void)drv; (void)client;
	unsigned i = sa_dev_index(dev);
	UInt64 now = mach_absolute_time();
	Float64 ticks_per_period = sa_host_ticks_per_frame * SA_PERIOD;
	UInt64 next = sa_anchor_host[i] + (UInt64)((Float64)(sa_ts_count[i] + 1) * ticks_per_period);
	if (now >= next) {
		sa_ts_count[i]++;
	}
	*sample = (Float64)(sa_ts_count[i] * SA_PERIOD);
	*host = sa_anchor_host[i] + (UInt64)((Float64)sa_ts_count[i] * ticks_per_period);
	*seed = sa_seed[i];
	return kAudioHardwareNoError;
}

static OSStatus
sa_WillDoIOOperation(AudioServerPlugInDriverRef drv, AudioObjectID dev, UInt32 client, UInt32 op, Boolean *will,
    Boolean *inplace)
{
	(void)drv; (void)client;
	const struct sa_dev *d = sa_dev_of(dev);
	*will = d != NULL && ((op == kAudioServerPlugInIOOperationWriteMix && d->out != 0) ||
	    (op == kAudioServerPlugInIOOperationReadInput && d->in != 0));
	*inplace = true;
	return kAudioHardwareNoError;
}

static OSStatus
sa_BeginIOOperation(AudioServerPlugInDriverRef drv, AudioObjectID dev, UInt32 client, UInt32 op, UInt32 frames,
    const AudioServerPlugInIOCycleInfo *cycle)
{
	(void)drv; (void)dev; (void)client; (void)op; (void)frames; (void)cycle;
	return kAudioHardwareNoError;
}

static OSStatus
sa_DoIOOperation(AudioServerPlugInDriverRef drv, AudioObjectID dev, AudioObjectID stream, UInt32 client, UInt32 op,
    UInt32 frames, const AudioServerPlugInIOCycleInfo *cycle, void *main, void *second)
{
	(void)drv; (void)dev; (void)client; (void)cycle; (void)second;
	bool input;
	UInt32 ch;
	if (main == NULL || sa_owner_of(stream, &input, &ch) == NULL) {
		return kAudioHardwareNoError;
	}
	if (op == kAudioServerPlugInIOOperationWriteMix && stream == kObjSpeakerOut) {
		sa_push((const uint32_t *)main, frames);
	} else if (op == kAudioServerPlugInIOOperationReadInput && input) {
		memset(main, 0, (size_t)frames * 2 * ch);       /* no microphones yet */
	}
	return kAudioHardwareNoError;
}

static OSStatus
sa_EndIOOperation(AudioServerPlugInDriverRef drv, AudioObjectID dev, UInt32 client, UInt32 op, UInt32 frames,
    const AudioServerPlugInIOCycleInfo *cycle)
{
	(void)drv; (void)dev; (void)client; (void)op; (void)frames; (void)cycle;
	return kAudioHardwareNoError;
}
