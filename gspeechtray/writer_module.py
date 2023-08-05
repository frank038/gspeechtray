# to use with pyinput
from pynput.keyboard import Controller, Key

class WM():
    def __init__(self):
        self.keyboard = Controller()
    
    def _write_text(self, tstring):
        self.keyboard.type(tstring)
        
    def _key_press(self, tstring):
        self.keyboard.press(tstring)
    
    def _key_release(self, tstringf):
        self.keyboard.release(tstring)
    
    def _delete_char(self):
        self.keyboard.press(Key.backspace)
        self.keyboard.release(Key.backspace)
        
    def _new_line(self):
        # self.keyboard.type("\n")
        self.keyboard.press(Key.backspace)
        self.keyboard.release(Key.backspace)
        self.keyboard.press(Key.enter)
        self.keyboard.release(Key.enter)
