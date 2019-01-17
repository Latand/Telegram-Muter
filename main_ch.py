from user_class import get_client
from telethon.events import NewMessage
from telethon import events
from config import *
import logging
import asyncio
from sql_class import sql

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)

u = get_client(phone=PHONE_NUMBER, password=AUTH_PASSWORD)

channels = set([x["id"] for x in sql.select(where="channels")])


@u.client.on(events.NewMessage(outgoing=True,
                               pattern='!unmute'))
async def admin_handler(event):
    await u.client.delete_messages(await event.get_input_chat(), message_ids=event.message.id)

    chat = await u.client.get_entity(await event.get_input_chat())
    logging.debug(f"{chat.to_dict()}")
    try:
        sql.delete(table="channels", where=['id'], what=[chat.id])
        channels.remove(chat.id)
        if chat.__class__.__name__ == "Channel":
            name = chat.title
        elif chat.__class__.__name__ == "User":

            name = f'{chat.first_name} {chat.last_name}'

        try:
            await u.send_message(message=f'{name} Unmuted')
        except Exception as err:
            logging.error(f"{err}")
    except Exception as err:

        await u.send_message(message=f"{err.__class__.__name__}: {err}")
        logging.error(f"{err.__class__.__name__}: {err}")


@u.client.on(events.NewMessage(outgoing=True,
                               pattern='!mute'))
async def admin_handler(event):
    await u.client.delete_messages(await event.get_input_chat(), message_ids=event.message.id)

    chat = await u.client.get_entity(await event.get_input_chat())
    logging.debug(f"{chat.to_dict()}")
    sql.insert(table="channels", id=chat.id)
    channels.add(chat.id)
    if chat.__class__.__name__ == "Channel":
        name = chat.title
    elif chat.__class__.__name__ == "User":

        name = f'{chat.first_name} {chat.last_name}'
    try:
        await u.send_message(message=f'{name} Muted')
    except Exception as err:
        logging.error(f"{err}")


@u.client.on(events.NewMessage(incoming=True,
                               chats=channels))
async def my_event_handler(event: NewMessage):
    event.message.message: str
    print(await u.client.send_read_acknowledge(await event.get_input_chat()))


loop = asyncio.get_event_loop()

u.client.start()
loop.create_task(u.get_info())
u.client.run_until_disconnected()
