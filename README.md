[![Python package](https://github.com/qcoumes/sandbox-api/workflows/Python%20package/badge.svg)](https://github.com/qcoumes/sandbox-api/actions/)
[![codecov](https://codecov.io/gh/qcoumes/sandbox-api/branch/master/graph/badge.svg)](https://codecov.io/gh/qcoumes/sandbox-api)
[![CodeFactor](https://www.codefactor.io/repository/github/qcoumes/sandbox-api/badge)](https://www.codefactor.io/repository/github/qcoumes/sandbox-api)
[![PyPI Version](https://badge.fury.io/py/sandbox-api.svg)](https://badge.fury.io/py/sandbox-api)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-brightgreen.svg)](#)
[![License MIT](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://github.com/qcoumes/sandbox-api/blob/master/LICENSE)

# Python API for WIMS' adm/raw module

A Python 3 interface to communicate with a [sandbox](https://github.com/PremierLangage/sandbox)


## Installation

The latest stable version is available on [PyPI](https://pypi.org/project/sandbox-api/) :

```bash
pip install sandbox-api
```

or from sources:

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

sandbox = Sandbox("http://www.my-sandbox.com")
```

Default request timeout is 60 seconds, use the `timeout` argument to override :

```python
sandbox = Sandbox("http://www.my-sandbox.com", timeout=2.5)
```

### Specifications

You can obtain the sandbox' host and container with the `.specifications()` method :

```python
>>> pprint.pp(sandbox.specifications())
{'host': {'cpu': {'core': 6,
                  'logical': 12,
                  'freq_min': 800.0,
                  'freq_max': 4700.0},
          'memory': {'ram': 16723701760,
                     'swap': 9448923136,
                     'storage': {'/dev/sda2': 225603444736,
                                 '/dev/sda1': 313942016,
                                 '/dev/sdc1': 2000396288000}},
          'docker_version': '19.03.8-ce',
          'sandbox_version': '3.0.0'},
 'container': {'count': 20,
               'cpu': {'count': 1, 'period': 1000, 'shares': 1024, 'quota': 0},
               'memory': {'ram': 100000000, 'swap': 100000000, 'storage': -1},
               'io': {'read_iops': {},
                      'read_bps': {},
                      'write_iops': {},
                      'write_bps': {}},
               'process': -1,
               'working_dir_device': '/dev/sda2'}}
```

### Sandbox' Usage

You can obtain the sandbox' usage with the `.usage()` method :

```python
>>> pprint.pp(sandbox.usage())
{'cpu': {'frequency': 800.0504166666668,
         'usage': 0.085,
         'usage_avg': [0.10416666666666667, 0.09000000000000001, 0.0775]},
 'memory': {'ram': 5376819200,
            'swap': 0,
            'storage': {'/dev/sda2': 60275105792,
                        '/dev/sda1': 286720,
                        '/dev/sdc1': 1294363865088}},
 'io': {'read_iops': {'/dev/sdc1': 0, '/dev/sda1': 0, '/dev/sda2': 0},
        'read_bps': {'/dev/sdc1': 0, '/dev/sda1': 0, '/dev/sda2': 0},
        'write_iops': {'/dev/sdc1': 0, '/dev/sda1': 0, '/dev/sda2': 0},
        'write_bps': {'/dev/sdc1': 0, '/dev/sda1': 0, '/dev/sda2': 2048}},
 'network': {'sent_bytes': 514,
             'received_bytes': 526,
             'sent_packets': 6,
             'received_packets': 6},
 'process': 326,
 'container': 0}

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
>>> pprint.pp(sandbox.execute({
     "commands": [
             "echo $((2+2))"
     ]
}))

{'status': 0,
 'execution': [ {'command': 'echo $((2+2))',
                 'exit_code': 0,
                 'stdout': '4',
                 'stderr': '',
                 'time': 0.28589797019958496
        }
    ],
 'total_time': 0.2871053218841553}
```

## Asynchronous API

Since requests may take sometime before a response is available, an asynchronous interface is available
through the class `ASandbox` : 

 ```python
from sandbox_api import ASandbox

sandbox = ASandbox("http://www.my-sandbox.com")
```

`ASandbox` use [*aiohttp*](https://docs.aiohttp.org/en/stable/index.html), so timeout works
differently. The default total timeout is still 60 seconds, but you're able to set differents
timeout for different part of the process with the following arguments :

* `total` : The whole operation time including connection
        establishment, request sending and response reading.
* `connect` : The time consists connection establishment for a new
        connection or waiting for a free connection from a pool if
        pool connection limits are exceeded.
* `sock_connect` : A timeout for connecting to a peer for a new
        connection, not given from a pool.
* `sock_read` : The maximum allowed timeout for period between reading
        a new data portion from a peer.

```python
sandbox = ASandbox("http://www.my-sandbox.com", total=2.5, connect=0.5)
```

All parameters are `floats`. `None` or `0` disables a particular timeout check, see the
[*aiohttp's ClientTimeout*](https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientTimeout)
reference for defaults and additional details.

To send requests, `ASandbox` uses a session that must be closed once done with the instance :

```python
sandbox = ASandbox("http://www.my-sandbox.com", total=2.5, connect=0.5)

# do stuff with sandbox

await sandbox.close()
```

You can also use a context manager to automatically close the session once done :

```python
async with ASandbox("http://www.my-sandbox.com") as sandbox:
    # do stuff with sandbox
```

Apart from the above, all the methods are the same than `Sandbox` but are all declared with the
`async` keyword and must be awaited :

```python
async with ASandbox("http://my-sandbox.com") as sandbox:
    usage, specs, execution = await asyncio.gather(
        sandbox.usage(),
        sandbox.specifications(),
        sandbox.execute({
            "commands": [
                "echo $((2+2))"
            ]
        })
    )
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
