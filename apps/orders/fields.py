from rest_framework.fields import CharField

from core.exceptions.invavid_enum_exceptions import InvalidEnumValueError


class EnumChoiceField(CharField):
    def __init__(self, enum_class, **kwargs):
        self.enum_class = enum_class
        self.valid_values = [e.value for e in enum_class]
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if data not in self.valid_values:
            raise InvalidEnumValueError(self.field_name, self.valid_values)
        return data
