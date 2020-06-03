# asandbox.py
#
# Authors:
#   - Coumes Quentin <coumes.quentin@gmail.com>


"""An asynchronous implementation of the Sandbox API."""

import io
import json
import os
from contextlib import AbstractAsyncContextManager
from typing import BinaryIO, Optional, Union

import aiohttp

from .exceptions import status_exceptions
from .utils import ENDPOINTS


class ASandbox(AbstractAsyncContextManager):
    """Interface a Sandbox server asynchronously."""
    
    
    def __init__(self, url: str, total: Optional[float] = 60, connect: Optional[float] = None,
                 sock_connect: Optional[float] = None, sock_read: Optional[float] = None):
        """Initialize a sandbox with the given URL.
        
        Default timeout for the whole operation is one minute, use the following
        argument to override :
            
            * total : The whole operation time including connection
                    establishment, request sending and response reading.
            * connect : The time consists connection establishment for a new
                    connection or waiting for a free connection from a pool if
                    pool connection limits are exceeded.
            * sock_connect : A timeout for connecting to a peer for a new
                    connection, not given from a pool.
            * sock_read : The maximum allowed timeout for period between reading
                    a new data portion from a peer.
        """
        self.url = url
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total, connect, sock_connect, sock_read)
        )
    
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    
    async def close(self):
        """Close the aiohttp ClientSession."""
        await self.session.close()
    
    
    async def _build_url(self, endpoint: str, *args: str):
        """Build the url corresponding to <endpoint> with the given <args>."""
        return os.path.join(self.url, ENDPOINTS[endpoint] % tuple(args))
    
    
    async def libraries(self) -> dict:
        """Asynchronously retrieve libraries installed in the containers of the
        sandbox."""
        async with self.session.get(await self._build_url("libraries")) as response:
            if response.status != 200:
                raise status_exceptions(response)
            
            return await response.json()
    
    
    async def specifications(self) -> dict:
        """Asynchronously retrieve specifications of the sandbox."""
        async with self.session.get(await self._build_url("specifications")) as response:
            if response.status != 200:
                raise status_exceptions(response)
            
            return await response.json()
    
    
    async def usage(self) -> dict:
        """Asynchronously retrieve current usage stats of the sandbox."""
        async with self.session.get(await self._build_url("usages")) as response:
            if response.status != 200:
                raise status_exceptions(response)
            
            return await response.json()
    
    
    async def download(self, uuid: str, path: str = None) -> BinaryIO:
        """Asynchronously download an environment or a specific file inside an
        environment."""
        if path is None:
            url = await self._build_url("environments", uuid)
        else:
            url = await self._build_url("files", uuid, path)
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise status_exceptions(response)
            
            return io.BytesIO(await response.read())
    
    
    async def check(self, uuid: str, path: str = None) -> int:
        """Asynchronously check if an environment or a specific file inside an
        environment exists."""
        if path is None:
            url = await self._build_url("environments", uuid)
        else:
            url = await self._build_url("files", uuid, path)
        
        async with self.session.head(url) as response:
            if response.status not in [200, 404]:  # pragma: no cover
                raise status_exceptions(response)

            return 0 if response.status == 404 else response.headers["Content-Length"]
    
    
    async def execute(self, config: Union[dict], environ: Optional[BinaryIO] = None) -> dict:
        """Asynchronously execute commands on the sandbox according to <config>
        and <environ>, returning the response's json as a dict.
        
        <environ>, if not None, will be consumed and closed and shall not be
        used further."""
        data = aiohttp.FormData()
        data.add_field("config", json.dumps(config))
        if environ is not None:
            data.add_field("environment", environ)
        
        async with self.session.post(await self._build_url("execute"), data=data) as response:
            if response.status != 200:
                raise status_exceptions(response)
            
            return await response.json()
