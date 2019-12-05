import websockets
import asyncio
import json


class BaseGateway:

    def __init__(self):
        self.connected = False

    def refresh(self):
        pass

    def open(self):
        pass

    def close(self):
        pass


class APIGateway(BaseGateway):

    def __init__(self):
        super(APIGateway, self).__init__()
        self.token = None

    def refresh(self):
        pass

    def open(self):
        pass

    def close(self):
        pass


class WebsocketAPIGateway(APIGateway):

    def __init__(self):
        super(APIGateway, self).__init__()
        self.connection = None

    def refresh(self):
        pass

    def open(self):
        pass

    def close(self):
        pass


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
        self.token = "NTUzODc2MzA0NDIwNjY3Mzky.D2UdAQ._ABnKKMRzGyn9aHrJoA7E5Hd1ZU"
        self.heartbeak_interval = None
        self._ready = False
        self.loop = asyncio.get_event_loop()
        self.dispatch_map = {
            "READY": self.ready
        }

    async def open(self):
        self.connection = await websockets.connect("wss://gateway.discord.gg/?v=6&encoding=json")
        response = json.loads(await self.connection.recv())
        if response["op"] == self.HELLO:
            print("opened connection to discord", response)
        self.heartbeak_interval = response["d"]["heartbeat_interval"]
        self.loop.create_task(self.accept_dispatch())

    async def send_raw(self, data):
        await self.connection.send(data)

    async def send(self, op, s=None, t=None, d=None):
        print("sent packet")
        await self.send_raw(json.dumps(dict(op=op, s=s, t=t, d=d)))

    async def accept_dispatch(self):
        while True:
            response = await self.connection.recv()
            response = json.loads(response)
            if (response["op"] == self.DISPATCH):
                await self.dispatch_map[response['t']](response)
            else:
                print(response)

    async def heartbeat(self):
        while True:
            await self.send(op=self.HEARTBEAT)
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
        await self.connection.close()

    @classmethod
    def sample_hearbeat(cls):
        return json.dumps(dict(op=cls.HEARTBEAT))

    async def ready(self, response):
        print(f"logged in as {response['d']['user']['username']}#{response['d']['user']['discriminator']}")
