from sqlalchemy import Column, Integer, String, DateTime
import humanize
from pytz import timezone

from . import  Base
from .datatypes import ArraySet

EASTERN = timezone('US/Eastern')

class Event(Base):
    __tablename__ = "events"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String)
    created_by = Column("created_by", String)
    going = Column("going", ArraySet(String))
    maybe = Column("maybe", ArraySet(String))
    date = Column("time", DateTime)
    server = Column("column", String)
    channel = Column("channel", String)

    def __init__(self, name, date, created_by, channel_id, server_id, going=[], maybe=[]):
        self.name = name
        self.created_by = created_by
        self.going = going
        self.maybe = maybe
        self.date = date
        self.server = server_id
        self.channel = channel_id

    def details(self):
        return "\nEVENT #{number} - **{name}** at {date} created by *{created}*\n  Going: \t{going}".format(
            number=self.id,
            name=self.name,
            date="{time} (__{human}__)".format(
                time=EASTERN.localize(self.date).strftime("%I:%M%p %Z on %a. %b %d"),
                human=humanize.naturaltime(self.date)
            ),
            going=", ".join(self.going) if self.going else "No one",
            created=self.created_by
        )
