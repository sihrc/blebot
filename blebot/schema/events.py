from sqlalchemy import Column, Integer, String, DateTime
import humanize
import pytz

from . import  Base
from .datatypes import ArraySet

EASTERN = pytz.timezone("EST")
UTC = pytz.timezone("UTC")
def convert_to_est(datetime):
    return UTC.localize(datetime).astimezone(EASTERN)

class Event(Base):
    __tablename__ = "events"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String)
    created_by = Column("created_by", String)
    going = Column("going", ArraySet(String))
    date = Column("time", DateTime)
    server = Column("column", String)
    channel = Column("channel", String)

    def __init__(self, name, date, created_by, channel_id, server_id, going=[]):
        self.name = name
        self.created_by = created_by
        self.going = going
        self.date = date
        self.server = server_id
        self.channel = channel_id

    def details(self):
        return "\nEVENT #{number}\n**{name}** at {date}\n__{human}__\ncreated by *{created}*\n\t\tGoing({num_people}): \t{going}".format(
            number=self.id,
            name=self.name,
            date="{time}".format(
                time=convert_to_est(self.date).strftime("%I:%M%p %Z on %a. %b %d"),
            ),
            human=humanize.naturaltime(self.date),
            going=", ".join(self.going) if self.going else "No one",
            created=self.created_by,
            num_people=len(self.going)
        )
