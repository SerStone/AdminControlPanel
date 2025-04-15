from enum import Enum


class CourseTypeEnum(Enum):
    PRO = 'pro'
    MINIMAL = 'minimal'
    PREMIUM = 'premium'
    INCUBATOR = 'incubator'
    VIP = 'vip'
    null = None

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

    @classmethod
    def values(cls):
        return [key.value for key in cls]

