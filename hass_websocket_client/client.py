from asyncio import CancelledError, Event, create_task, sleep
from typing import Union
from websockets import client
import json
from .exceptions import *
from .models import *
from contextlib import asynccontextmanager, AbstractAsyncContextManager
from secrets import token_urlsafe


class HassEventListener:
    def __init__(self, quit_event: Event, client: "HassWS", subscription_id: int):
        self.quit_event = quit_event
        self.client = client
        self.subscription_id = subscription_id

    def __aiter__(self):
        return self

    async def __anext__(self) -> Message[HassEvent]:
        if self.quit_event.is_set():
            raise StopAsyncIteration
        self.client.guard_ready()
        while True:
            task = create_task(self.client.connection.recv())
            while True:
                await sleep(0)
                if task.cancelled():
                    raise StopAsyncIteration
                if task.done():
                    data = Message.create(json.loads(task.result()))
                    if data.id == self.subscription_id:
                        return data.data
                    else:
                        break
                if self.quit_event.is_set():
                    task.cancel()
                    raise StopAsyncIteration

    def quit(self):
        self.quit_event.set()


class HassWS:
    def __init__(self, server: str, token: str) -> None:
        self.server = server
        self.token = token
        self.connection: client.WebSocketClientProtocol = None
        self.message_id: int = 1
        self.meta: Union[HassMeta, None] = None
        self.workers: dict[str, HassWS] = {}

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

        for w in list(self.workers.keys()):
            await self.workers[w].close()
            del self.workers[w]

        self.meta = None

    @property
    def ready(self) -> bool:
        return self.connection and self.connection.open

    def guard_ready(self):
        if not self.ready:
            raise HassException(detail="Connection is closed.")

    async def send_message(self, type: str, ignore_closed: bool = False, **kwargs) -> Message:
        if ignore_closed and not self.ready:
            return
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
    ) -> bool:
        return (
            await self.send_message(
                "call_service",
                domain=domain,
                service=service,
                service_data=data,
                target=target,
            )
        ).success

    async def start_worker_listener(self, type: str = None) -> tuple["HassWS", HassEventListener]:
        worker = await HassWS(self.server, self.token)
        if type:
            subscription_response = await worker.send_message(
                "subscribe_events", event_type=type
            )
        else:
            subscription_response = await worker.send_message("subscribe_events")
        if not subscription_response.success:
            raise HassException(detail="Failed to subscribe to event")
        quit_event = Event()
        listener = HassEventListener(
            quit_event, worker, subscription_response.id)
        return worker, listener

    @asynccontextmanager
    async def listen_event(
        self, type: str = None
    ) -> AbstractAsyncContextManager[HassEventListener]:
        worker, listener = await self.start_worker_listener(type=type)
        worker_id = token_urlsafe()
        self.workers[worker_id] = worker
        try:
            try:
                yield listener
            finally:
                listener.quit()
                await worker.send_message(
                    "unsubscribe_events", subscription=listener.subscription_id, ignore_closed=True
                )
                await self.workers[worker_id].close()
                del self.workers[worker_id]
        except (CancelledError, RuntimeError):
            try:
                listener.quit()
                await worker.send_message(
                    "unsubscribe_events", subscription=listener.subscription_id, ignore_closed=True
                )
                await self.workers[worker_id].close()
                del self.workers[worker_id]
            except:
                pass
            raise CancelledError
