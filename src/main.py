import asyncio
from gateway import DiscordGateway, FacebookGateway
from console import *

loop = asyncio.new_event_loop()


async def main():
    discord = DiscordGateway()
    fb = FacebookGateway()
    await discord.open()
    await discord.login()
    await discord.start_heartbeat()
    await fb.open()
    try:
        await asyncio.sleep(10)
    finally:
        await discord.close()
        exit()


asyncio.run(main())
