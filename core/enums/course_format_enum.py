from enum import Enum


class CourseFormatEnum(Enum):
    static = 'static'
    online = 'online'
    null = None

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

    @classmethod
    def values(cls):
        return [key.value for key in cls]
