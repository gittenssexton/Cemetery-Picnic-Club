"""Offline geology pipeline safety tests; synthetic data, no source downloads."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts/geology/ma_zen1983_pipeline.py'
spec=importlib.util.spec_from_file_location('ma_zen1983_pipeline',SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestProcessing(unittest.TestCase):
    def test_known_source_hashes(self):
        self.assertEqual(len(mod.EXPECTED_SHA),2)
        self.assertTrue(all(len(x)==64 for x in mod.EXPECTED_SHA.values()))

    def test_synthetic_zip_extract(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);path=root/'test.zip'
            with zipfile.ZipFile(path,'w') as z:
                for member in mod.EXPECTED_MEMBERS:
                    z.writestr(member,b'test')
            mod.extract(path,root/'output')
            self.assertTrue(all((root/'output'/p).exists() for p in mod.EXPECTED_MEMBERS))
            mod.extract(path,root/'output')

    def test_missing_archive_member_fails(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'test.zip'
            with zipfile.ZipFile(path,'w') as z:z.writestr('README.txt',b'dummy')
            with self.assertRaises(ValueError):mod.verify(path)

    def test_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'test.zip'
            with zipfile.ZipFile(path,'w') as z:
                for member in mod.EXPECTED_MEMBERS:z.writestr(member,b'0')
                z.writestr('../escape.txt',b'attack')
            with self.assertRaises(ValueError):mod.extract(path,Path(t)/'output')
            self.assertFalse((Path(t)/'escape.txt').exists())

    def test_corrupt_existing_file_fails(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'test.zip'
            with zipfile.ZipFile(path,'w') as z:
                for member in mod.EXPECTED_MEMBERS:z.writestr(member,b'good')
            output=Path(t)/'output';output.mkdir()
            (output/'README.txt').write_bytes(b'bad')
            with self.assertRaises(FileExistsError):mod.extract(path,output)

if __name__=='__main__':unittest.main()