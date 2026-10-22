/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* Resize through F2FS, never by editing its on-disk allocation metadata. */
#define _GNU_SOURCE
#include <assert.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Non-Linux hosts build the same rounding self-test without device I/O. */
#if !defined(__linux__) && !defined(F2FS_SELF_TEST_ONLY)
#define F2FS_SELF_TEST_ONLY
#endif

#ifndef F2FS_SELF_TEST_ONLY
#include <dirent.h>
#include <fcntl.h>
#include <inttypes.h>
#include <limits.h>
#include <linux/fs.h>
#include <mntent.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/statfs.h>
#include <unistd.h>

#define F2FS_MAGIC 0xf2f52010U
#define F2FS_IOC_RESIZE_FS _IOW(0xf5, 16, uint64_t)
#define BLOCK_BYTES UINT64_C(4096)
#endif
#define SEG_BLOCKS UINT64_C(512)

static void fail(const char *message)
{
    fprintf(stderr, "STOP: %s (errno=%d: %s); do not change GPT or blindly retry\n",
            message, errno, strerror(errno));
    exit(1);
}

static uint64_t request_blocks(uint64_t before, uint64_t limit)
{
    uint64_t remainder = before % SEG_BLOCKS;
    if (limit <= remainder + SEG_BLOCKS)
        fail("target is too small");
    /* The kernel removes whole sections and retains the original remainder. */
    return (limit - remainder) / SEG_BLOCKS * SEG_BLOCKS;
}

#ifndef F2FS_SELF_TEST_ONLY
static uint64_t number(const char *s)
{
    char *end;
    errno = 0;
    unsigned long long value = strtoull(s, &end, 10);
    if (!*s || *s < '0' || *s > '9' || *end || errno || !value)
        fail("invalid positive integer");
    return value;
}

static uint32_t le32(const unsigned char *p)
{
    return (uint32_t)p[0] | (uint32_t)p[1] << 8 |
           (uint32_t)p[2] << 16 | (uint32_t)p[3] << 24;
}

static uint64_t le64(const unsigned char *p)
{
    return le32(p) | (uint64_t)le32(p + 4) << 32;
}

static uint64_t super_blocks(int fd)
{
    unsigned char copies[2][4096];
    if (pread(fd, copies, sizeof(copies), 0) != sizeof(copies))
        fail("cannot read both F2FS superblocks");
    const unsigned char *s = copies[0] + 1024;
    const unsigned char *t = copies[1] + 1024;
    /* shortcut: single-device, one segment per section; review other layouts before extending. */
    if (memcmp(s, t, 3072) || le32(s) != F2FS_MAGIC || le32(s + 16) != 12 ||
        le32(s + 20) != 9 || le32(s + 24) != 1 ||
        le32(s + 8) + le32(s + 12) != 12 ||
        le32(s + 8) < 9 || le32(s + 8) > 12)
        fail("unsupported F2FS geometry or disagreeing superblocks");
    /* devs[0].path begins at byte 2201 in the packed F2FS superblock. */
    if (s[2201] || (le32(s + 2180) & 2))
        fail("multi-device or zoned F2FS is unsupported");
    return le64(s + 36);
}

static int block_open(const char *path, uint64_t *bytes, struct stat *st)
{
    int fd = open(path, O_RDONLY | O_CLOEXEC);
    if (fd < 0 || fstat(fd, st) || !S_ISBLK(st->st_mode) || ioctl(fd, BLKGETSIZE64, bytes))
        fail("cannot identify block device");
    return fd;
}

static void directory_device(const char *node, const char *directory, const char *expected)
{
    char path[PATH_MAX];
    if (snprintf(path, sizeof(path), "/sys/class/block/%s/%s", node, directory) >= (int)sizeof(path))
        fail("path too long");
    DIR *dir = opendir(path);
    if (!dir)
        fail("cannot inspect device-mapper backing device");
    unsigned count = 0;
    struct dirent *entry;
    while ((entry = readdir(dir))) {
        if (entry->d_name[0] == '.')
            continue;
        if (!expected || strcmp(entry->d_name, expected))
            fail("unexpected device-mapper holder or backing device");
        count++;
    }
    closedir(dir);
    if (count != (expected ? 1U : 0U))
        fail("unsupported device-mapper topology");
}

static void backing_device(const char *raw, const char *mapped)
{
    const char *base = strrchr(mapped, '/');
    const char *rawbase = strrchr(raw, '/');
    if (!base || !rawbase)
        fail("unsupported /data device");
    if (!strcmp(raw, mapped)) {
        directory_device(rawbase + 1, "holders", NULL);
        return;
    }
    if (strncmp(base + 1, "dm-", 3))
        fail("unsupported /data device");
    directory_device(base + 1, "slaves", rawbase + 1);
    directory_device(rawbase + 1, "holders", base + 1);
    directory_device(base + 1, "holders", NULL);
}

static void mounted_device(char *device)
{
    FILE *mounts = setmntent("/proc/mounts", "r");
    if (!mounts)
        fail("cannot read mounts");
    struct mntent *entry;
    unsigned count = 0;
    while ((entry = getmntent(mounts))) {
        if (strcmp(entry->mnt_dir, "/data"))
            continue;
        if (strcmp(entry->mnt_type, "f2fs") || !hasmntopt(entry, "rw") ||
            strstr(entry->mnt_opts, "checkpoint=disable") || !realpath(entry->mnt_fsname, device))
            fail("/data must be mounted read-write as decrypted F2FS with checkpoints enabled");
        count++;
    }
    endmntent(mounts);
    if (count != 1)
        fail("expected exactly one /data mount");
}

static void require_unmounted(dev_t raw, dev_t mapped)
{
    FILE *mounts = setmntent("/proc/mounts", "r");
    if (!mounts)
        fail("cannot read mounts");
    struct mntent *entry;
    while ((entry = getmntent(mounts))) {
        struct stat st;
        if (stat(entry->mnt_dir, &st))
            fail("cannot inspect mountpoint");
        if (st.st_dev == raw || st.st_dev == mapped)
            fail("userdata or a bind mount is still mounted");
    }
    endmntent(mounts);
}

#endif

int main(int argc, char **argv)
{
    if (argc == 2 && !strcmp(argv[1], "self-test")) {
        assert(request_blocks(57685263, 40907796) == 40907264);
        assert(57685263 - (57685263 - request_blocks(57685263, 40907796)) / 512 * 512 == 40907535);
        for (uint64_t remainder = 0; remainder < 512; remainder++) {
            uint64_t before = 20000 * 512 + remainder;
            uint64_t request = request_blocks(before, 9000 * 512 + 101);
            assert(request % 512 == 0);
            assert(before - (before - request) / 512 * 512 <= 9000 * 512 + 101);
        }
        puts("PASS: F2FS section rounding");
        return 0;
    }
#ifdef F2FS_SELF_TEST_ONLY
    fprintf(stderr, "This host build supports self-test only. Device operations require a Linux/Android build.\n");
    return 2;
#else
    int probe = argc == 3 && !strcmp(argv[1], "probe");
    int shrink = argc == 6 && !strcmp(argv[1], "shrink");
    int offline = argc == 7 && !strcmp(argv[1], "offline");
    if (!probe && !shrink && !offline) {
        fprintf(stderr, "Usage: %s probe RAW | shrink RAW PART_BYTES OLD_BLOCKS LIMIT_BLOCKS | "
                "offline RAW PART_BYTES EXPECTED_BLOCKS LIMIT_BLOCKS MAPPER | self-test\n", argv[0]);
        return 2;
    }
    char raw[PATH_MAX], mapped[PATH_MAX];
    if (geteuid() || !realpath(argv[2], raw))
        fail("root and a valid userdata path are required");
    if (offline) {
        if (!realpath(argv[6], mapped))
            fail("missing decrypted mapping; keep recovery running");
    } else {
        mounted_device(mapped);
    }
    backing_device(raw, mapped);
    uint64_t rawbytes, mapbytes;
    struct stat rawstat, mapstat;
    int rawfd = block_open(raw, &rawbytes, &rawstat);
    int block = block_open(mapped, &mapbytes, &mapstat);
    close(rawfd);
    if (mapbytes != rawbytes || rawbytes % BLOCK_BYTES)
        fail("mapping length differs from userdata; footer encryption and offset mappings are unsupported");
    uint64_t before = super_blocks(block);
    if (!before || before > rawbytes / BLOCK_BYTES)
        fail("filesystem exceeds userdata");
    uint64_t limit = probe ? before : number(argv[5]);
    if (!probe && (rawbytes != number(argv[3]) || before != number(argv[4]) || limit > rawbytes / BLOCK_BYTES))
        fail("device or filesystem changed since planning");
    if (offline) {
        require_unmounted(rawstat.st_rdev, mapstat.st_rdev);
        if (before > limit)
            fail("filesystem does not fit the planned partition");
        puts("VERIFIED: unmounted filesystem fits the planned userdata partition");
        close(block);
        return 0;
    }
    int fs = open("/data", O_RDONLY | O_DIRECTORY | O_CLOEXEC);
    struct stat st;
    struct statfs info;
    if (fs < 0 || fstat(fs, &st) || st.st_dev != mapstat.st_rdev || fstatfs(fs, &info) ||
        (unsigned long)info.f_type != F2FS_MAGIC || info.f_bsize != BLOCK_BYTES)
        fail("mount identity or filesystem check failed");
    if (probe) {
        printf("{\"blocks\":%" PRIu64 ",\"available_blocks\":%" PRIu64
               ",\"partition_bytes\":%" PRIu64 ",\"mapped\":\"%s\"}\n",
               before, (uint64_t)info.f_bavail, rawbytes, mapped);
    } else if (before > limit) {
        uint64_t request = request_blocks(before, limit);
        uint64_t expected = before - (before - request) / SEG_BLOCKS * SEG_BLOCKS;
        if (before - request >= (uint64_t)info.f_bavail)
            fail("insufficient available space; kernel also needs reserved space");
        puts("Shrinking F2FS. Keep power connected; do not use the recovery UI.");
        fflush(stdout);
        if (syncfs(fs) || ioctl(fs, F2FS_IOC_RESIZE_FS, &request) || syncfs(fs))
            fail("F2FS shrink failed; retain GPT and inspect recovery logs");
        if (super_blocks(block) != expected || expected > limit)
            fail("unexpected F2FS shrink result");
        puts("VERIFIED: both F2FS superblocks fit the planned partition");
    } else {
        puts("VERIFIED: F2FS already fits; no resize needed");
    }
    close(fs);
    close(block);
    return 0;
#endif
}
