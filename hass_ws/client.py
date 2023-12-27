from typing import Union
from websockets import client
import json
from .exceptions import *
from .models import *


class HassWS:
    def __init__(self, server: str, token: str) -> None:
        self.server = server
        self.token = token
        self.connection: client.WebSocketClientProtocol = None
        self.message_id: int = 1
        self.meta: Union[HassMeta, None] = None

    def __await__(self):
        return self._initialize().__await__()

    async def _initialize(self):
        await self.authenticate()
        return self

    async def authenticate(self):
        if self.connection:
            await self.connection.close()

        try:
            connection = await client.connect(self.server + "/api/websocket")
        except:
            raise HassException(detail="Connection failure.")

        try:
            auth_msg: dict = json.loads(await connection.recv())
        except:
            raise HassException(
                detail="Initial handshake failed, check HASS version info."
            )

        if auth_msg.get("type") != "auth_required":
            raise HassException(detail="Initial handshake failed, bad message format.")

        await connection.send(json.dumps({"type": "auth", "access_token": self.token}))
        try:
            auth_reply: dict = json.loads(await connection.recv())
        except:
            raise HassException(
                detail="Failed to perform authentication (unknown error)"
            )

        if auth_reply.get("type") == "auth_ok":
            self.connection = connection
            self.meta = HassMeta(version=auth_reply["ha_version"], server=self.server)
            self.message_id = 1
        else:
            raise AuthenticationError(
                detail="Failed to authenticate with provided token."
            )

    async def close(self):
        if self.connection:
            await self.connection.close()

        self.meta = None

    @property
    def ready(self) -> bool:
        return self.connection and self.connection.open

    def guard_ready(self):
        if not self.ready:
            raise HassException(detail="Connection is closed.")

    async def send_message(self, type: str, **kwargs) -> Message:
        self.guard_ready()
        await self.connection.send(
            json.dumps(dict(id=self.message_id, type=type, **kwargs))
        )
        self.message_id += 1
        return Message.create(json.loads(await self.connection.recv()))

    async def fetch_states(self) -> Message[list[HassEntity]]:
        return await self.send_message("get_states")

    async def fetch_config(self) -> Message[HassConfig]:
        return await self.send_message("get_config")

    async def fetch_services(self) -> Message[dict[str, dict[str, HassService]]]:
        return await self.send_message("get_services")

    async def fetch_panels(self) -> Message[dict[str, HassPanel]]:
        return await self.send_message("get_panels")

    async def call_service(
        self, domain: str, service: str, target: HassServiceTarget = {}, data: dict = {}
    ):
        return await self.send_message(
            "call_service",
            domain=domain,
            service=service,
            service_data=data,
            target=target,
        )
