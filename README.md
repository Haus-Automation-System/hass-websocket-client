# hass-client
Home Assistant async API wrapper

## API Documentation

**Example Usage:**

```python
from hass_ws import HassWS

async def main():
    client = async HassWS("wss://server.hass", "token")

    print(await client.fetch_states()) # Displays all HASS states
    print(await client.call_service("light", "turn_on")) # Turns on all lights
    async with client.listen_event(type="call_service") as listener:
        async for i in listener:
            print(i)

    await client.close()
```
