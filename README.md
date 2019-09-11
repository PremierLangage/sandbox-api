[![Build Status](https://travis-ci.org/qcoumes/sandbox-api.svg?branch=master)](https://travis-ci.org/qcoumes/sandbox-api)
[![codecov](https://codecov.io/gh/qcoumes/sandbox-api/branch/master/graph/badge.svg)](https://codecov.io/gh/qcoumes/sandbox-api)
[![CodeFactor](https://www.codefactor.io/repository/github/qcoumes/sandbox-api/badge)](https://www.codefactor.io/repository/github/qcoumes/sandbox-api)
[![PyPI Version](https://badge.fury.io/py/sandbox-api.svg)](https://badge.fury.io/py/sandbox-api)
[![Python 3.5+](https://img.shields.io/badge/python-3.5+-brightgreen.svg)](#)
[![License MIT](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://github.com/qcoumes/sandbox-api/blob/master/LICENSE)

# Python API for WIMS' adm/raw module

A Python 3 interface to communicate with a [sandbox](https://github.com/PremierLangage/sandbox)


## Installation

The latest stable version is available on [PyPI](https://pypi.org/project/sandbox-api/) :

```bash
pip install sandbox-api
```

or from the sources:

```bash
git clone https://github.com/qcoumes/sandbox-api
cd sandbox-api
python3 setup.py install
```
 
 
 ## Usage
 
 Sandbox-api is pretty straightforward to use, you just need to import Sandbox and create
 an instance with the url of the server :
 
 ```python
from sandbox_api import Sandbox

s = Sandbox("http://www.my-sandbox.com")
```

### Specifications and libraries

The specs of the sandbox and the libraries installed are available as attributes:

```python
s.cpu
{'count': 1, 'period': 1000, 'shares': 1024, 'quota': 0, 'name': 'Intel(R) Core(TM) i7-8700K CPU @ 3.70GHz'}

s.containers
{'total': 5, 'running': 0, 'available': 5}

s.python3
'3.7.3'

s.python2
'2.7.16'
```

Attribute other than 'url' are retrieved from the sandbox at first access, attribute are
separated in two categories, specifications and libraries. Every attribute of one category are
retrieved the first time an attribute of the corresponding category is accessed.

These attributes are fetch through HTTP requests, this can take some times (should be no more
than 2 seconds), especially for the libraries category.

Note that attributes are cached (except for 'containers'), and subsequent access to one category
are instantaneous.

Available attributes are:

* Specifications
    *   sandbox_version (str): Version of the sandbox formatted as 'MAJOR.MINOR.PATCH'.
    *   docker_version (str): Version of docker used by the sandbox formatted as 'MAJOR.MINOR.PATCH'
    *   containers (dict): Dict containing the status of the containers running on the sandbox.
    *   memory (dict): Memory limits for each containers on the sandbox.
    *   cpu (dict): CPU information for each containers on the sandbox.
    *   environ (dict): Environments variables use in the containers.
    *   execute_timeout (Union[int, float]): Time in seconds before an 'execute/' request timeout.
    *   expiration (int): Time in before an environment expire on the sandbox.
* Libraries
    *   python3 (str): Version of python3 used by the sandbox formatted as 'MAJOR.MINOR.PATCH'.
    *   python2 (str): Version of python2 used by the sandbox formatted as 'MAJOR.MINOR.PATCH'.
    *   java (str): Version of java used by the sandbox formatted as 'JDK MAJOR.MINOR'.
    *   gcc (str): Version of gcc used by the sandbox formatted as 'MAJOR.MINOR.PATCH'.
    *   gpp (str): Version of g++ used by the sandbox formatted as 'MAJOR.MINOR.PATCH'.
    *   perl (str): Version of perl used by the sandbox formatted as 'MAJOR.MINOR.PATCH'.
    *   postgres (str): Version of postgres used by the sandbox formatted as 'MAJOR.MINOR'.
    *   libraries (dict): Dict containing :
        *   system (dict): The installed packages (dpkg).
        *   c (dict): The installed libraries and their version.
        *   python (dict): The installed python modules.
        *   perl (dict): The installed perl modules.
    *   bin (dict): Every command available in PATH on the sandbox


### Sandbox current load

It is possible to obtain the current load of the sandbox with the `usage()` method.
It returns a float between 0 and 1, indicating the current charge on the sandbox, 0 means that the
sandbox is currently unused, 1 means that it is used a full capacity and an 'execute/' request will
probably be delayed.

```python
s.usage()
0.2
```


### Downloading environments and files

You can download files or environments through the `download(uuid, path=None)` method. `uuid`
correspond to the ID of the environment on the sandbox.

If only uuid is provided the whole environment will be downloading, if path is also provided, only
the file corresponding to path inside the environment will be downloaded.

The downloaded object is returned as a `io.BytesIO`.


### Executing commands

Use the `execute(config, environ=None)` method to execute commands on the sandbox. Config
must be a dictionary corresponding to a valid config as defined
[here](https://documenter.getpostman.com/view/7955851/S1a915EG?version=latest#872b604c-9cce-42e2-8888-9a0311f3a724),
environ, if provided, must be a binary object implementing the `.read()` (I.G. `file object` or
`io.BytesIO`) at position 0 corresponding to a valid environment (again, more information
[here](https://documenter.getpostman.com/view/7955851/S1a915EG?version=latest#872b604c-9cce-42e2-8888-9a0311f3a724)).

The returned value is a dictionary corresponding to the response's json :

You can check a config dictionnary by calling `sandbox_api.utils.validate(config)`.

```python
s.execute({
     "commands": [
             "echo $((2+2))"
     ]
})

{
    'status': 0,
    'execution': [
        {
            'command': 'echo $((2+2))',
            'exit_code': 0,
            'stdout': '4',
            'stderr': '',
            'time': 0.28589797019958496
        }
    ],
    'total_time': 0.2871053218841553
}
```

## Exceptions

Since sandbox-api rely on HTTP, any response with a status code greater or equal to 300 will raise
a corresponding exception `Sanbox{STATUS}` the response (a `requests.Response` object) received is
available in the `response` attribute of the exception.

All of these exceptions inherit `SandboxError`.

```python
from sandbox_api import SandboxError, Sandbox404

try:
    file = s.download("872b604c-9cce-42e2-8888-9a0311f3a724", "unknown")
except Sandbox404:
    print("'unknown' does not exists in environment '872b604c-9cce-42e2-8888-9a0311f3a724'")
except SandboxError as e:
    print("Sandbox responded with a '%d' status code" % e.response.status_code)
```