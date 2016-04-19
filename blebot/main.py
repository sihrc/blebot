#https://discordapp.com/oauth2/authorize?&client_id=170000479709822976&scope=bot

import os, re

import asyncio
from psycopg2 import OperationalError

from .client import client
from .commands import handle_command, initialize
from .utils.error import BlebotError
from .schema import create_database

PATTERN = re.compile(r"/([a-z]*)\s*([^\s]*)\s*(.*)")

@client.event
@asyncio.coroutine
def on_ready():
    print('Connected!')
    print('Username: ' + client.user.name)
    print('ID: ' + client.user.id)

@client.event
@asyncio.coroutine
def on_message(message):
    text = message.content
    if not text.startswith("/"):
        raise StopIteration
    try:
        results = PATTERN.match(text)
        if results:
            command = results.group(1)
            action = results.group(2)
            args = results.group(3)
            yields, result = handle_command(command, action, args, message)
            for future in yields:
                yield from future
            if result:
                yield from client.send_message(message.channel, result)

    except BlebotError as e:
        yield from client.send_message(message.channel, e)
    except OperationalError as f:
        if "database" in f.message and "does not exist" in f.message:
            create_database(message.server.id)
        on_message(message)
    except Exception as e:
        import traceback; traceback.print_exc()
        yield from client.send_message(message.channel, "\nEncountered an interal server error:\n{error}".format(
            error=e
        ))
    # finally:
    #     yield from client.delete_message(message)

@client.event
@asyncio.coroutine
def on_server_join(server):
    create_database(server.id)

@client.event
@asyncio.coroutine
def on_server_available(server):
    create_database(server.id)

@client.event
@asyncio.coroutine
def on_server_join(server):
    create_database(server.id)

if __name__ == "__main__":
    initialize()
    client.run(os.getenv("DISCORD_ACCESS_TOKEN"))
