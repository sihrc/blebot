import json

from sqlalchemy import Column, String

from . import Base
from .datatypes import ArrayList

class Topic(Base):
    __tablename__ = "topics"

    channel = Column("channel", String, primary_key=True)
    server = Column("server", String)
    modules = Column("modules", ArrayList(String))

    def __init__(self, server, channel, modules={}):
        self.server = server
        self.channel = channel
        self.modules = modules
