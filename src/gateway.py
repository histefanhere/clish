import websockets
import asyncio
import json
import time
import datetime
from dateutil import tz
import arrow
from console import *


class AbstractMethodNotImplementedError(Exception):
    pass


class BaseGateway:

    def __init__(self):
        self.connected = False
        self.print = print

    def refresh(self):
        raise AbstractMethodNotImplementedError

    def open(self):
        raise AbstractMethodNotImplementedError

    def close(self):
        raise AbstractMethodNotImplementedError  # future plugins will work by subclassing these functions.


class RequestGateway(BaseGateway):
    pass


class APIGateway(BaseGateway):

    def __init__(self):
        super(APIGateway, self).__init__()
        self.token = None


class WebsocketAPIGateway(APIGateway):

    def __init__(self):
        super(APIGateway, self).__init__()
        self.connection = None


class DiscordGateway(WebsocketAPIGateway):
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    PRESENCE = 3
    VOICE_STATE = 4
    VOICE_PING = 5
    RESUME = 6
    RECONNECT = 7
    REQUEST_MEMBERS = 8
    INVALIDATE_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11
    GUILD_SYNC = 12

    def __init__(self):
        super(WebsocketAPIGateway, self).__init__()
        self.token = "NTUzODc2MzA0NDIwNjY3Mzky.D2UdAQ._ABnKKMRzGyn9aHrJoA7E5Hd1ZU"  # plz dont fuck with my self bot
        self.heartbeak_interval = None
        self._ready = False
        self.loop = asyncio.get_event_loop()
        self.dispatch_map = {
            "READY": self.ready,
            "MESSAGE_CREATE": self.on_message
        }
        self.last_seq = 0

    async def open(self):
        self.connection = await websockets.connect("wss://gateway.discord.gg/?v=6&encoding=json")
        response = json.loads(await self.connection.recv())
        if response["op"] == self.HELLO:
            print("opened connection to discord", response)
        self.heartbeak_interval = response["d"]["heartbeat_interval"]
        self.connected = True
        self.loop.create_task(self.accept_dispatch())

    async def send_raw(self, data):
        await self.connection.send(data)

    async def send(self, op, s=None, t=None, d=None):
        print("sent packet")
        await self.send_raw(json.dumps(dict(op=op, s=s, t=t, d=d)))

    async def accept_dispatch(self):
        while True and self.connected:
            try:
                response = await self.connection.recv()
            except websockets.exceptions.ConnectionClosed:
                return
            response = json.loads(response)
            self.last_seq = response["s"]
            if response["t"] not in list(self.dispatch_map.keys()):
                pass
                # print(response)
            elif response["op"] == self.HEARTBEAT_ACK:
                pass  # heartbeat ACKNOWLEDGED
            elif response["op"] == self.DISPATCH:
                await self.dispatch_map[response['t']](response)
            else:
                print(response)

    async def heartbeat(self):
        while True:
            await self.send(op=self.HEARTBEAT, d=self.last_seq)
            st = time.time()
            await self.connection.recv()
            print(f"latency: {round((time.time() - st) * 1000)}ms")
            await asyncio.sleep(self.heartbeak_interval / 1000, loop=self.loop)

    async def start_heartbeat(self):
        self.loop.create_task(self.heartbeat())
        # self.loop.run_forever()

    async def login(self):
        login_str = {
            "token": self.token,
            "properties": {
                "$os": "windows",
                "$browser": "chrome",
                "$device": "disco"
            },
            "presence": {
                "game": {
                    "name": "Cards Against Humanity",
                    "type": 0
                },
            }
        }
        await self.send(op=self.IDENTIFY, d=login_str)
        # print(await self.connection.recv())

    async def close(self):
        self._ready, self.connected = False, False
        await self.connection.close()
        exit()

    @classmethod
    def sample_heartbeat(cls):
        return json.dumps(dict(op=cls.HEARTBEAT))  # can be removed

    ## EVENT HANDLERS ##

    async def ready(self, response):
        self.print(f"logged in as {response['d']['user']['username']}#{response['d']['user']['discriminator']}")

    async def on_message(self, response):
        self.print(f"{arrow.get(response['d']['timestamp']).datetime.astimezone(tz.tzlocal()).strftime('%H:%M:%S')}: " +
                   f"<@{response['d']['author']['username']}> {response['d']['content']}")
