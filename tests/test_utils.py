import unittest

from sandbox_api.utils import validate



class ValidateTestCase(unittest.TestCase):
    
    def test_validate_commands_ok(self):
        self.assertTrue(validate({"commands": [{"command": "true"}]})[0])
        self.assertTrue(validate({"commands": [{"command": "true", "timeout": 1}]})[0])
        self.assertTrue(validate({"commands": [{"command": "true", "timeout": 1.0}]})[0])
    
    
    def test_validate_commands_wrong(self):
        self.assertFalse(validate({})[0])
        self.assertFalse(validate({"commands": object()})[0])
        self.assertFalse(validate({"commands": []})[0])
        self.assertFalse(validate({"commands": [{"timeout": 1}]})[0])
        self.assertFalse(validate({"commands": [{"command": object()}]})[0])
        self.assertFalse(validate({"commands": [{"command": object(), "timeout": 1}]})[0])
    
    
    def test_validate_commands_timeout_wrong(self):
        self.assertFalse(validate({"commands": [{"command": "true", "timeout": object()}]})[0])
    
    
    def test_validate_environ_ok(self):
        config = {
            "commands": [{"command": "true"}],
            "environ":  {
                "var1": "value1",
                "var2": "value2",
            }
        }
        self.assertTrue(validate(config)[0])
        config = {
            "commands": [{"command": "true"}],
            "environ":  {},
        }
        self.assertTrue(validate(config)[0])
    
    
    def test_validate_environ_not_dict(self):
        config = {
            "commands": [{"command": "true"}],
            "environ":  object(),
        }
        
        self.assertFalse(validate(config)[0])
    
    
    def test_validate_save_ok(self):
        config = {
            "commands": [{"command": "true"}],
            "save":     True,
        }
        self.assertTrue(validate(config)[0])
    
    
    def test_validate_save_not_bool(self):
        config = {
            "commands": [{"command": "true"}],
            "save":     object(),
        }
        
        self.assertFalse(validate(config)[0])
    
    
    def test_validate_result_path_ok(self):
        config = {
            "commands":    [{"command": "true"}],
            "result_path": "path/to/file",
        }
        self.assertTrue(validate(config)[0])
    
    
    def test_validate_result_path_not_string(self):
        config = {
            "commands": [{"command": "true"}],
            "result_path":     object(),
        }
        
        self.assertFalse(validate(config)[0])
