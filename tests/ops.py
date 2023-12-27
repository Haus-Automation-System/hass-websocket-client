from hass_ws import HassWS
from dotenv import load_dotenv
import os
import asyncio
import json

load_dotenv()


async def test_get_states(client: HassWS):
    with open("states.out.json", "w") as f:
        result = await client.fetch_states()
        if result.success:
            print(json.dumps(result.data, indent=4), file=f)


async def test_get_config(client: HassWS):
    with open("config.out.json", "w") as f:
        result = await client.fetch_config()
        if result.success:
            print(json.dumps(result.data, indent=4), file=f)


async def test_get_services(client: HassWS):
    with open("services.out.json", "w") as f:
        result = await client.fetch_services()
        if result.success:
            print(json.dumps(result.data, indent=4), file=f)


async def test_get_panels(client: HassWS):
    with open("panels.out.json", "w") as f:
        result = await client.fetch_panels()
        if result.success:
            print(json.dumps(result.data, indent=4), file=f)


async def test_ops():
    client = await HassWS(os.environ["HASS_SERVER"], os.environ["HASS_TOKEN"])
    print(client.meta)

    await test_get_states(client)
    await test_get_config(client)
    await test_get_services(client)
    await test_get_panels(client)

    await client.close()


def main():
    asyncio.run(test_ops())


if __name__ == "__main__":
    main()
