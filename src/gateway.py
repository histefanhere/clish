import websockets
import requests
import aiohttp
import asyncio
import json
import time
import bs4
import datetime
import arrow

from constants import errors
AbstractMethodNotImplementedError = errors.AbstractMethodNotImplementedError

class BaseGateway:

    def __init__(self):
        self.connected = False
        self.print = print

    def refresh(self):
        raise AbstractMethodNotImplementedError

    def open(self):
        raise AbstractMethodNotImplementedError

    def login(self):
        raise AbstractMethodNotImplementedError

    def close(self):
        raise AbstractMethodNotImplementedError  # future plugins will work by subclassing these functions.


class OtherGateway(BaseGateway):

    def __init__(self):
        super().__init__()
        self.email = None
        self.password = None
        self.cookie = None


class FacebookGateway(OtherGateway):

    def __init__(self):
        super().__init__()
        self.email = "censored"
        self.password = "ThisIsABot"
        self.session = aiohttp.ClientSession()
        self.chats = {}

    @staticmethod
    def find_input_fields(html):
        return bs4.BeautifulSoup(html, "html.parser", parse_only=bs4.SoupStrainer("input"))

    @staticmethod
    def to_soup(html):
        return bs4.BeautifulSoup(html, "html.parser")

    async def open(self):
        if not self.password and not self.email and not self.cookie:
            raise RuntimeError("no credentials for facebook")

        if self.cookie:
            return

        await self.login()

    async def login(self):

        r1 = await self.session.get("https://m.facebook.com/")
        soup = self.find_input_fields(await r1.text())
        data = dict(
            (elem["name"], elem["value"])
            for elem in soup
            if elem.has_attr("value") and elem.has_attr("name")
        )
        data["email"] = self.email
        data["pass"] = self.password
        data["login"] = "Log In"

        r = await self.session.post("https://m.facebook.com/login.php", data=data)

        if "save-device" in str(r.url):
            r = await self.session.get("https://m.facebook.com/login/save-device/cancel/")
            r = await self.session.get("https://m.facebook.com/home.php")

        if "https://m.facebook.com/home.php" in str(r.url):
            homepage = self.to_soup(await r.text())
            for link in homepage.find_all("a"):
                if link.string == "Photos":
                    parts = link.attrs["href"].split(".")
                    print(f"logged in as {parts[0].replace('/', '').capitalize()} {parts[1].capitalize()}")

            chats = await self.session.get("https://m.facebook.com/messages")
            chat_soup = self.to_soup(await chats.text())
            for link in chat_soup.find_all("a"):
                try:
                    if link.attrs["href"].startswith("/messages/read"):
                        self.chats.update({f"{link.contents[0]}": link.attrs["href"]})
                except:
                    pass
            # print(self.chats)
        else:
            print("facebook login failed")

    def get_convos(self):
        pass

    async def close(self):
        await self.session.close()


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
        self.token = "censored"  # plz dont fuck with my self bot
        self.heartbeak_interval = None
        self._ready = False
        self.loop = asyncio.get_event_loop()
        self.dispatch_map = {
            "READY": self.ready,
            "MESSAGE_CREATE": self.on_message
        }
        self.last_seq = 0
        self.last_ping = 0

    async def open(self):
        self.connection = await websockets.connect("wss://gateway.discord.gg/?v=6&encoding=json")
        response = json.loads(await self.connection.recv())
        if response["op"] == self.HELLO:
            pass
            # print("opened connection to discord", response)
        else:
            raise RuntimeError("failed to connect to discord")
        self.heartbeak_interval = response["d"]["heartbeat_interval"]
        self.connected = True
        self.loop.create_task(self.accept_dispatch())

    async def send_raw(self, data):
        await self.connection.send(data)

    async def send(self, op, s=None, t=None, d=None):
        # print("sent packet")
        await self.send_raw(json.dumps(dict(op=op, s=s, t=t, d=d)))

    async def accept_dispatch(self):  # this function runs in its own thread and handles all incoming events
        while True and self.connected:
            try:
                response = await self.connection.recv()
            except websockets.exceptions.ConnectionClosed:
                return
            response = json.loads(response)
            self.last_seq = response["s"]
            # print(response)
            if response["t"] and response["t"] not in list(self.dispatch_map.keys()):
                pass
                # print(response)
            elif response["op"] == self.HEARTBEAT_ACK:
                self.last_ping = time.time()  # heartbeat ACKNOWLEDGED, however, this is handled somewhere else
            elif response["op"] == self.DISPATCH:
                await self.dispatch_map[response['t']](response)
            else:
                print(response)  # something unhandled

    async def heartbeat(self):  # this function runs in its own thread and makes sure we stay connected to discord
        while True:
            await self.send(op=self.HEARTBEAT, d=self.last_seq)
            st = time.time()
            stv = self.last_ping
            while self.last_ping == stv:
                await asyncio.sleep(0.000001, loop=self.loop)
                # print("waiting")
            print(f"latency: {round((self.last_ping - st) * 1000)}ms")
            await asyncio.sleep(self.heartbeak_interval / 1000, loop=self.loop)

    async def start_heartbeat(self):
        self.loop.create_task(self.heartbeat())
        # self.loop.run_forever()

    async def login(self):
        login_str = {
            "token": self.token,
            "properties": {
                "$os": "windows",
                "$browser": None,
                "$device": "CLISH"
            },
            "presence": {
                "game": {
                    "name": "Custom Status",
                    "state": "look its a custom status!",
                    "emoji": ":eye:",
                    "type": 4
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
        self.last_seq = 1

    async def on_message(self, response):
        self.print(f"{arrow.get(response['d']['timestamp']).datetime.astimezone(datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo).strftime('%H:%M:%S')}: " +
                   f"<@{response['d']['author']['username']}> {response['d']['content']}")
