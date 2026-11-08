// SPDX-License-Identifier: AGPL-3.0-or-later
// Procursus ldid as a library. installd's sandbox denies process-fork, so the
// AppSync adapter signs inside installd instead of starting unixnu-ldid.
// This translation unit includes ldid.cpp to reach its file-local option
// state, which a second command in the same process must start from again.

// Every system header ldid.cpp uses comes first, so the two macros below only
// rewrite ldid's own code.
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <exception>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <mutex>
#include <set>
#include <sstream>
#include <streambuf>
#include <string>
#include <vector>

#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <regex.h>
#include <stdbool.h>
#include <stdint.h>
#include <unistd.h>

#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>

#include <openssl/opensslv.h>
#if OPENSSL_VERSION_MAJOR >= 3
#include <openssl/provider.h>
#endif
#include <openssl/asn1t.h>
#include <openssl/err.h>
#include <openssl/evp.h>
#include <openssl/pem.h>
#include <openssl/pkcs12.h>
#include <openssl/pkcs7.h>
#include <openssl/ui.h>
#include <openssl/x509.h>

#include <plist/plist.h>

namespace unixnu_ldid {
struct Stop {
    int code;
};

[[noreturn]] static void stop(int code) {
    throw Stop{code};
}
}

// ldid ends a failed command with exit(), which would end installd. Inside
// this unit it unwinds to unixnu_ldid_sign_bundle instead.
#define exit(code) unixnu_ldid::stop(code)
#define main unixnu_ldid_main
#include "ldid.cpp"
#undef main
#undef exit

// Signs the bundle or Mach-O at path ad-hoc, keeping its entitlements: the
// command "ldid -Hsha256 -M -S path". Returns 0 on success; otherwise writes a
// reason into message. Calls are serialized because ldid keeps global state.
extern "C" __attribute__((visibility("default")))
int unixnu_ldid_sign_bundle(const char *path, char *message, size_t size) {
    static std::mutex lock;
    std::lock_guard<std::mutex> guard(lock);
    auto report = [&](const std::string &text) {
        if (message && size) snprintf(message, size, "%s", text.c_str());
    };
    report("");
    if (!path || !*path) {
        report("no path to sign");
        return 1;
    }

    // Defaults of ldid's globals; an earlier command changed them.
    flag_w = false;
    flag_U = false;
    password.clear();
    flag_H = false;
    flag_t = NULL;
    do_sha1 = true;
    do_sha256 = true;
    cleanup.clear();

    std::string target(path);
    char program[] = "ldid", hash[] = "-Hsha256", merge[] = "-M", adhoc[] = "-S";
    char *arguments[] = {program, hash, merge, adhoc, &target[0], NULL};
    int status;
    try {
        status = unixnu_ldid_main(5, arguments);
        if (status)
            report("ldid returned " + std::to_string(status));
    } catch (const unixnu_ldid::Stop &stop) {
        status = stop.code;
        if (status)
            report("ldid stopped with status " + std::to_string(status));
    } catch (const char *problem) {
        status = 1;
        report(problem);
    } catch (const std::exception &problem) {
        status = 1;
        report(problem.what());
    } catch (...) {
        status = 1;
        report("ldid raised an unknown exception");
    }
    // A failed write leaves its ".ldid." temporary beside the target. ldid's
    // main also registers cleanupfunc with atexit on every call; the list is
    // empty after each call, so those registrations remove nothing later.
    cleanupfunc();
    cleanup.clear();
    return status;
}
