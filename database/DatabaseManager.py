from database.Tables import *


class DatabaseManager:
    def __init__(self):
        self.db = database
        self.init_data = [
                {'name': 'CTRL', 'parent': '0'},
                {'name': 'ALT', 'parent': '0'},
                {'name': 'NONE', 'parent': '0'},
                {'name': '1', 'parent': '1'},
                {'name': '2', 'parent': '1'},
                {'name': '3', 'parent': '1'},
                {'name': '4', 'parent': '1'},
                {'name': '5', 'parent': '1'},
                {'name': '6', 'parent': '1'},
                {'name': '7', 'parent': '1'},
                {'name': '8', 'parent': '1'},
                {'name': '9', 'parent': '1'},
                {'name': '0', 'parent': '1'},
                {'name': '1', 'parent': '2'},
                {'name': '2', 'parent': '2'},
                {'name': '3', 'parent': '2'},
                {'name': '4', 'parent': '2'},
                {'name': '5', 'parent': '2'},
                {'name': '6', 'parent': '2'},
                {'name': '7', 'parent': '2'},
                {'name': '8', 'parent': '2'},
                {'name': '9', 'parent': '2'},
                {'name': '0', 'parent': '2'},
                {'name': 'F1', 'parent': '1'},
                {'name': 'F2', 'parent': '1'},
                {'name': 'F3', 'parent': '1'},
                {'name': 'F4', 'parent': '1'},
                {'name': 'F5', 'parent': '1'},
                {'name': 'F6', 'parent': '1'},
                {'name': 'F7', 'parent': '1'},
                {'name': 'F8', 'parent': '1'},
                {'name': 'F9', 'parent': '1'},
                {'name': 'F10', 'parent': '1'},
                {'name': 'F11', 'parent': '1'},
                {'name': 'F12', 'parent': '1'},
                {'name': 'F1', 'parent': '2'},
                {'name': 'F2', 'parent': '2'},
                {'name': 'F3', 'parent': '2'},
                {'name': 'F4', 'parent': '2'},
                {'name': 'F5', 'parent': '2'},
                {'name': 'F6', 'parent': '2'},
                {'name': 'F7', 'parent': '2'},
                {'name': 'F8', 'parent': '2'},
                {'name': 'F9', 'parent': '2'},
                {'name': 'F10', 'parent': '2'},
                {'name': 'F11', 'parent': '2'},
                {'name': 'F12', 'parent': '2'},
                {'name': 'F1', 'parent': '3'},
                {'name': 'F2', 'parent': '3'},
                {'name': 'F3', 'parent': '3'},
                {'name': 'F4', 'parent': '3'},
                {'name': 'F5', 'parent': '3'},
                {'name': 'F6', 'parent': '3'},
                {'name': 'F7', 'parent': '3'},
                {'name': 'F8', 'parent': '3'},
                {'name': 'F9', 'parent': '3'},
                {'name': 'F10', 'parent': '3'},
                {'name': 'F11', 'parent': '3'},
                {'name': 'F12', 'parent': '3'},
            ]
        try:
            initialize()
            self.init_tables()
        except OperationalError:
            pass
        self.db.connect()

    @staticmethod
    def create_setting(values):
        record = GeneralSetting(name=values['name'], value1=values['value1'])
        record.save()

    @staticmethod
    def get_keys(parent=0):
        return ShortcutKey.select().where(ShortcutKey.parent == parent)

    @staticmethod
    def set_shortcut_key(key_id):
        shortcut_key = GeneralSetting.get(name="shortcut_key")
        shortcut_key.value1 = str(key_id)
        shortcut_key.save()

    @staticmethod
    def get_shortcut_key():
        shortcut_key, created = GeneralSetting.get_or_create(name="shortcut_key", defaults={'value1': 4})
        modifier = ShortcutKey.alias()
        shortcut_key_model = (ShortcutKey
                              .select(ShortcutKey, modifier)
                              .join(modifier, on=(ShortcutKey.parent == modifier.id))
                              .where(ShortcutKey.id == shortcut_key.value1)).first()
        return shortcut_key_model

    @staticmethod
    def set_current_state(state):
        current_state = GeneralSetting.get(name="current_state")
        current_state.value1 = str(state)
        current_state.save()

    @staticmethod
    def get_current_state():
        current_state, created = GeneralSetting.get_or_create(name="current_state", defaults={'value1': "False"})
        return current_state.value1

    @staticmethod
    def set_current_keyboard(idx):
        current_state = GeneralSetting.get(name="current_keyboard")
        current_state.value1 = str(idx)
        current_state.save()

    @staticmethod
    def get_current_keyboard():
        current_state, created = GeneralSetting.get_or_create(name="current_keyboard", defaults={'value1': "1"})
        return current_state.value1

    @staticmethod
    def add_keyboard(keyboard_name, file_path):
        LanguageSetting.create(language_name=keyboard_name, file_path=file_path)

    @staticmethod
    def get_keyboard(keyboard_name):
        return LanguageSetting.select().where(LanguageSetting.language_name == keyboard_name).get()

    @staticmethod
    def check_keyboard_exist(keyboard_name):
        query = LanguageSetting.select().where(LanguageSetting.language_name == keyboard_name)
        if query.exists():
            return True
        else:
            return False

    @staticmethod
    def get_all_keyboards():
        return [LanguageSetting.select().count(), LanguageSetting.select()]

    @staticmethod
    def remove_keyboard(idx):
        query = LanguageSetting.delete().where(LanguageSetting.id == idx)
        query.execute()
        return

    @staticmethod
    def get_keyboard_path(keyboard_id):
        return LanguageSetting.get(LanguageSetting.id == keyboard_id).file_path

    def init_tables(self):
        with self.db.atomic():
            ShortcutKey.insert_many(self.init_data).execute()

    def __del__(self):
        self.db.close()
