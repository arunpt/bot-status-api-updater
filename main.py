import os
import time
import asyncio
import logging
from telethon import TelegramClient
from telethon.sessions import StringSession
from aiohttp import ClientSession

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("telethon").setLevel(logging.WARNING)  # idc
logger = logging.getLogger(__name__)

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")
BOTS = [b.strip() for b in os.getenv("BOTS").split(",")]
API_KEY = os.getenv("API_KEY")
ENDPOINT = os.getenv("ENDPOINT")
TIMEOUT = 20


async def update_data(username, response, status):
    async with ClientSession() as session:
        async with session.post(ENDPOINT, json={
            "username": username, "ping": response, "status": status
        }, headers={"x-api-key": API_KEY}) as res:
            await res.json()  # why?


async def main(client: TelegramClient):
    async with client as user:
        for bot in BOTS:
            res = 0
            status = False
            async with user.conversation(bot, exclusive=False) as conv:
                logger.info(f"pinging {bot}")
                try:
                    await conv.send_message('/start')
                    then = time.time()
                    reply = await conv.get_response(timeout=TIMEOUT)
                    res = round(time.time() - then, 2)
                    await reply.mark_read()
                except asyncio.TimeoutError:
                    res = 968  # bgmi
                    logger.warning(f"no response from {bot} even after {TIMEOUT} seconds")
                else:
                    status = True
                    logger.info(f"{bot} responded in {res} ms")
                finally:
                    logger.info("updating database")
                    await update_data(bot, res, status)


if __name__ == "__main__":
    client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main(client))
