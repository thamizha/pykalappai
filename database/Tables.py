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


class ShortcutKey(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField()
    parent = IntegerField()


def initialize():
    database.connect()
    database.create_tables([GeneralSetting, LanguageSetting, ShortcutKey])
