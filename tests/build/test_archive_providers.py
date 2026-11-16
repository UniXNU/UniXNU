"""Keep embedded component builds explicit without bypassing archive coverage."""
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from unixnu.kernel import archive_plan
from unixnu.util import Error


class ArchiveProviderTests(unittest.TestCase):
    def context(self, entries, providers=None, dependencies=()):
        specs = [dict(id='Platform', build=['platform.py']),
                 dict(id='SoftwareAES', build=['aes.py'], dependencies=list(dependencies))]
        return SimpleNamespace(schema_version=2, component_specs=specs,
                               board=dict(kernel=dict(archives=entries, embedded_components=providers or {})))

    def test_embedded_source_is_built_only_by_its_provider(self):
        ctx = self.context(['component:Platform', 'display.py'], {'SoftwareAES': 'display.py'})
        plan = archive_plan(ctx)
        self.assertEqual([(kind, item['id'] if kind == 'component' else item) for kind, item in plan],
                         [('component', 'Platform'), ('script', 'display.py')])

    def test_unclaimed_component_still_fails(self):
        with self.assertRaisesRegex(Error, 'needs component entries for: SoftwareAES'):
            archive_plan(self.context(['component:Platform', 'display.py']))

    def test_missing_or_repeated_provider_fails(self):
        for entries in (['component:Platform'], ['component:Platform', 'display.py', 'display.py']):
            with self.subTest(entries=entries), self.assertRaisesRegex(Error, 'one matching archive command'):
                archive_plan(self.context(entries, {'SoftwareAES': 'display.py'}))

    def test_duplicate_standalone_build_fails(self):
        with self.assertRaisesRegex(Error, 'also has a standalone recipe'):
            archive_plan(self.context(['component:Platform', 'component:SoftwareAES', 'display.py'],
                                      {'SoftwareAES': 'display.py'}))

    def test_unselected_component_fails(self):
        with self.assertRaisesRegex(Error, 'component Missing is not selected'):
            archive_plan(self.context(['component:Platform', 'display.py'], {'Missing': 'display.py'}))

    def test_dependency_cannot_run_before_embedded_provider(self):
        ctx = self.context(['component:Platform', 'display.py'], {'SoftwareAES': 'display.py'})
        ctx.component_specs[0]['dependencies'] = ['SoftwareAES']
        with self.assertRaisesRegex(Error, 'needed before its embedded provider'):
            archive_plan(ctx)

    def test_standalone_build_is_unchanged(self):
        plan = archive_plan(self.context(['component:Platform', 'component:SoftwareAES']))
        self.assertEqual([item['id'] for kind, item in plan], ['Platform', 'SoftwareAES'])

    def test_implicit_plan_retains_provider_dependencies(self):
        plan = archive_plan(self.context(['display.py'], {'SoftwareAES': 'display.py'}, ['Platform']))
        self.assertEqual([(kind, item['id'] if kind == 'component' else item) for kind, item in plan],
                         [('component', 'Platform'), ('script', 'display.py')])


if __name__ == '__main__':
    unittest.main()
