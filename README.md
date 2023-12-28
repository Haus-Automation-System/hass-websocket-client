# hass-client
Home Assistant async API wrapper

## API Documentation

**Example Usage:**

```python
from hass_ws import HassWS

async def main():
    client = await HassWS("wss://server.hass", "token")

    print(await client.fetch_states()) # Displays all HASS states
    print(await client.call_service("light", "turn_on")) # Turns on all lights
    async with client.listen_event(type="call_service") as listener:
        async for i in listener:
            print(i)

    await client.close()
```

### HassWS Interface:

```python
await HassWS(server: str, token: str)
```
- `server`: Required, str. Base server URL of HASS instance, including `wss://` or `ws://` protocol specifier.
- `token`: Required, str. Long-lived HASS access token.

**Properties/Members:**

- `HassWS().ready`: Boolean value, `True` if the client is ready to send commands.
- `HassWS().meta`: `HassMeta`, server metadata. `None` if not connected.

**Methods:**

- `await HassWS().close()`: Closes the currently active connection. To reconnect, call `await HassWS().authenticate()`
- `await HassWS().fetch_states() -> HassEntity[]`: Returns current states of all entities.
- `await HassWS().fetch_config() -> HassConfig`: Returns current server config
- `await HassWS().fetch_services() -> {domain: {service: HassService}}`: Returns all available services
- `await HassWS().fetch_panels() -> {name: HassPanel}`: Returns all UI panels
- `await HassWS().call_service(domain: str, service: str, target: HassServiceTarget = {}, data: dict = {}) -> bool`: Calls a service, returning boolean success value.
- `async with HassWS().listen_event(type: str = None) -> AsyncIterator`: Subscribes to an event (or all events, if `type = None`), and returns an asynchronous iterator for them.

