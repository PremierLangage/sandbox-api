# sandbox.py
#
# Authors:
#   - Coumes Quentin <coumes.quentin@gmail.com>


import io
import json
import os
from typing import BinaryIO, Optional, Union

import requests

from .exceptions import status_exceptions



class Sandbox:
    """Interface a Sandbox server.
    
    Attribute other than 'url' are retrieved from the sandbox at first access, attribute are
    separated in two categories, specifications and libraries. Every attribute of one category are
    retrieved the first time an attribute of the corresponding category is accessed.
    
    These attributes are fetch through HTTP requests, this can take some times (should be no more
    than seconds), especially for the libraries category.
    
    Note that attributes are cached (except for 'containers'), and subsequent access to one category
    are instantaneous.
    
    Attributes:
        url (str): URL of the sandbox
        
        # Specifications
        sandbox_version (str): Version of the sandbox formatted as 'MAJOR.MINOR.PATCH'.
        docker_version (str): Version of docker used by the sandbox formatted as 'MAJOR.MINOR.PATCH'
        containers (dict): Dict containing the status of the containers running on the sandbox.
        memory (dict): Memory limits for each containers on the sandbox.
        cpu (dict): CPU information for each containers on the sandbox.
        environ (dict): Environments variables use in the containers.
        execute_timeout (Union[int, float]): Time in seconds before an 'execute/' request timeout.
        expiration (int): Time in before an environment expire on the sandbox.
        
        # Libraries
        python3 (str): Version of python3 used by the sandbox formatted as 'MAJOR.MINOR.PATCH'.
        python2 (str): Version of python2 used by the sandbox formatted as 'MAJOR.MINOR.PATCH'.
        java (str): Version of java used by the sandbox formatted as 'JDK MAJOR.MINOR'.
        gcc (str): Version of gcc used by the sandbox formatted as 'MAJOR.MINOR.PATCH'.
        gpp (str): Version of g++ used by the sandbox formatted as 'MAJOR.MINOR.PATCH'.
        perl (str): Version of perl used by the sandbox formatted as 'MAJOR.MINOR.PATCH'.
        postgres (str): Version of postgres used by the sandbox formatted as 'MAJOR.MINOR'.
        libraries (dict): Dict containing :
            system (dict): The installed packages (dpkg).
            c (dict): The installed libraries and their version.
            python (dict): The installed python modules.
            perl (dict): The installed perl modules.
        bin (dict): Every command available in PATH on the sandbox
    """
    
    sandbox_version: str
    sandbox_version: str
    docker_version: str
    containers: dict
    memory: dict
    cpu: dict
    environ: dict
    execute_timeout: Union[int, float]
    expiration: int
    python3: str
    python2: str
    java: str
    gcc: str
    gpp: str
    perl: str
    postgres: str
    libraries: dict
    bin: dict
    
    # Lists of the sandbox's endpoints
    _endpoints = {
        "specs":        "specifications/",
        "libs":         "libraries/",
        "environments": "environments/%s/",
        "files":        "files/%s/%s/",
        "execute":      "execute/",
    }
    
    # Lists of fields in the specs endpoint's response
    _specs = [
        "sandbox_version",
        "docker_version",
        "containers",
        "cpu",
        "memory",
        "environ",
        "execute_timeout",
        "expiration",
    ]
    
    # Lists of fields in the libs endpoint's response
    _libs = [
        "python3",
        "python2",
        "java",
        "gcc",
        "gpp",
        "perl",
        "postgres",
        "libraries",
        "bin",
    ]
    
    
    def __init__(self, url: str):
        self.url = url
        
        for prop in self._specs + self._libs:
            setattr(self.__class__, prop, self._property(prop))
    
    
    @staticmethod
    def _property(attribute: str):
        """Wraps specification's and libraries' attribute to be fetch from the Sandbox at first
        access.
        
        'containers' attribute is also refreshed every time."""
        
        
        def getter(self):
            if attribute == "containers":
                self._fetch("specs")
            
            elif not hasattr(self, "_" + attribute):
                if attribute in self._libs:
                    self._fetch("libs")
                else:
                    self._fetch("specs")
            
            return getattr(self, "_" + attribute)
        
        
        def setter(self, value):
            setattr(self, "_" + attribute, value)
        
        
        def deleter(self):
            delattr(self, "_" + attribute)
        
        
        if attribute == "containers":
            docstring = "Fetch containers from the sandbox."
        else:
            docstring = "Fetch %s from the sandbox the first time it is accessed." % attribute
        
        return property(getter, setter, deleter, docstring)
    
    
    def _build_url(self, endpoint: str, *args: str):
        """Build the url corresponding to <endpoint> with the given <args>."""
        return os.path.join(self.url, self._endpoints[endpoint] % tuple(args))
    
    
    def _fetch(self, endpoint: str):
        """Retrieve the json of <endpoint> and set attributes of self according to the json."""
        response = requests.get(self._build_url(endpoint))
        if response.status_code != 200:
            raise status_exceptions(response)
        
        for k, v in response.json().items():
            if k == "g++":
                k = "gpp"
            setattr(self, "_" + k, v)
    
    
    def usage(self) -> float:
        """Returns a float between 0 and 1, indicating the current charge on the sandbox.
        
        0 means that the sandbox is currently unused, 1 means that it is used a full capacity and
        an 'execute/' request will probably be delayed."""
        return self.containers["running"] / self.containers["total"]
    
    
    def download(self, uuid: str, path=None) -> BinaryIO:
        """Download an environment or a specific file inside an environment."""
        if path is None:
            url = self._build_url("environments", uuid)
        else:
            url = self._build_url("files", uuid, path)
        
        response = requests.get(url)
        if response.status_code != 200:
            raise status_exceptions(response)
        
        return io.BytesIO(response.content)
    
    
    def execute(self, config: Union[dict], environ: Optional[BinaryIO] = None) -> dict:
        """Execute commands on the sandbox according to <config> and <environment>, returning
        the response's json as a dict."""
        files = {"environment": environ} if environ is not None else None
        response = requests.post(
            self._build_url("execute"),
            data={"config": json.dumps(config)},
            files=files
        )
        if response.status_code != 200:
            raise status_exceptions(response)
        
        return response.json()
