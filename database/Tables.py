from peewee import *


database = SqliteDatabase('ekalappai.db')


class BaseModel(Model):
    class Meta:
        database = database


class GeneralSetting(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField()
    value1 = CharField(null=True)
    value2 = CharField(null=True)
    value3 = CharField(null=True)


class LanguageSetting(BaseModel):
    id = IntegerField(primary_key=True)
    language_name = CharField()
    file_path = CharField(511)
    is_default = IntegerField(default=20)


class ShortcutKey(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField()
    parent = ForeignKeyField('self', backref='children')



def initialize():
    database.connect()
    database.create_tables([GeneralSetting, LanguageSetting, ShortcutKey], safe=False)
    return database
