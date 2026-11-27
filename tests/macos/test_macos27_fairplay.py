#!/usr/bin/env python3
"""Check the macOS 27.3 FairPlayIOKit prelink root and the vmm-hide kern.hv_vmm_present filter."""
from pathlib import Path
import subprocess
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[2]
PROFILE_DIR = ROOT / 'profiles/os/macos-27.3-26C5035r'
PATCH = PROFILE_DIR / 'patches/xnu-12377/macos-vmm-present-proc-filter.patch'


class Macos27FairPlayTest(unittest.TestCase):
    def test_fairplay_iokit_prelink_and_vmm_present_filter_patch(self):
        profile = tomllib.loads((PROFILE_DIR / 'profile.toml').read_text())
        roots = profile['kernel']['prelink']['roots']
        self.assertIn('com.apple.driver.FairPlayIOKit', roots)

        entries = [
            line.strip()
            for line in (PROFILE_DIR / 'patches/xnu/series').read_text().splitlines()
            if line.strip() and not line.strip().startswith('#')
        ]
        self.assertIn('../xnu-12377/macos-vmm-present-proc-filter.patch', entries)

        self.assertTrue(PATCH.is_file(), f'missing patch: {PATCH}')
        text = PATCH.read_text()
        for marker in (
            '--- a/bsd/kern/hvg_sysctl.c',
            '+++ b/bsd/kern/hvg_sysctl.c',
            'native_vmm_hide_hits',
            'native_vmm_present_hidden_in_list(',
            'PE_parse_boot_arg_str("vmm-hide"',
            'proc_best_name(req->p)',
        ):
            self.assertIn(marker, text)
        diff_body = text[text.index('diff --git'):]
        for forbidden in ('p_comm', 'proc_name_address'):
            self.assertNotIn(forbidden, diff_body)

    def test_vmm_hide_matcher_host_execution(self):
        added_lines = [
            line[1:]
            for line in PATCH.read_text().splitlines()
            if line.startswith('+') and not line.startswith('+++')
        ]
        added_src = '\n'.join(added_lines)
        start = added_src.index('static bool\nnative_vmm_present_hidden_in_list(')
        end = added_src.index('\n}\n', start) + 3
        fn_src = added_src[start:end]

        c_driver = (
            '#include <assert.h>\n'
            '#include <stdbool.h>\n'
            '#include <stddef.h>\n'
            '#include <stdio.h>\n'
            '#include <string.h>\n\n'
            + fn_src
            + r'''
int main(void) {
  const char *def = "adid,fairplayd,fairplaydeviceidentityd,akd";
  assert(native_vmm_present_hidden_in_list(def, "adid"));
  assert(native_vmm_present_hidden_in_list(def, "fairplayd"));
  assert(native_vmm_present_hidden_in_list(def, "fairplaydeviceidentityd"));
  assert(native_vmm_present_hidden_in_list(def, "akd"));

  const char *ext = "adid,fairplayd,fairplaydeviceidentityd,akd,appstored,storeaccountd,apsd,identityservicesd";
  assert(native_vmm_present_hidden_in_list(ext, "identityservicesd"));
  assert(native_vmm_present_hidden_in_list(ext, "storeaccountd"));

  assert(!native_vmm_present_hidden_in_list(def, "pakd"));
  assert(!native_vmm_present_hidden_in_list(def, "akd2"));
  assert(!native_vmm_present_hidden_in_list(def, "fairplay"));
  assert(!native_vmm_present_hidden_in_list(def, "fairplaydeviceid"));
  assert(!native_vmm_present_hidden_in_list(def, "myadid"));
  assert(!native_vmm_present_hidden_in_list(def, "watchdogd"));
  assert(!native_vmm_present_hidden_in_list(def, "WindowServer"));
  assert(!native_vmm_present_hidden_in_list(def, ""));
  assert(!native_vmm_present_hidden_in_list(def, NULL));

  assert(!native_vmm_present_hidden_in_list("", "adid"));
  assert(!native_vmm_present_hidden_in_list("0", "adid"));
  assert(!native_vmm_present_hidden_in_list("none", "akd"));
  assert(!native_vmm_present_hidden_in_list(NULL, "adid"));

  const char *commas = ",adid,,akd,";
  assert(!native_vmm_present_hidden_in_list(commas, ""));
  assert(native_vmm_present_hidden_in_list(commas, "adid"));
  assert(native_vmm_present_hidden_in_list(commas, "akd"));
  assert(!native_vmm_present_hidden_in_list(commas, ","));

  puts("PASS: vmm-hide matcher");
  return 0;
}
'''
        )
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / 'matcher.c'
            exe = Path(tmp) / 'matcher'
            src.write_text(c_driver)
            build = subprocess.run(
                ['clang', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                 '-fsanitize=address,undefined', str(src), '-o', str(exe)],
                capture_output=True, text=True,
            )
            self.assertEqual(build.returncode, 0, f'compile failed:\n{build.stderr}')
            run = subprocess.run([str(exe)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, f'run failed:\n{run.stderr}')
            self.assertIn('PASS: vmm-hide matcher', run.stdout)


if __name__ == '__main__':
    unittest.main()
