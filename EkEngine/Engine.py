import pyHook
import pythoncom

from threading import Thread
from EkEngine import WinPipe
from EkEngine.ScimTableParser import ScimTableParser


class Engine(Thread):
    def __init__(self, filepath=""):
        Thread.__init__(self)
        self.file_name = filepath
        self.conv_state = True

        self.key_state = {
            'Lcontrol': False,
            'Rcontrol': False,
            'Lshift': False,
            'Rshift': False,
            'Lmenu': False,
            'Rmenu': False
        }
        self.control_keys = ['Lcontrol', 'Rcontrol', 'Lshift', 'Rshift', 'Lmenu', 'Rmenu']
        self.event_queue = Queue()

        self.char_pressed = ""
        self.chars_to_send = ""
        self.prev_char_to_delete = ""
        self.prev_unicode_char_length = 0
        self.scim_mapping = {}
        self.scim_mapping_reversed = {}
        self.valid_chars = []
        self.hm = pyHook.HookManager()
        self.quit_thread = False

    def run(self):
        self.initialize()
        self.hook()
        # Making sure to remove hm in case
        self.un_hook()
        return

    def initialize(self):
        table_parser = ScimTableParser()
        self.scim_mapping = table_parser.parse(self.file_name)
        self.setvalid_chars()
        self.reverse_scim_map()

    def un_hook(self):
        try:
            self.quit_thread = True
            self.hm.__del__()
        except:
            pass

    def hook(self):
        self.hm.KeyDown = self.on_keyboard_event
        self.hm.KeyUp = self.on_keyup_event
        self.hm.HookKeyboard()
        while not self.quit_thread:
            pythoncom.PumpWaitingMessages()

    def setvalid_chars(self):
        keys_list = list(self.scim_mapping.keys())
        self.valid_chars = list(set("".join(keys_list)))
        return True

    def reverse_scim_map(self):
        self.scim_mapping_reversed = {}
        for k, v in self.scim_mapping.items():
            self.scim_mapping_reversed[v] = k

    def on_keyup_event(self, event):
        if event.Key in self.control_keys:
            self.key_state[event.Key] = False
        return True

    def check_event(self, char):
        for key, event in enumerate(self.event_queue.get_list()):
            fire = False
            for index, keys in enumerate(event[0]):
                fire = False
                if keys not in self.control_keys:
                    if keys == char:
                        fire = True
                elif not self.key_state[keys]:
                    break
            if fire:
                event[1](event[2])

    def on_keyboard_event(self, event):
        if event.Key in self.control_keys:
            self.key_state[event.Key] = True
        self.check_event(event.Key)
        if self.conv_state:
            char = chr(event.Ascii)
            if char in self.valid_chars:
                self.char_pressed += char
            elif char == " ":
                self.char_pressed += char
            elif char == 8:
                pass
            else:
                return True

            try:
                if char == 8:
                    self.char_pressed = self.char_pressed[:-1]

                if len(self.char_pressed) > 20:
                    self.char_pressed = self.char_pressed[-20:]

                for i in range(-5, 0):
                    chars = self.char_pressed[i:]
                    if chars in self.scim_mapping:
                        self.chars_to_send = self.scim_mapping[chars]
                        if chars[:-1] in self.scim_mapping:
                            self.prev_char_to_delete = self.scim_mapping[chars[:-1]]
                        else:
                            self.prev_char_to_delete = ""
                        self.prev_unicode_char_length = len(self.prev_char_to_delete)
                        break
                    elif i == -1:
                        return True

                if self.prev_unicode_char_length > 0 and len(self.chars_to_send) > 0:
                    for i in range(0, self.prev_unicode_char_length):
                        WinPipe.send_backspace()

                if self.chars_to_send:
                    for i in self.chars_to_send:
                        WinPipe.send_key_press(i)
                    self.chars_to_send = ""

                return False

            except KeyError as e:
                # print ('MessageName:',event.MessageName)
                # print ('Message:',event.Message)
                # print ('Time:',event.Time)
                # print ('Window:',event.Window)
                # print ('WindowName:',event.WindowName)
                # print ('Ascii:', event.Ascii, chr(event.Ascii))
                # print ('Key:', event.Key)
                # print ('KeyID:', event.KeyID)
                # print ('ScanCode:', event.ScanCode)
                # print ('Extended:', event.Extended)
                # print ('Injected:', event.Injected)
                # print ('Alt', event.Alt)
                # print ('Transition', event.Transition)
                # print ('---')
                print(e)
                return True
        else:
            return True


class Queue(object):
    """
        This is a queue where it will stay at the length of 5. when it reaches five it will start to dequeue the first
        element and then append the new element. Used to store the last five keystrokes.
    """
    def __init__(self, queue=None):
        if queue is None:
            self.queue = []
        else:
            self.queue = list(queue)

    def remove_event(self):
        try:
            return self.queue.pop(0)
        except IndexError:
            raise IndexError('dequeue from empty Queue')

    def register_event(self, element):
        self.queue.append(element)

    def get_list(self):
        return self.queue

    def remove_all(self):
        self.queue = []
