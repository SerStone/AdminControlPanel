from enum import Enum


class StatusEnum(Enum):
    InWork = 'In work'
    New = 'New'
    Aggre = 'Aggre'
    Disaggre = 'Disaggre'
    Dubbing = 'Dubbing'


    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

    @classmethod
    def values(cls):
        return [key.value for key in cls]
