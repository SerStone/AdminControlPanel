class InvalidEnumValueError(Exception):

    def __init__(self, field_name, valid_values):
        self.field_name = field_name
        self.valid_values = valid_values
        super().__init__(self._generate_message())

    def _generate_message(self):
        valid_values = [v for v in self.valid_values if v is not None]
        return {self.field_name: [f"Invalid value. Available values: {', '.join(valid_values)}"]}

