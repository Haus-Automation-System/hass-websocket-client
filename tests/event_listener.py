from hass_websocket_client import HassWS
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()


async def test_listener(client: HassWS):
    async with client.listen_event(type="call_service") as listener:
        c = 0
        async for i in listener:
            if c > 10:
                listener.quit()
                continue
            print(i)
            c += 1

    await client.close()


async def test_background_listener():
    client = await HassWS(os.environ["HASS_SERVER"], os.environ["HASS_TOKEN"])
    task = asyncio.create_task(test_listener(client))
    for i in range(5):
        await asyncio.sleep(3)
        print(await client.fetch_config())

    task.cancel()



def main():
    asyncio.run(test_background_listener())


if __name__ == "__main__":
    main()
