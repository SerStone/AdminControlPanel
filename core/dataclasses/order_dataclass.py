from dataclasses import dataclass
from datetime import datetime


@dataclass
class OrderDataClass:
    id: int
    name: str
    surname: str
    email: str
    phone: str
    age: int
    course: str
    course_format: str
    course_type: str
    sum: int
    alreadyPaid: int
    createdAt: datetime
    utm: str
    msg: str
    status: str
    manager: int
    group: str
