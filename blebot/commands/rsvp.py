import traceback, re

import parsedatetime
from pytz import timezone
from time import mktime
import datetime
import dateutil.parser
from sqlalchemy import and_

from ..schema import get_session
from ..schema.events import Event
from ..schema.topics import Topic
from ..utils.error import BlebotError
from ..client import client

EASTERN = timezone("US/Eastern")
allowed_actions = ["create", "delete", "list", "going", "maybe", "help", "details", "ditch", "topic"]
def handle_help():
    return [], """\n`rsvp` - Organizes rsvp events\n
`create` - create an event
    `/rsvp create Raid @ 8:00pm on Saturday`
`delete` - deletes an event
    `/rsvp delete [event number]`
`list` - lists the upcoming events
    `/rssvp list`
`going` - rsvp as going to an event
    `/rsvp going [event number]`
`maybe` - rsvp as maybe going to an event
    `/rsvp maybe [event number]`
`ditch` - remove your rsvp from the event
    `/rsvp ditch [event number]`
`topic` - add upcoming events to the channel's topic
    `/rsvp topic on|off`
"""

def handle_action(command, action, args, message, extras):
    if not action:
        return [], "\nPlease provide an action! See `/rsvp help`"

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
    elif action == "maybe":
        futures, results = _maybe(action, args, message)
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
        cal = parsedatetime.Calendar()
        time_struct, parse_status = cal.parse(time.strip())
        date = datetime.datetime.fromtimestamp(mktime(time_struct))

    except:
        traceback.print_exc()
        try:
            date = dateutil.parser.parse(time.strip())
        except:
            traceback.print_exc()
            raise BlebotError("I couldn't understand that time.")
    try:
        date = EASTERN.localize(date)
    except:
        traceback.print_exc()
        date = date.astimezone(EASTERN)

    event = Event(name.strip().upper(), date, message.author.name, message.channel.id, message.server.id)
    session.add(event)
    session.commit()

    result = "\nYou created an event!\nEvent Number: *{number}*!\n**{name}** @ __{date}__".format(
        number=event.id,
        name=name.upper(),
        date=date.strftime("%I:%M%p %Z on %a. %b %d"),
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
        events="\n".join(list(map(lambda x: x.format(), events)))
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


def _maybe(action, args, message):
    if not args:
        raise BlebotError("Please provide the number of the event you wish to maybe go to! Check `/rsvp list`")

    session = get_session(message.server.id)

    event = session.query(Event).filter(and_(Event.id == int(args), Event.channel == message.channel.id)).first()
    if not event:
        raise BlebotError("Could not find event with number {number}".format(number=args))

    if message.author.name in event.going:
        event.going.remove(message.author.name)

    event.maybe.add(message.author.name)
    session.commit()
    session.close()
    return [], "\n{name} registered as maybe attending!".format(name=message.author.name)

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
