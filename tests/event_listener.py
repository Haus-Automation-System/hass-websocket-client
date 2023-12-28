from hass_websocket_client import HassWS
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()


async def test_listener():
    client = await HassWS(os.environ["HASS_SERVER"], os.environ["HASS_TOKEN"])
    async with client.listen_event(type="call_service") as listener:
        c = 0
        async for i in listener:
            if c > 10:
                listener.quit()
                continue
            print(i)
            c += 1

    await client.close()


def main():
    asyncio.run(test_listener())


if __name__ == "__main__":
    main()
