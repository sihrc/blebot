from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.dialects.postgresql import ARRAY

class MutableList(Mutable, list):
    def append(self, value):
        list.append(self, value)
        self.changed()
    def remove(self, value):
        list.remove(self, value)
        self.changed()
    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value

def ArrayList(_type, dimensions=1):
    return MutableList.as_mutable(ARRAY(_type, dimensions=dimensions))
