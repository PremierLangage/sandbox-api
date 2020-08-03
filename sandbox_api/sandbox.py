# sandbox.py
#
# Authors:
#   - Coumes Quentin <coumes.quentin@gmail.com>


"""A synchronous implementation of the Sandbox API."""

import io
import json
import os
from typing import BinaryIO, Optional, Union

import requests

from .exceptions import status_exceptions
from .utils import ENDPOINTS


class Sandbox:
    """Interface a Sandbox server."""
    
    
    def __init__(self, url: str, timeout: Optional[float] = 60):
        """Initialize a sandbox with the given URL.
        
        Default timeout for waiting a response is one minute, use the <timeout>
        argument to override."""
        self.url = url
        self.timeout = timeout
    
    
    def _build_url(self, endpoint: str, *args: str):
        """Build the url corresponding to <endpoint> with the given <args>."""
        return os.path.join(self.url, ENDPOINTS[endpoint] % tuple(args))
    
    
    def libraries(self) -> dict:
        """Retrieve libraries installed in the containers of the sandbox."""
        response = requests.get(self._build_url("libraries"), timeout=self.timeout)
        if response.status_code != 200:
            raise status_exceptions(response)
        
        return response.json()
    
    
    def specifications(self) -> dict:
        """Retrieve specifications of the sandbox."""
        response = requests.get(self._build_url("specifications"), timeout=self.timeout)
        if response.status_code != 200:
            raise status_exceptions(response)
        
        return response.json()
    
    
    def usage(self) -> dict:
        """Retrieve current usage stats of the sandbox."""
        response = requests.get(self._build_url("usages"), timeout=self.timeout)
        if response.status_code != 200:
            raise status_exceptions(response)
        
        return response.json()
    
    
    def download(self, uuid: str, path: str = None) -> BinaryIO:
        """Download an environment or a specific file inside an environment."""
        if path is None:
            url = self._build_url("environments", uuid)
        else:
            url = self._build_url("files", uuid, path)
        
        response = requests.get(url, timeout=self.timeout)
        if response.status_code != 200:
            raise status_exceptions(response)
        
        return io.BytesIO(response.content)
    
    
    def check(self, uuid: str, path: str = None) -> int:
        """Return the size of an environment or a specific file, 0 if it was not
        found.
        
        Can be used to check if an environment or a specific file inside an
        environment exists."""
        if path is None:
            url = self._build_url("environments", uuid)
        else:
            url = self._build_url("files", uuid, path)
        
        response = requests.head(url, timeout=self.timeout)
        if response.status_code not in [200, 404]:  # pragma: no cover
            raise status_exceptions(response)
        
        return 0 if response.status_code == 404 else response.headers["Content-Length"]
    
    
    def execute(self, config: Union[dict], environ: Optional[BinaryIO] = None) -> dict:
        """Execute commands on the sandbox according to <config> and
        <environ>, returning the response's json as a dict.
        
        <environ>, if not None, will be consumed and closed and shall not be
        used further."""
        files = {"environment": environ} if environ is not None else None
        response = requests.post(
            self._build_url("execute"), data={"config": json.dumps(config)}, files=files,
            timeout=self.timeout
        )
        if response.status_code != 200:
            raise status_exceptions(response)
        
        return response.json()
