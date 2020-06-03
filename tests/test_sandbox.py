# test_sandbox.py
#
# Authors:
#   - Coumes Quentin <coumes.quentin@gmail.com>


import os
import tarfile
import time
import unittest

from sandbox_api import Sandbox, Sandbox400, Sandbox404
from sandbox_api.enums import SandboxErrCode
from tests.utils import ENV1, RESOURCES_ROOT


TEST_URL = os.environ.get("SANDBOX_URL", "http://127.0.0.1:7000/")
RESOURCE_DIR = os.path.join(os.path.dirname(__file__), "resources")


class SandboxTestCase(unittest.TestCase):
    
    def test_usage(self):
        s = Sandbox(TEST_URL)
        self.assertTrue(dict, type(s.usage()))
    
    
    def test_libraries(self):
        s = Sandbox(TEST_URL)
        self.assertTrue(dict, type(s.libraries()))
    
    
    def test_specifications(self):
        s = Sandbox(TEST_URL)
        self.assertTrue(dict, type(s.specifications()))


class SandboxExecuteTestCase(unittest.TestCase):
    
    def test_execute_ok_without_env(self):
        s = Sandbox(TEST_URL)
        result = s.execute({
            "commands": [
                "true",
                {"command": "echo $((1+1))", "timeout": 1},
                "-false",
            ]
        })
        self.assertEqual(0, result["status"])
        self.assertEqual(3, len(result["execution"]))
        self.assertEqual("2", result["execution"][1]["stdout"])
        
        real_total = sum(r["time"] for r in result["execution"])
        self.assertTrue(result["total_time"] - 0.5 <= real_total <= result["total_time"])
    
    
    def test_execute_ok_with_env_config(self):
        s = Sandbox(TEST_URL)
        env = s.execute({
            "commands": ["true"],
            "save":     True,
        })["environment"]
        result = s.execute({
            "commands":    [
                'echo "Hello World !" > result.txt'
            ],
            "environment": env,
            "result_path": "result.txt"
        })
        self.assertEqual(0, result["status"])
        self.assertEqual(1, len(result["execution"]))
        self.assertNotIn("environment", result)
        self.assertEqual("Hello World !\n", result["result"])
        
        real_total = sum(r["time"] for r in result["execution"])
        self.assertTrue(result["total_time"] - 0.5 <= real_total <= result["total_time"])
    
    
    def test_execute_ok_with_env_body_save(self):
        s = Sandbox(TEST_URL)
        result = s.execute({
            "commands":    [
                'echo "Hello World !" > result.txt'
            ],
            "result_path": "result.txt",
            "save":        True,
        }, open(os.path.join(RESOURCES_ROOT, f"{ENV1}.tgz"), "rb"))
        
        self.assertEqual(0, result["status"])
        self.assertEqual(1, len(result["execution"]))
        self.assertIn("environment", result)
        self.assertEqual("Hello World !\n", result["result"])
        
        real_total = sum(r["time"] for r in result["execution"])
        self.assertTrue(result["total_time"] - 0.5 <= real_total <= result["total_time"])
    
    
    def test_execute_ok_with_env_config_and_body_save(self):
        s = Sandbox(TEST_URL)
        env = s.execute({
            "commands": ["true"],
            "save":     True,
        })["environment"]
        result = s.execute({
            "commands":    [
                'echo "Hello World !" > result.txt'
            ],
            "result_path": "result.txt",
            "save":        True,
            "environment": env,
        }, open(os.path.join(RESOURCES_ROOT, f"{ENV1}.tgz"), "rb"))
        
        self.assertEqual(0, result["status"])
        self.assertEqual(1, len(result["execution"]))
        self.assertIn("environment", result)
        self.assertEqual("Hello World !\n", result["result"])
        
        real_total = sum(r["time"] for r in result["execution"])
        self.assertTrue(result["total_time"] - 0.5 <= real_total <= result["total_time"])
    
    
    def test_execute_ok_environ(self):
        s = Sandbox(TEST_URL)
        result = s.execute({
            "commands": [
                'echo $VAR1'
            ],
            "environ":  {
                "VAR1": "My var"
            },
        })
        self.assertEqual(0, result["status"])
        self.assertEqual(1, len(result["execution"]))
        self.assertEqual("My var", result["execution"][0]["stdout"])
    
    
    def test_execute_timeout(self):
        s = Sandbox(TEST_URL)
        result = s.execute({
            "commands": [
                {"command": "echo $((1+1))", "timeout": 1},
                {"command": "sleep 1", "timeout": 0.2},
            ],
        })
        self.assertEqual(SandboxErrCode.TIMEOUT, result["status"])
        self.assertEqual("sleep 1", result["execution"][1]["command"])
        self.assertEqual(SandboxErrCode.TIMEOUT, result["execution"][1]["exit_code"])
        self.assertEqual("", result["execution"][1]["stdout"])
        self.assertEqual(f"Command timed out after 0.2 seconds\n", result["execution"][1]["stderr"])
        self.assertIsInstance(result["execution"][1]["time"], float)
        self.assertLessEqual(result["execution"][1]["time"], 0.25)
    
    
    def test_execute_failing(self):
        s = Sandbox(TEST_URL)
        result = s.execute({
            "commands": [
                "false"
            ]
        })
        self.assertEqual(1, len(result["execution"]))
        real_total = sum(r["time"] for r in result["execution"])
        self.assertTrue(result["total_time"] - 0.5 <= real_total <= result["total_time"])
    
    
    def test_execute_result_not_found(self):
        s = Sandbox(TEST_URL)
        result = s.execute({
            "commands":    [
                "true"
            ],
            "result_path": "unknown.txt"
        })
        
        self.assertEqual(SandboxErrCode.RESULT_NOT_FOUND, result["status"])
        self.assertEqual(1, len(result["execution"]))
    
    
    def test_execute_missing_config(self):
        s = Sandbox(TEST_URL)
        with self.assertRaises(Sandbox400):
            s.execute({})
    
    
    def test_execute_config_not_dict(self):
        s = Sandbox(TEST_URL)
        with self.assertRaises(Sandbox400):
            s.execute("Definitely not json")


class SandboxDownloadTestCase(unittest.TestCase):
    
    def test_download_env(self):
        s = Sandbox(TEST_URL)
        f = open(os.path.join(RESOURCE_DIR, "dae5f9a3-a911-4df4-82f8-b9343241ece5.tgz"), "rb")
        
        response = s.execute({
            "commands": ["true"],
            "save":     True,
        }, f)
        time.sleep(0.1)
        downloaded = s.download(response["environment"])

        f = open(os.path.join(RESOURCE_DIR, "dae5f9a3-a911-4df4-82f8-b9343241ece5.tgz"), "rb")
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
        time.sleep(0.1)
        downloaded = s.download(response["environment"], "dir/file1.txt")
        
        self.assertEqual(b"env1\n", downloaded.read())
    
    
    def test_download_env_unknown(self):
        s = Sandbox(TEST_URL)
        time.sleep(0.1)
        with self.assertRaises(Sandbox404):
            s.download("unknown")
    
    
    def test_download_file_unknown(self):
        s = Sandbox(TEST_URL)
        f = open(os.path.join(RESOURCE_DIR, "dae5f9a3-a911-4df4-82f8-b9343241ece5.tgz"), "rb")
        
        response = s.execute({
            "commands": ["true"],
            "save":     True,
        }, f)
        
        time.sleep(0.1)
        with self.assertRaises(Sandbox404):
            s.download(response["environment"], "unknown.unk")


class SandboxCheckTestCase(unittest.TestCase):
    
    def test_check_env(self):
        s = Sandbox(TEST_URL)
        f = open(os.path.join(RESOURCE_DIR, "dae5f9a3-a911-4df4-82f8-b9343241ece5.tgz"), "rb")
        
        response = s.execute({
            "commands": ["true"],
            "save":     True,
        }, f)
        time.sleep(0.1)
        self.assertTrue(s.check(response["environment"]))
    
    
    def test_check_file(self):
        s = Sandbox(TEST_URL)
        f = open(os.path.join(RESOURCE_DIR, "dae5f9a3-a911-4df4-82f8-b9343241ece5.tgz"), "rb")
        
        response = s.execute({
            "commands": ["true"],
            "save":     True,
        }, f)
        time.sleep(0.1)
        self.assertTrue(s.check(response["environment"], "dir/file1.txt"))
    
    
    def test_check_env_unknown(self):
        s = Sandbox(TEST_URL)
        time.sleep(0.1)
        self.assertFalse(s.check("unknown"))
    
    
    def test_check_file_unknown(self):
        s = Sandbox(TEST_URL)
        f = open(os.path.join(RESOURCE_DIR, "dae5f9a3-a911-4df4-82f8-b9343241ece5.tgz"), "rb")
        
        response = s.execute({
            "commands": ["true"],
            "save":     True,
        }, f)
        time.sleep(0.1)
        self.assertFalse(s.check(response["environment"], "unknown.unk"))
