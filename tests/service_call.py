from hass_ws import HassWS
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()


async def test_toggle_light():
    client = await HassWS(os.environ["HASS_SERVER"], os.environ["HASS_TOKEN"])

    await client.call_service(
        "light", "toggle", target={"entity_id": "light.room_lights"}
    )
    await client.close()


def main():
    asyncio.run(test_toggle_light())


if __name__ == "__main__":
    main()
