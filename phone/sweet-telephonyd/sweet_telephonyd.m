/*
 * sweet-telephonyd: a stand-in for CommCenter on umi (the X55 modem is driven by the kernel, sweet_mdm.c; Apple's
 * CommCenter needs Apple's baseband drivers and firmware and cannot drive it). Stage 1: learn what iOS asks.
 *
 * It takes CommCenter's launchd job (same MachServices) and serves:
 *   - com.apple.commcenter.coretelephony.xpc with an NSXPC listener exporting CoreTelephony's CTXPCServiceInterface:
 *     every request is logged (client, selector) and its reply block, if any, is called with neutral values
 *     (nil / 0 / NO), its signature taken from the block itself;
 *   - every other CommCenter service as plain XPC (CoreTelephony's older CTServerConnection API sends dictionaries
 *     with "kRequest" and placeholders of the answers wanted): logged and answered with the request's own keys,
 *     which echoes the placeholders (a reply, so the clients do not reconnect in a storm).
 * The modem's state comes from the kernel's sysctl kern.sweet_cell (used in the answers from stage 2 on).
 * Log: /private/var/sweet/telephonyd.log, rewritten whole every 5 s from a ring in memory (appending grows files a
 * block at a time on this file system), plus counts per client and request.
 *
 * Approach (a stand-in answering CTXPCServiceInterface and the plain-XPC API, the echo of placeholders) follows the
 * facts the OnePlus 8 Pro port (dekefake/hackios-op8pro, docs/research/modem-sdx55.md) found; the code is our own.
 */
#import <Foundation/Foundation.h>
#import <objc/runtime.h>
#import <dlfcn.h>
#import <sys/sysctl.h>
#import <xpc/xpc.h>
#import <objc/message.h>

/* present at run time, marked unavailable on iOS in the SDK: reached through dlsym / the runtime */
extern const char *_Block_signature(void *block);
static xpc_connection_t (*p_create_mach_service)(const char *, dispatch_queue_t, uint64_t);
static pid_t (*p_get_pid)(xpc_connection_t);
extern const char *_protocol_getMethodTypeEncoding(Protocol *p, SEL sel, BOOL isRequired, BOOL isInstance);

/* ---- log: a ring of lines in memory, the file rewritten whole ---- */

#define LOG_LINES 4000
static NSMutableArray<NSString *> *log_ring;
static NSMutableDictionary<NSString *, NSNumber *> *counts;
static dispatch_queue_t log_q;
static uint64_t t0;

static void
say(NSString *fmt, ...)
{
	va_list ap;
	va_start(ap, fmt);
	NSString *s = [[NSString alloc] initWithFormat:fmt arguments:ap];
	va_end(ap);
	double t = (double)(clock_gettime_nsec_np(CLOCK_MONOTONIC) - t0) / 1e9;
	NSString *line = [NSString stringWithFormat:@"[%8.3f] %@", t, s];
	dispatch_async(log_q, ^{
		[log_ring addObject:line];
		if (log_ring.count > LOG_LINES) {
			[log_ring removeObjectsInRange:NSMakeRange(0, log_ring.count - LOG_LINES)];
		}
	});
}

static void
count(NSString *key)
{
	dispatch_async(log_q, ^{
		counts[key] = @(counts[key].unsignedLongLongValue + 1);
	});
}

static void
log_flush(void)
{
	dispatch_async(log_q, ^{
		NSMutableString *all = [NSMutableString string];
		for (NSString *l in log_ring) {
			[all appendString:l];
			[all appendString:@"\n"];
		}
		[all appendString:@"---- counts (client / request) ----\n"];
		NSArray *keys = [counts keysSortedByValueUsingComparator:^NSComparisonResult(NSNumber *a, NSNumber *b) {
			return [b compare:a];
		}];
		for (NSString *k in keys) {
			[all appendFormat:@"%8llu %@\n", counts[k].unsignedLongLongValue, k];
		}
		[all writeToFile:@"/private/var/sweet/telephonyd.log" atomically:NO encoding:NSUTF8StringEncoding error:nil];
	});
}

static NSString *
cell_state(void)
{
	char buf[160] = { 0 };
	size_t n = sizeof(buf) - 1;
	if (sysctlbyname("kern.sweet_cell", buf, &n, NULL, 0) != 0) {
		return @"(no kern.sweet_cell)";
	}
	return [NSString stringWithUTF8String:buf];
}

static NSString *
proc_name(pid_t pid)
{
	char name[64] = { 0 };
	struct kinfo_proc kp;
	size_t n = sizeof(kp);
	int mib[4] = { CTL_KERN, KERN_PROC, KERN_PROC_PID, pid };
	if (sysctl(mib, 4, &kp, &n, NULL, 0) == 0 && n > 0) {
		strlcpy(name, kp.kp_proc.p_comm, sizeof(name));
	}
	return [NSString stringWithFormat:@"%s[%d]", name[0] ? name : "?", pid];
}

/* ---- NSXPC: CTXPCServiceInterface ---- */

static Protocol *ct_proto;

static id slot1_context(void);
static NSString *sim_status(void);
static NSString *operator_name(void);
static id display_status(void);
static id signal_info(void);
static id data_status(void);

@interface SweetCT : NSObject
@property (nonatomic, copy) NSString *client;
@property (nonatomic, weak) NSXPCConnection *conn;
@property (nonatomic, strong) NSSet<NSString *> *wanted;      /* the notifications it registered for */
@property (nonatomic, copy) NSString *last;                   /* the state last told */
@end

static NSMutableArray<SweetCT *> *registered_clients;
static Protocol *ct_delegate_proto;

/* Tell one client what it registered for (the modem's state now); only when it changed for that client. */
static void
notify_client(SweetCT *c, BOOL force)
{
	NSXPCConnection *conn = c.conn;
	if (conn == nil || c.wanted == nil) {
		return;
	}
	NSString *state = cell_state();
	if (!force && [state isEqualToString:c.last]) {
		return;
	}
	c.last = state;
	id proxy = [conn remoteObjectProxyWithErrorHandler:^(NSError *e) {
		(void)e;
	}];
	id ctx = slot1_context();
	NSSet *w = c.wanted;
	unsigned sent = 0;
#define WANT(s) ([w containsObject:@s])
	if (WANT("activeSubscriptionsDidChange")) {
		((void (*)(id, SEL))objc_msgSend)(proxy, NSSelectorFromString(@"activeSubscriptionsDidChange"));
		sent++;
	}
	if (WANT("subscriptionInfoDidChange")) {
		((void (*)(id, SEL))objc_msgSend)(proxy, NSSelectorFromString(@"subscriptionInfoDidChange"));
		sent++;
	}
	if (ctx != nil && WANT("simStatusDidChange:status:")) {
		((void (*)(id, SEL, id, id))objc_msgSend)(proxy, NSSelectorFromString(@"simStatusDidChange:status:"), ctx, sim_status());
		sent++;
	}
	if (ctx != nil && WANT("operatorNameChanged:name:")) {
		((void (*)(id, SEL, id, id))objc_msgSend)(proxy, NSSelectorFromString(@"operatorNameChanged:name:"), ctx, operator_name());
		sent++;
	}
	if (ctx != nil && WANT("displayStatusChanged:status:")) {
		((void (*)(id, SEL, id, id))objc_msgSend)(proxy, NSSelectorFromString(@"displayStatusChanged:status:"), ctx, display_status());
		sent++;
	}
	if (ctx != nil && WANT("signalStrengthChanged:info:")) {
		((void (*)(id, SEL, id, id))objc_msgSend)(proxy, NSSelectorFromString(@"signalStrengthChanged:info:"), ctx, signal_info());
		sent++;
	}
	if (ctx != nil && WANT("dataStatus:dataStatusInfo:")) {
		((void (*)(id, SEL, id, id))objc_msgSend)(proxy, NSSelectorFromString(@"dataStatus:dataStatusInfo:"), ctx, data_status());
		sent++;
	}
#undef WANT
	say(@"notify %@: %u notification(s); %@", c.client, sent, state);
}

@implementation SweetCT

- (BOOL)respondsToSelector:(SEL)sel
{
	if (ct_proto != nil && protocol_getMethodDescription(ct_proto, sel, YES, YES).name != NULL) {
		return YES;
	}
	if (ct_proto != nil && protocol_getMethodDescription(ct_proto, sel, NO, YES).name != NULL) {
		return YES;
	}
	return [super respondsToSelector:sel];
}

- (NSMethodSignature *)methodSignatureForSelector:(SEL)sel
{
	const char *types = NULL;
	for (int req = 1; req >= 0 && types == NULL; --req) {
		types = _protocol_getMethodTypeEncoding(ct_proto, sel, (BOOL)req, YES);
		if (types == NULL) {
			struct objc_method_description d = protocol_getMethodDescription(ct_proto, sel, (BOOL)req, YES);
			types = d.types;
		}
	}
	if (types != NULL) {
		return [NSMethodSignature signatureWithObjCTypes:types];
	}
	return [super methodSignatureForSelector:sel];
}

/* ---- stage 2: real answers (one SIM, slot 1, from kern.sweet_cell) ---- */

static BOOL
cell_has(NSString *kv)
{
	return [cell_state() rangeOfString:kv].location != NSNotFound;
}

/* The subscription context of slot 1 (OnePlus 8 Pro port's facts: +contextWithSlot:, uuid ...0001 for slot 1). */
static id
slot1_context(void)
{
	Class cls = NSClassFromString(@"CTXPCServiceSubscriptionContext");
	id ctx = ((id (*)(id, SEL, long long))objc_msgSend)(cls, NSSelectorFromString(@"contextWithSlot:"), 1);
	if (ctx == nil) {
		return nil;
	}
	if ([ctx valueForKey:@"uuid"] == nil) {
		Ivar iv = class_getInstanceVariable(cls, "_uuid");
		if (iv != NULL) {
			object_setIvar(ctx, iv, [[NSUUID alloc] initWithUUIDString:@"00000000-0000-0000-0000-000000000001"]);
		}
	}
	BOOL sim = cell_has(@"sim=ready");
	@try {
		[ctx setValue:@"sweet-slot-1" forKey:@"labelID"];
		[ctx setValue:@"Primary" forKey:@"label"];
		[ctx setValue:@1 forKey:@"userDataPreferred"];
		[ctx setValue:@1 forKey:@"userDefaultVoice"];
		[ctx setValue:@(sim) forKey:@"isSimPresent"];
		[ctx setValue:@(sim) forKey:@"isSimGood"];
	} @catch (NSException *e) {
		say(@"  context: %@", e.reason);
	}
	return ctx;
}

static long
cell_num(NSString *key)
{
	for (NSString *kv in [cell_state() componentsSeparatedByString:@" "]) {
		NSArray *p = [kv componentsSeparatedByString:@"="];
		if (p.count == 2 && [p[0] isEqualToString:key]) {
			return [p[1] integerValue];
		}
	}
	return 0;
}

static NSString *
ct_const(const char *name, NSString *fallback)
{
	CFStringRef *v = dlsym(RTLD_DEFAULT, name);
	return v != NULL && *v != NULL ? (__bridge NSString *)*v : fallback;
}

static NSString *
operator_name(void)
{
	long mcc = cell_num(@"mcc"), mnc = cell_num(@"mnc");
	if (mcc == 228) {
		if (mnc == 1) return @"Swisscom";
		if (mnc == 2) return @"Sunrise";
		if (mnc == 3) return @"Salt";
	}
	return mcc ? [NSString stringWithFormat:@"%03ld %02ld", mcc, mnc] : @"";
}

static BOOL
registered(void)
{
	return cell_has(@"reg=1");
}

static long
bars(void)
{
	long dbm = cell_num(@"dbm");
	if (!registered() || dbm == 0) return 0;
	return dbm >= -85 ? 4 : dbm >= -95 ? 3 : dbm >= -105 ? 2 : 1;
}

static id
signal_info(void)
{
	id si = [NSClassFromString(@"CTSignalStrengthInfo") new];
	@try {
		[si setValue:@(bars()) forKey:@"bars"];
		[si setValue:@(bars()) forKey:@"displayBars"];
		[si setValue:@4 forKey:@"maxDisplayBars"];
	} @catch (NSException *e) {
		say(@"  signal info: %@", e.reason);
	}
	return si;
}

static NSString *
reg_status(void)
{
	return registered() ? ct_const("kCTRegistrationStatusRegisteredHome", @"kCTRegistrationStatusRegisteredHome")
	                    : ct_const("kCTRegistrationStatusNotRegistered", @"kCTRegistrationStatusNotRegistered");
}

static id
display_status(void)
{
	id ds = [NSClassFromString(@"CTRegistrationDisplayStatus") new];
	@try {
		[ds setValue:reg_status() forKey:@"registrationDisplayStatus"];
		[ds setValue:@YES forKey:@"isInHomeCountry"];
	} @catch (NSException *e) {
		say(@"  display status: %@", e.reason);
	}
	return ds;
}

/* LTE values (OnePlus 8 Pro port's facts): radioTechnology 7, indicator 7 ("4G"/LTE), dataBearerTechnology 4. */
static id
data_status(void)
{
	id d = [NSClassFromString(@"CTDataStatus") new];
	BOOL lte = registered() && cell_has(@"rat=lte");
	@try {
		[d setValue:@(registered()) forKey:@"attached"];
		[d setValue:@YES forKey:@"dataSim"];
		[d setValue:@(lte ? 7 : 0) forKey:@"indicator"];
		[d setValue:@(lte ? 7 : 0) forKey:@"radioTechnology"];
		[d setValue:@(lte ? 4 : 0) forKey:@"dataBearerTechnology"];
		[d setValue:@(registered()) forKey:@"cellularDataPossible"];
	} @catch (NSException *e) {
		say(@"  data status: %@", e.reason);
	}
	return d;
}

static NSString *
sim_status(void)
{
	return cell_has(@"sim=ready") ? ct_const("kCTSIMSupportSIMStatusReady", @"kCTSIMSupportSIMStatusReady")
	                              : ct_const("kCTSIMSupportSIMStatusNotInserted", @"kCTSIMSupportSIMStatusNotInserted");
}

/* Objects for a selector's reply block (in order; NSNull = nil); nil = no answer of ours. */
static NSArray *
answer_for(NSString *sel)
{
	NSNull *nul = [NSNull null];
	if ([sel isEqualToString:@"getSIMStatus:completion:"]) {
		return @[ sim_status(), nul ];
	}
	if ([sel isEqualToString:@"copyRegistrationStatus:completion:"]) {
		return @[ reg_status(), nul ];
	}
	if ([sel isEqualToString:@"copyRegistrationDisplayStatus:completion:"]) {
		return @[ display_status(), nul ];
	}
	if ([sel isEqualToString:@"copyOperatorName:completion:"] || [sel isEqualToString:@"copyLocalizedOperatorName:completion:"] ||
	    [sel isEqualToString:@"getShortLabel:completion:"]) {
		return @[ operator_name(), nul ];
	}
	if ([sel hasPrefix:@"copyMobileCountryCode:"] || [sel hasPrefix:@"copyMobileSubscriberCountryCode:"] ||
	    [sel hasPrefix:@"copyLastKnownMobileCountryCode:"]) {
		long mcc = cell_num(@"mcc");
		return @[ mcc ? [NSString stringWithFormat:@"%03ld", mcc] : (id)nul, nul ];
	}
	if ([sel hasPrefix:@"copyMobileSubscriberNetworkCode:"] || [sel hasPrefix:@"copyMobileNetworkCode:"]) {
		long mcc = cell_num(@"mcc");
		return @[ mcc ? [NSString stringWithFormat:@"%02ld", cell_num(@"mnc")] : (id)nul, nul ];
	}
	if ([sel isEqualToString:@"getSignalStrengthInfo:completion:"]) {
		return @[ signal_info(), nul ];
	}
	if ([sel isEqualToString:@"getDataStatus:completion:"] || [sel isEqualToString:@"getDataStatusBasic:completion:"]) {
		return @[ data_status(), nul ];
	}
	if ([sel isEqualToString:@"getUserDefaultVoiceSubscriptionContext:"] ||
	    [sel isEqualToString:@"getUserDataPreferredSubscriptionContext:"]) {
		id ctx = slot1_context();
		return ctx ? @[ ctx, nul ] : nil;
	}
	if ([sel isEqualToString:@"getSubscriptionInfo:"]) {
		id ctx = slot1_context();
		id info = [NSClassFromString(@"CTXPCServiceSubscriptionInfo") new];
		if (ctx == nil || info == nil) {
			return nil;
		}
		[info setValue:@[ ctx ] forKey:@"subscriptions"];
		[info setValue:@[ ctx ] forKey:@"subscriptionsInUse"];
		[info setValue:@[ ctx ] forKey:@"subscriptionsValid"];
		return @[ info, [NSNull null] ];
	}
	if ([sel isEqualToString:@"getActiveContexts:"]) {
		id ctx = slot1_context();
		id all = [NSClassFromString(@"CTXPCContexts") new];
		if (ctx == nil || all == nil) {
			return nil;
		}
		[all setValue:@[ ctx ] forKey:@"subscriptions"];
		[all setValue:[ctx valueForKey:@"uuid"] forKey:@"dataPreferred"];
		[all setValue:[ctx valueForKey:@"uuid"] forKey:@"voicePreferred"];
		return @[ all, [NSNull null] ];
	}
	return nil;
}

/* Call a reply block: object arguments from `objs` in order (NSNull = nil), the rest zero. The objects live in `objs`
   until the call returns (NSInvocation does not retain them). */
static void
reply_with(id block, NSArray *objs, NSString *what)
{
	const char *sig = _Block_signature((__bridge void *)block);
	if (sig == NULL) {
		return;
	}
	NSMethodSignature *ms = [NSMethodSignature signatureWithObjCTypes:sig];
	NSInvocation *inv = [NSInvocation invocationWithMethodSignature:ms];
	inv.target = block;
	NSUInteger o = 0;
	for (NSUInteger i = 1; i < ms.numberOfArguments; ++i) {
		const char *t = [ms getArgumentTypeAtIndex:i];
		if (t[0] == '@' && o < objs.count) {
			__unsafe_unretained id v = objs[o++];
			if (v == (id)[NSNull null]) {
				v = nil;
			}
			[inv setArgument:&v atIndex:(NSInteger)i];
			continue;
		}
		NSUInteger size = 0;
		NSGetSizeAndAlignment(t, &size, NULL);
		void *z = calloc(1, size ? size : 8);
		[inv setArgument:z atIndex:(NSInteger)i];
		free(z);
	}
	[inv invoke];
	(void)what;
}

/* Call a reply block with every argument zero (nil, 0, NO). */
static void
reply_neutral(id block, NSString *what)
{
	const char *sig = _Block_signature((__bridge void *)block);
	if (sig == NULL) {
		say(@"  %@: reply block without a signature: not called", what);
		return;
	}
	NSMethodSignature *ms = [NSMethodSignature signatureWithObjCTypes:sig];
	NSInvocation *inv = [NSInvocation invocationWithMethodSignature:ms];
	inv.target = block;
	for (NSUInteger i = 1; i < ms.numberOfArguments; ++i) {
		NSUInteger size = 0;
		NSGetSizeAndAlignment([ms getArgumentTypeAtIndex:i], &size, NULL);
		void *z = calloc(1, size ? size : 8);
		[inv setArgument:z atIndex:(NSInteger)i];
		free(z);
	}
	[inv invoke];
}

- (void)forwardInvocation:(NSInvocation *)inv
{
	NSString *sel = NSStringFromSelector(inv.selector);
	NSMethodSignature *ms = inv.methodSignature;
	if ([sel isEqualToString:@"registerForNotifications:completion:"] && ms.numberOfArguments >= 3) {
		__unsafe_unretained id names = nil;
		[inv getArgument:&names atIndex:2];
		if ([names isKindOfClass:[NSArray class]] || [names isKindOfClass:[NSSet class]]) {
			NSMutableSet *all = [NSMutableSet setWithSet:self.wanted ?: [NSSet set]];
			for (id n in names) {
				if ([n isKindOfClass:[NSString class]]) {
					[all addObject:n];
				}
			}
			self.wanted = all;
			if (![registered_clients containsObject:self]) {
				[registered_clients addObject:self];
			}
			SweetCT *me = self;
			dispatch_after(dispatch_time(DISPATCH_TIME_NOW, 300 * NSEC_PER_MSEC), dispatch_get_main_queue(), ^{
				notify_client(me, YES);
			});
		}
	}
	count([NSString stringWithFormat:@"%@ %@", self.client, sel]);
	static unsigned logged_ct;
	if (logged_ct++ < 2000) {
		say(@"CT %@ %@ (%lu args)", self.client, sel, (unsigned long)ms.numberOfArguments - 2);
	}
	for (NSUInteger i = 2; i < ms.numberOfArguments; ++i) {
		const char *t = [ms getArgumentTypeAtIndex:i];
		if (t[0] == '@' && t[1] == '?') {
			__unsafe_unretained id block = nil;
			[inv getArgument:&block atIndex:(NSInteger)i];
			if (block != nil) {
				NSArray *objs = answer_for(sel);
				if (objs != nil) {
					reply_with(block, objs, sel);
				} else {
					reply_neutral(block, sel);
				}
			}
		} else if (t[0] == '@') {
			__unsafe_unretained id obj = nil;
			[inv getArgument:&obj atIndex:(NSInteger)i];
			NSString *d = [[obj description] stringByReplacingOccurrencesOfString:@"\n" withString:@" "];
			if (d.length > 160) {
				d = [d substringToIndex:160];
			}
			say(@"  arg %lu: %@", (unsigned long)i - 2, d);
		}
	}
}
@end

@interface SweetListenerDelegate : NSObject <NSXPCListenerDelegate>
@end

@implementation SweetListenerDelegate
- (BOOL)listener:(NSXPCListener *)listener shouldAcceptNewConnection:(NSXPCConnection *)c
{
	NSString *who = proc_name(c.processIdentifier);
	count([NSString stringWithFormat:@"connection CT %@", who]);
	say(@"CT connection from %@", who);
	c.exportedInterface = [NSXPCInterface interfaceWithProtocol:ct_proto];
	SweetCT *obj = [SweetCT new];
	obj.client = who;
	obj.conn = c;
	c.exportedObject = obj;
	if (ct_delegate_proto != nil) {
		c.remoteObjectInterface = [NSXPCInterface interfaceWithProtocol:ct_delegate_proto];
	}
	__weak SweetCT *weak = obj;
	c.invalidationHandler = ^{
		SweetCT *o = weak;
		if (o != nil) {
			dispatch_async(dispatch_get_main_queue(), ^{
				[registered_clients removeObject:o];
			});
		}
	};
	[c resume];
	return YES;
}
@end

/* ---- plain XPC: every other CommCenter service ---- */

static NSString *
xpc_short(xpc_object_t o)
{
	char *d = xpc_copy_description(o);
	NSString *s = [[NSString stringWithUTF8String:d ? d : ""] stringByReplacingOccurrencesOfString:@"\n" withString:@" "];
	free(d);
	return s.length > 300 ? [s substringToIndex:300] : s;
}

/* typed answers for the old _CTServerConnection property getters (kPacketGetProperty, kRegistrationGetProperty);
 * types from CoreTelephony's readers (bool: dyn_cast_or_default(obj, bool), string: copied to a CFString) */
static xpc_object_t
plain_property(const char *key)
{
	if (strcmp(key, "kCellularDataHideRatIndicator") == 0 || strcmp(key, "kCellularDataHideIndicator") == 0 ||
	    strcmp(key, "kRegistrationEmergencyCallBackMode") == 0) {
		return xpc_bool_create(false);
	}
	if (strcmp(key, "kRegistrationIsInHomeCountry") == 0) {
		return xpc_bool_create(true);
	}
	if (strcmp(key, "kRegistrationIsDataAttached") == 0) {
		return xpc_bool_create(registered());
	}
	if (registered() && strcmp(key, "kRegistrationMCC") == 0) {
		return xpc_string_create([[NSString stringWithFormat:@"%ld", cell_num(@"mcc")] UTF8String]);
	}
	if (registered() && strcmp(key, "kRegistrationOperatorName") == 0) {
		return xpc_string_create([operator_name() UTF8String]);
	}
	return NULL;
}

static void
plain_listen(const char *service)
{
	NSString *svc = [NSString stringWithUTF8String:service];
	xpc_connection_t l = p_create_mach_service(service, dispatch_get_main_queue(), XPC_CONNECTION_MACH_SERVICE_LISTENER);
	xpc_connection_set_event_handler(l, ^(xpc_object_t peer) {
		if (xpc_get_type(peer) != XPC_TYPE_CONNECTION) {
			return;
		}
		NSString *who = proc_name(p_get_pid(peer));
		count([NSString stringWithFormat:@"connection %@ %@", svc, who]);
		xpc_connection_set_event_handler(peer, ^(xpc_object_t msg) {
			if (xpc_get_type(msg) != XPC_TYPE_DICTIONARY) {
				return;
			}
			const char *req = xpc_dictionary_get_string(msg, "kRequest");
			NSString *r = req ? [NSString stringWithUTF8String:req] : @"(no kRequest)";
			count([NSString stringWithFormat:@"%@ %@ %@", svc, who, r]);
			static unsigned logged;
			if (logged++ < 3000) {
				say(@"XPC %@ %@ %@: %@", svc, who, r, xpc_short(msg));
			}
			xpc_object_t reply = xpc_dictionary_create_reply(msg);
			if (reply != NULL) {
				/* echo: the request's keys and placeholder values back; property keys with a known type get a real
				 * value (a null makes CoreTelephony fall back to its default, which for the hide-indicator keys is
				 * "hide": SpringBoard then takes the line for a bootstrap one and shows SOS) */
				xpc_dictionary_apply(msg, ^bool(const char *key, xpc_object_t value) {
					if (strcmp(key, "kRequest") != 0) {
						xpc_object_t v = plain_property(key);
						xpc_dictionary_set_value(reply, key, v != NULL ? v : value);
					}
					return true;
				});
				xpc_connection_send_message(peer, reply);
			}
		});
		xpc_connection_resume(peer);
	});
	xpc_connection_resume(l);
	say(@"plain XPC listener: %@", svc);
}

int
main(void)
{
	@autoreleasepool {
		t0 = clock_gettime_nsec_np(CLOCK_MONOTONIC);
		log_q = dispatch_queue_create("log", DISPATCH_QUEUE_SERIAL);
		log_ring = [NSMutableArray array];
		counts = [NSMutableDictionary dictionary];
		say(@"sweet-telephonyd start; modem: %@", cell_state());
		p_create_mach_service = dlsym(RTLD_DEFAULT, "xpc_connection_create_mach_service");
		p_get_pid = dlsym(RTLD_DEFAULT, "xpc_connection_get_pid");
		if (p_create_mach_service == NULL || p_get_pid == NULL) {
			say(@"xpc_connection_create_mach_service / get_pid not found");
			log_flush();
			sleep(6);
			return 1;
		}

		/* what MobileGestalt answers for the cellular capabilities (SpringBoard's status bar uses them) */
		dlopen("/usr/lib/libMobileGestalt.dylib", RTLD_NOW);
		CFTypeRef (*mg_copy)(CFStringRef, CFDictionaryRef) = dlsym(RTLD_DEFAULT, "MGCopyAnswer");
		static const char *const mg_keys[] = {
			"contains-cellular-radio", "cellular-telephony-capability", "telephony", "HasBaseband",
			"cellular-data", "BasebandChipset", "DeviceSupportsSOS", "sms", "BasebandClass",
		};
		/* MGCopyAnswer only: MGGetBoolAnswer aborts the process for a key whose answer is not a boolean */
		for (unsigned i = 0; mg_copy != NULL && i < sizeof(mg_keys) / sizeof(mg_keys[0]); ++i) {
			CFStringRef k = CFStringCreateWithCString(NULL, mg_keys[i], kCFStringEncodingUTF8);
			CFTypeRef v = mg_copy(k, NULL);
			say(@"MG %s: %@", mg_keys[i], (__bridge id)v);
			if (v != NULL) {
				CFRelease(v);
			}
			CFRelease(k);
		}

		dlopen("/System/Library/Frameworks/CoreTelephony.framework/CoreTelephony", RTLD_NOW);
		ct_proto = NSProtocolFromString(@"CTXPCServiceInterface");
		ct_delegate_proto = NSProtocolFromString(@"CoreTelephonyClientDelegateProxyInterface");
		registered_clients = [NSMutableArray array];
		say(@"CoreTelephonyClientDelegateProxyInterface: %@", ct_delegate_proto ? @"found" : @"NOT FOUND");
		say(@"CTXPCServiceInterface: %@", ct_proto ? @"found" : @"NOT FOUND");

		static const char *const plain[] = {
			"com.apple.commcenter.xpc", "com.apple.aps.CommCenter", "com.apple.basebandd.xpc",
			"com.apple.CellularPlanDaemon.xpc", "com.apple.commcenter.ari.rt.xpc", "com.apple.commcenter.atcs.xpc",
			"com.apple.commcenter.cupolicy.xpc", "com.apple.commcenter.mobile-helper-cbupdateservice",
			"com.apple.ipTelephony", "com.apple.usernotifications.delegate.com.apple.SIMSetupUIService",
		};
		for (unsigned i = 0; i < sizeof(plain) / sizeof(plain[0]); ++i) {
			plain_listen(plain[i]);
		}
		static SweetListenerDelegate *del;
		static NSXPCListener *ctl;
		if (ct_proto != nil) {
			del = [SweetListenerDelegate new];
			ctl = ((NSXPCListener * (*)(id, SEL, NSString *))objc_msgSend)([NSXPCListener alloc],
			    NSSelectorFromString(@"initWithMachServiceName:"), @"com.apple.commcenter.coretelephony.xpc");
			ctl.delegate = del;
			[ctl resume];
			say(@"NSXPC listener: com.apple.commcenter.coretelephony.xpc");
		}
		dispatch_source_t tick = dispatch_source_create(DISPATCH_SOURCE_TYPE_TIMER, 0, 0, dispatch_get_main_queue());
		dispatch_source_set_timer(tick, dispatch_time(DISPATCH_TIME_NOW, 5 * NSEC_PER_SEC), 5 * NSEC_PER_SEC, NSEC_PER_SEC);
		dispatch_source_set_event_handler(tick, ^{
			static unsigned n;
			if (n++ % 12 == 0) {
				say(@"modem: %@", cell_state());
			}
			for (SweetCT *c in [registered_clients copy]) {
				notify_client(c, NO);
			}
			log_flush();
		});
		dispatch_resume(tick);
		dispatch_main();
	}
	return 0;
}
