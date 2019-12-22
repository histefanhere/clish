import asyncio
from gateway import DiscordGateway, FacebookGateway

loop = asyncio.new_event_loop()


async def main():
    discord = DiscordGateway()
    fb = FacebookGateway()
    await discord.open()
    await discord.login()
    await discord.start_heartbeat()
    await fb.open()
    try:
        await asyncio.sleep(20)
    finally:
        await fb.close()
        await discord.close()
        exit()


asyncio.run(main())
