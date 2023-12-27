from hass_client import HassWS
from dotenv import load_dotenv
import os
import asyncio
import json

load_dotenv()


async def test_get_states(client: HassWS):
    states = await client.states()
    if states.success:
        print(json.dumps(states.data, indent=4))


async def test_ops():
    client = await HassWS(os.environ["HASS_SERVER"], os.environ["HASS_TOKEN"])
    print(client.meta)

    await test_get_states(client)

    await client.close()


def main():
    asyncio.run(test_ops())


if __name__ == "__main__":
    main()
