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
    """Interface a Sandbox server."""
    
    # Lists of the sandbox's endpoints
    _endpoints = {
        "specifications": "specifications/",
        "libraries":      "libraries/",
        "usages":         "usages/",
        "environments":   "environments/%s/",
        "files":          "files/%s/%s/",
        "execute":        "execute/",
    }
    
    
    def __init__(self, url: str):
        self.url = url
    
    
    def _build_url(self, endpoint: str, *args: str):
        """Build the url corresponding to <endpoint> with the given <args>."""
        return os.path.join(self.url, self._endpoints[endpoint] % tuple(args))
    
    
    def libraries(self) -> dict:
        """Retrieve libraries installed in the containers of the sandbox."""
        response = requests.get(self._build_url("libraries"))
        if response.status_code != 200:
            raise status_exceptions(response)
        
        return response.json()
    
    
    def specifications(self) -> dict:
        """Retrieve specifications of the sandbox."""
        response = requests.get(self._build_url("specifications"))
        if response.status_code != 200:
            raise status_exceptions(response)
        
        return response.json()
    
    
    def usage(self) -> dict:
        """Retrieve current usage stats of the sandbox."""
        response = requests.get(self._build_url("usages"))
        if response.status_code != 200:
            raise status_exceptions(response)
        
        return response.json()
    
    
    def download(self, uuid: str, path: str = None) -> BinaryIO:
        """Download an environment or a specific file inside an environment."""
        if path is None:
            url = self._build_url("environments", uuid)
        else:
            url = self._build_url("files", uuid, path)
        
        response = requests.get(url)
        if response.status_code != 200:
            raise status_exceptions(response)
        
        return io.BytesIO(response.content)
    
    
    def check(self, uuid: str, path: str = None) -> bool:
        """Check if an environment or a specific file inside an environment exists."""
        if path is None:
            url = self._build_url("environments", uuid)
        else:
            url = self._build_url("files", uuid, path)
        
        response = requests.head(url)
        if response.status_code not in [200, 404]:  # pragma: no cover
            raise status_exceptions(response)
        
        return response.status_code == 200
    
    
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
