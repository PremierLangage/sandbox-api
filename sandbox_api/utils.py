# utils.py
#
# Authors:
#   - Coumes Quentin <coumes.quentin@gmail.com>


from typing import Tuple


# Lists of the sandbox's endpoints
ENDPOINTS = {
    "specifications": "specifications/",
    "libraries":      "libraries/",
    "usages":         "usages/",
    "environments":   "environments/%s/",
    "files":          "files/%s/%s/",
    "execute":        "execute/",
}


def validate_command(c: dict) -> bool:
    """Returns True if <d> is a valid representation of a command,
    False otherwise.

    Check that:
        - 'command' is present and is a string.
        - if 'timeout' is present, it is either an integer or a float."""
    return all((
        'command' in c and isinstance(c["command"], str),
        "timeout" not in c or isinstance(c["timeout"], (int, float)),
    ))


def validate(config: dict) -> Tuple[bool, str]:
    """Check the validity of a config dictionary.
    
    Returns a tuple (bool, msg). If bool is True, the config dictionary is valid
    and msg is an empty string.
    If bool is False, the config dictionary is invalid and msg contains a
    message explaining the error."""
    if "result_path" in config and not isinstance(config["result_path"], str):
        return False, f'result_path must be a string, not {type(config["result_path"])}'
    if "save" in config and not isinstance(config["save"], bool):
        return False, f'save must be a boolean, not {type(config["save"])}'
    if "environ" in config and not isinstance(config["environ"], dict):
        return False, f'environ must be a dict, not {type(config["environ"])}'
    
    if 'commands' not in config:
        return False, "Missing field 'commands' in config"
    if not isinstance(config["commands"], list):
        return False, f'commands must be a list, not {type(config["commands"])}'
    if not config["commands"]:
        return False, f'commands list is empty'
    
    for c in config["commands"]:
        if not ((isinstance(c, dict) and validate_command(c)) or isinstance(c, str)):
            return False, f"Command badly formatted : '{c}'"
    
    return True, ""
