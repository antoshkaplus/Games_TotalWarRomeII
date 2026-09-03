import peewee


DB = peewee.SqliteDatabase(None)


class BaseModel(peewee.Model):
    class Meta:
        database = DB
