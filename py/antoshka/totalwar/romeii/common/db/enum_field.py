import peewee
import enum
import typing as ty


def EnumField(base_field):
    class Field(base_field):
        """
        ref: https://github.com/coleifer/peewee/issues/630
        """

        def __init__(self, enum: ty.Type[enum.Enum], *args: ty.Any, **kwargs: ty.Any) -> None:
            super().__init__(*args, **kwargs)
            self.enum = enum

        def db_value(self, value: ty.Any) -> ty.Any:
            if value is None:
                return None
            return value.value

        def python_value(self, value: ty.Any) -> ty.Any:
            if value is None:
                return None
            return self.enum(value)

    return Field


EnumCharField = EnumField(peewee.CharField)
EnumIntegerField = EnumField(peewee.IntegerField)


class IgnoreFieldType(enum.Enum):
    Value = enum.auto()