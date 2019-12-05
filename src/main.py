import asyncio
from gateway import DiscordGateway

loop = asyncio.new_event_loop()


async def constant_update(func):
    while True:
        await func()
        await asyncio.sleep(3, loop=loop)


async def main():
    discord = DiscordGateway()
    await discord.open()
    await discord.login()
    await discord.start_heartbeat()
    try:
        await asyncio.sleep(10)
    finally:
        await discord.close()
        exit()

asyncio.run(main())
