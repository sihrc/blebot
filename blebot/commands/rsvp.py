import traceback, re

import datetime
import dateutil.parser
from sqlalchemy import and_

from ..schema import get_session
from ..schema.events import Event
from ..schema.topics import Topic
from ..utils.error import BlebotError
from ..utils.tzinfo import TZD, convert_to_utc
from ..client import client

allowed_actions = ["create", "delete", "list", "going", "help", "details", "ditch", "topic"]
def handle_help():
    return [], """\n`rsvp` - Organizes rsvp events\n
RSVP to an Event:
    `/rsvp [event number]` i.e. `/rsvp 1`
Get the Event number or a list of the events:
    `/rsvp list`
Create an Event:
    `/rsvp create Raid @ 8:00pm on Saturday`
Remove an Event:
    `/rsvp delete [event number]`
Ditch an Event:
    `/rsvp ditch [event number]`
Other commands:
`going` - `/rsvp going [event number]`
`topic` - `/rsvp topic on|off` - adds the schedule to channel topic
"""

def handle_action(command, action, args, message, extras):
    if not action:
        return [], "\nPlease provide an action! See `/rsvp help`"

    if action.isdigit():
        args = action
        action = "going"

    if action not in allowed_actions:
        raise BlebotError("\n`{action}` is not one of {actions}".format(
            action = action,
            actions = ", ".join(list(map(lambda x: "`" + x + "`", allowed_actions)))
        ))

    if action == "create":
        futures, results = _create(action, args, message)
    elif action == "delete":
        futures, results = _delete(action, args, message)
    elif action == "list":
        futures, results = _list(action, args, message)
    elif action == "details":
        futures, results = _details(action, args, message)
    elif action == "going":
        futures, results = _going(action, args, message)
    elif action == "ditch":
        futures, results = _ditch(action, args, message)
    elif action == "help":
        futures, results = handle_help()
    elif action == "topic":
        futures, results = _topic(args, message)
    else:
        futures = []
        results = "\nSomething went wrong"

    session = get_session(message.server.id)
    topic = session.query(Topic).filter(Topic.channel == message.channel.id).first()

    if topic and "rsvp" in topic.modules:
        futures.append(_edit_topic(message.channel, _list(action, args, message, limit=2)[1]))
    session.close()

    return futures, results

def _create(action, args, message):
    session = get_session(message.server.id)
    if not args or "@" not in args:
        raise BlebotError("\nPlease format your event description as [event name]@[date time]\n i.e. `/rsvp create Raid @ 4/16/2016 8:00pm EST`")
    name, time = args.split("@")
    try:
        date = dateutil.parser.parse(time.upper().strip(), tzinfos=TZD)
        utc_date = convert_to_utc(date)
    except:
        traceback.print_exc()
        raise BlebotError("I could not understand the time you gave me!")

    event = Event(name.strip().upper(), utc_date, message.author.name, message.channel.id, message.server.id)
    session.add(event)
    session.commit()

    result = "\nYou created an event!\n{event}".format(
        event=event.details()
    )
    session.close()
    return [], result

def _delete(action, args, message):
    session = get_session(message.server.id)
    if not args:
        raise BlebotError("Please provide the number of the event you wish to create! Check `/rsvp list`")

    event = session.query(Event).filter(and_(Event.id == int(args), Event.channel == message.channel.id)).first()
    if not event:
        raise BlebotError("Could not find event with number {number}".format(number=args))
    session.delete(event)
    session.commit()
    session.close()

    return [], "\nYou've deleted the event!"

def _list(action, args, message, limit=10):
    session = get_session(message.server.id)
    events = session.query(Event).filter(and_(Event.date >= datetime.datetime.now(), Event.channel == message.channel.id)).order_by(Event.date).limit(limit).all()
    if not events:
        return [], "\nThere are no upcoming events! :( \n\nMake one by using `/rsvp create`"

    return [], "\n{events}".format(
        events="\n".join(list(map(lambda x: x.details(), events)))
    )

def _details(action, args, message):
    if not args:
        raise BlebotError("Please provide the number of the event you wish to see! Check `/rsvp list`")
    session = get_session(message.server.id)
    event = session.query(Event).filter(and_(Event.id == int(args), Event.channel == message.channel.id)).first()
    if not event:
        raise BlebotError("Could not find event with number {number}".format(number=args))

    result = event.details()
    session.close()

    return [], result

def _going(action, args, message):
    if not args:
        raise BlebotError("Please provide the number of the event you wish to go to! Check `/rsvp list`")

    session = get_session(message.server.id)
    event = session.query(Event).filter(and_(Event.id == int(args), Event.channel == message.channel.id)).first()
    if not event:
        raise BlebotError("Could not find event with number {number}".format(number=args))

    if message.author.name in event.maybe:
        event.maybe.remove(message.author.name)
    event.going.add(message.author.name)
    session.commit()
    session.close()
    return [], "\n{name} registered as going!".format(name=message.author.name)

def _ditch(action, args, message):
    if not args:
        raise BlebotError("Please provide the number of the event you wish to ditch! Check `/rsvp list`")

    session = get_session(message.server.id)

    event = session.query(Event).filter(and_(Event.id == int(args), Event.channel == message.channel.id)).first()
    if not event:
        raise BlebotError("Could not find event with number {number}".format(number=args))

    if message.author.name in event.maybe:
        event.maybe.remove(message.author.name)
    if message.author.name in event.going:
        event.going.remove(message.author.name)
    session.commit()
    session.close()
    return [], "\n{name} ditched this event!".format(name=message.author.name)

PRESTRING = "(^-^) BLEBot Upcoming Events List:"
POSTSTRING = "--BLEBot Events List(^-^)"
def _topic(args, message):
    session = get_session(message.server.id)
    topic = session.query(Topic).filter(Topic.channel == message.channel.id).first()
    if not topic:
        topic = Topic(message.server.id, message.channel.id, {})
    if args == "on":
        topic.modules.add("rsvp")
        session.add(topic)
        session.commit()
        session.close()
        return [], "\nTopic updates for rsvp has been turned on!"
    elif args == "off":
        topic.modules.remove("rsvp")
        session.add(topic)
        session.commit()
        future = _edit_topic(message.channel, "")
        session.close()
        return [future], "\nTopic updates for rsvp has been turned off!"

def _edit_topic(channel, message, force=False):
    # topic = channel.topic or ""
    # if PRESTRING not in topic:
    #     topic += "\n{prestring}\n{message}\n{poststring}".format(
    #         prestring=PRESTRING,
    #         message=message,
    #         poststring=POSTSTRING
    #     )
    # else:
    #     start = topic.find(PRESTRING) + len(PRESTRING)
    #     end = topic.find(POSTSTRING)
    #     topic = topic[:start] + message + topic[end + 1:]
    message = PRESTRING + message
    return client.edit_channel(channel, topic=message)
