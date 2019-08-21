# test_sandbox.py
#
# Authors:
#   - Coumes Quentin <coumes.quentin@gmail.com>


import os
import tarfile
import unittest

from sandbox_api import Sandbox, Sandbox404


TEST_URL = os.environ.get("SANDBOX_URL", "http://127.0.0.1:7000/")
RESOURCE_DIR = os.path.join(os.path.dirname(__file__), "resources")



class SandboxTestCase(unittest.TestCase):
    
    def test_properties_specs(self):
        s = Sandbox(TEST_URL)
        for attr in Sandbox._specs:
            self.assertIsNotNone(getattr(s, attr))
    
    
    def test_properties_libs(self):
        s = Sandbox(TEST_URL)
        for attr in Sandbox._libs:
            self.assertIsNotNone(getattr(s, attr))
    
    
    def test_property_unknown(self):
        s = Sandbox(TEST_URL)
        with self.assertRaises(AttributeError):
            s.unknown
    
    
    def test_property_decorator(self):
        s = Sandbox(TEST_URL)
        self.assertIsInstance(s.cpu, dict)  # getter
        s.cpu = 2  # setter
        self.assertEqual(2, s.cpu)
        delattr(s, "cpu")  # deleter
        self.assertIsInstance(s.cpu, dict)
    
    
    def test_usage(self):
        s = Sandbox(TEST_URL)
        # self.assertEqual(0, s.usage())
        s.execute({"commands": ["sleep 0.5"]})
        self.assertGreater(s.usage(), 0.01)
    
    
    def test_download_env(self):
        s = Sandbox(TEST_URL)
        f = open(os.path.join(RESOURCE_DIR, "dae5f9a3-a911-4df4-82f8-b9343241ece5.tgz"), "rb")
        
        response = s.execute({
            "commands": ["true"],
            "save":     True,
        }, f)
        downloaded = s.download(response["environment"])
        
        f.seek(0)
        with tarfile.open(fileobj=f, mode="r|gz") as t1, \
                tarfile.open(fileobj=downloaded, mode="r|gz") as t2:
            l1 = [m.name for m in t1.getmembers() if m.name]
            l2 = [m.name for m in t2.getmembers() if m.name]
        
        self.assertEqual(len(l1), len(l2))
        self.assertEqual(sorted(l1), sorted(l2))
    
    
    def test_download_file(self):
        s = Sandbox(TEST_URL)
        f = open(os.path.join(RESOURCE_DIR, "dae5f9a3-a911-4df4-82f8-b9343241ece5.tgz"), "rb")
        
        response = s.execute({
            "commands": ["true"],
            "save":     True,
        }, f)
        downloaded = s.download(response["environment"], "dir/file1.txt")
        
        self.assertEqual(b"env1\n", downloaded.read())
    
    def test_download_unknown(self):
        s = Sandbox(TEST_URL)
        f = open(os.path.join(RESOURCE_DIR, "dae5f9a3-a911-4df4-82f8-b9343241ece5.tgz"), "rb")
        
        response = s.execute({
            "commands": ["true"],
            "save":     True,
        }, f)
        
        with self.assertRaises(Sandbox404):
            s.download(response["environment"], "unknown.unk")


if __name__ == '__main__':
    unittest.main()
