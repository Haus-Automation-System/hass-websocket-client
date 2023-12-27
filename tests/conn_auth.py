from hass_ws import HassWS
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()


async def test_connection_auth():
    client = await HassWS(os.environ["HASS_SERVER"], os.environ["HASS_TOKEN"])
    print(client.meta)


def main():
    asyncio.run(test_connection_auth())


if __name__ == "__main__":
    main()
