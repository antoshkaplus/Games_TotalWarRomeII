import datetime
import pandas as pd
import peewee


utc_tz = datetime.timezone.utc


class UTC_DateTimeField(peewee.DateTimeField):
    """
    https://github.com/coleifer/peewee/issues/1427#issuecomment-359067837

    When saving datetime.date convert it to datetime.datetime with NY time zone first.
    Everything is saved and read as UTC time zone. User responsibility to convert to desired timezone later.

    TODO:
        By coding style standards this should be somewhere under `db` package. But this is not a db model.
        This is db type used by db models. Maybe we should have `dbtypes` package under `model` folder.
    """

    def python_value(self, value):
        dt = super().python_value(value)
        if dt is None:
            return
        return dt.replace(tzinfo=utc_tz)

    def db_value(self, value):
        if value is None:
            return
        # Must check that it's not a datetime directly, since datetime is subclass of date
        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            raise RuntimeError("Must be timezone aware datetime. `datetime.date` is not.")
        if isinstance(value, pd.Timestamp):
            value = value.to_pydatetime()
        value = value.astimezone(utc_tz).replace(tzinfo=None)
        return value