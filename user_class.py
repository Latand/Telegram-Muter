from telethon import TelegramClient
import socks
import logging
from config import API_HASH, API_ID, PROXY


def proxy(data: str):
    """
    If you need proxy, example data = '123.456.789:1234:login:pass'
    """
    if not data:
        return None
    data = data.split(":")
    if len(data) == 4:
        host, port, login, passw = data
        return socks.SOCKS5, host, int(port), True, login, passw
    elif len(data) == 2:

        host, port = data
        return socks.SOCKS5, host, int(port), True


class User(object):
    def __init__(self, phone, proxy_data=PROXY, password=None):
        self.client: TelegramClient = TelegramClient(str(phone), API_ID, API_HASH, proxy=proxy(proxy_data))

        self.client.start(phone=phone, password=password)

        self.me = None

        self.first_name = None
        self.chat_id = None

    async def get_info(self):

        self.me = await self.client.get_me()

        self.first_name = self.me.first_name
        self.chat_id = self.me.id

        logging.info(f"Created user: {self.first_name}")

    async def send_message(self, username=None, message=None, **kwargs):  # quick send
        if not message:
            message = "Ммм..."
        if not username:
            username = "self"
        await self.client.send_message(username, str(message), **kwargs)


def get_client(phone, proxy=None, password=None) -> User:  # upload client
    try:
        logging.info(f"trying number {phone}, {proxy}")
        client = User(phone, proxy, password=password)
        return client
    except ConnectionError:
        logging.info("Lost connection to telegram")
