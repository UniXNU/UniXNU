#pragma once
/*
 * Per-phone constants. Default is sweet (Redmi Note 10 Pro, SM7150);
 * shim/build.sh BOARD=umi builds for the Xiaomi Mi 10 (SM8250).
 * GIC, PS_HOLD, UFS host and the splash framebuffer base are the same on both.
 */
#if defined(BOARD_UMI)
#define BOARD_NAME		"umi"
#define IMEM_RESTART_REASON	0x146bf65cUL	/* qcom,msm-imem@146bf000 restart_reason@65c */
#define BOARD_FB_H		2340		/* 1080x2340 DSC cmd-mode AMOLED */
#define VTIMER_INTID		27		/* DT: standard <GIC_PPI 11 ...> */
#define PTIMER_INTID		30		/* DT: <GIC_PPI 14 ...> */
#else
#define BOARD_NAME		"sweet"
#define IMEM_RESTART_REASON	0x146aa65cUL	/* qcom,msm-imem restart_reason@65c */
#define BOARD_FB_H		2400
#define VTIMER_INTID		19		/* DT: <GIC_PPI 3 ...>, not the usual 27 */
#define PTIMER_INTID		18		/* DT: <GIC_PPI 2 ...> */
#endif
