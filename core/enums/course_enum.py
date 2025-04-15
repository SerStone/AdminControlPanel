from enum import Enum


class CourseEnum(Enum):
    QACX = 'QACX'
    PCX = 'PCX'
    FS = 'FS'
    JSCX = 'JSCX'
    JCX = 'JCX'
    FE = 'FE'
    null = None

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

    @classmethod
    def values(cls):
        return [key.value for key in cls]
