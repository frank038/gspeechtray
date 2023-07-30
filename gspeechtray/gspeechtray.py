#!/usr/bin/env python3

# V. 0.3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio
from gi.repository.GdkPixbuf import Pixbuf
import os
import sys
from time import time, sleep

WINW = 800
WINH = 40

# the window for the microphone
mic_win = 0

ddata = None

from cfg import *
from sostituzioni import *

import threading

from pynput.keyboard import Controller, Key
keyboard = Controller()

import argparse
import queue
import sys
import sounddevice as sd
from vosk import Model, KaldiRecognizer

################################

# audio device list
audio_dev = sd.query_devices()
audio_dev_list = list(audio_dev)

ddev = None
asamplerate = 16000
num_channels = 1


for adev in audio_dev_list:
   if adev["max_input_channels"] == 0:
       continue
   if adev["name"] == mic:
       ddev = adev["index"]
       asamplerate = int(adev["default_samplerate"])
       num_channels = int(adev["max_input_channels"])
       break
#
if msamplerate != -1:
    asamplerate = msamplerate

#
if numch != -1:
    num_channels = numch

q = queue.Queue()


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


#
is_ready = 1
if ddev == None:
    is_ready = 0
    

########################
thread_stop = False

class cThread(threading.Thread):
    def __init__(self, sd, callback, q, ddev, samplerate, num_ch):
        super(cThread, self).__init__()
        self.ii = 0
        self.sd = sd
        self.callback = callback
        self.q = q
        self.ddev = ddev
        self.samplerate = samplerate
        self.num_ch = num_ch
        
    def run(self):
        while True:
            with self.sd.RawInputStream(samplerate=self.samplerate, blocksize = 8000, device=self.ddev,
                dtype="int16", channels=self.num_ch, callback=self.callback):
                rec = KaldiRecognizer(Model(lang="it"), self.samplerate)
                
                # first word capitalized
                word_capitalized = 1
                
                while not thread_stop:
                    data = self.q.get()
                    if rec.AcceptWaveform(data):
                        
                        rddata = rec.Result().strip("\n")
                        
                        if ddata:
                            text_to_send = rddata[2:-2].split(":")[1][2:-1]
                            
                            if text_to_send == "":
                                continue
                            # segni tipo virgola
                            elif text_to_send in segni_senza_pre_spazio:
                                chart = segni_senza_pre_spazio[text_to_send]
                                keyboard.press(Key.backspace)
                                keyboard.release(Key.backspace)
                                keyboard.type(chart)
                                keyboard.type(" ")
                                if chart in segni_di_fine_frase:
                                    word_capitalized = 1
                                continue
                            # segni tipo virgolette
                            elif text_to_send in segni_con_pre_spazio:
                                chart = segni_con_pre_spazio[text_to_send]
                                keyboard.type(chart)
                                continue
                            # con spazi
                            elif text_to_send in segni_con_spazi:
                                chart = segni_con_spazi[text_to_send]
                                keyboard.type(chart)
                                keyboard.type(" ")
                                continue
                            # simboli
                            elif text_to_send in segni_simboli:
                                chart = segni_simboli[text_to_send]
                                keyboard.type(chart)
                                keyboard.type(" ")
                                continue
                            # segni senza spazi
                            elif text_to_send in segni_senza_spazi:
                                chart = segni_senza_spazi[text_to_send]
                                keyboard.press(Key.backspace)
                                keyboard.release(Key.backspace)
                                keyboard.type(chart)
                                continue
                            # cancella l ultimo carattere inserito
                            elif text_to_send == "cancella":
                                keyboard.press(Key.backspace)
                                keyboard.release(Key.backspace)
                                continue
                            # # nuovo rigo
                            # elif text_to_send == "a capo":
                                # # keyboard.type("\n")
                                # keyboard.press(Key.backspace)
                                # keyboard.release(Key.backspace)
                                # keyboard.press(Key.enter)
                                # keyboard.release(Key.enter)
                                # continue
                            #
                            if word_capitalized:
                                text_to_send = text_to_send[0].upper()+text_to_send[1:]
                                word_capitalized = 0
                            # for chch in text_to_send:
                                # keyboard.type(chch)
                            keyboard.type(text_to_send)
                            keyboard.type(" ")
                        
                        # # else:
                            # # print(rec.PartialResult())
                        # if dump_fn is not None:
                            # dump_fn.write(data)
                        
            #################
            if thread_stop:
                break
        if thread_stop:
            return

is_started = 0
def t_start():
    if is_ready and ddata:
        global is_started
        is_started = 1
        threadc = cThread(sd, callback, q, ddev, asamplerate, num_channels)
        threadc.start()

####################

################### Tray applet #################

class StatusIcon:
    def __init__(self):
        self.status_icon = Gtk.StatusIcon()
        
        self.TRAY_ICON = "start.png"
        self.TRAY_ICON_STOP = "pause.png"
        
        self.status_icon.set_from_file(self.TRAY_ICON_STOP)
        self.status_icon.connect("popup-menu", self.on_right_click)
        
        # to change the icon
        global ddata
        ddata = False
        
        #
        if is_ready == 0:
            global mic_win
            if not mic_win:
                win = MicWindow()
                win.show_all()
                mic_win = 1
            
        
    def on_right_click(self, icon, button, time):
        self.menu = Gtk.Menu()
        menutray = Gtk.MenuItem()
        menutray.set_label("Inizia/Ferma il riconoscimento")
        menutray.connect("activate", self.set_data)
        self.menu.append(menutray)
        
        # set the microphone
        mictray = Gtk.MenuItem()
        mictray.set_label("Scegli il microfono")
        mictray.connect("activate", self.set_mic)
        self.menu.append(mictray)
        
        eexit = Gtk.MenuItem()
        eexit.set_label("Esci")
        eexit.connect("activate", self.t_exit)
        self.menu.append(eexit)
        self.menu.show_all()
        self.menu.popup(None, None, None, self.status_icon, button, time)
    
    def t_exit(self, w):
        global thread_stop
        thread_stop = True
        Gtk.main_quit()
    
    def set_data(self, widget):
        global ddata
        if ddata:
            self.status_icon.set_from_file(self.TRAY_ICON_STOP)
            ddata = False
        else:
            self.status_icon.set_from_file(self.TRAY_ICON)
            ddata = True
            if is_started == 0:
                t_start()
            
    def set_mic(self, widget):
        global mic_win
        if not mic_win:
            win = MicWindow()
            win.show_all()
            mic_win = 1
            
################## window ####################

class mainWindow(Gtk.Window):
    
    def __init__(self):
        Gtk.Window.__init__(self, title="Gspeach")
        self.set_border_width(4)
        self.resize(400, 400)
        #
        self.set_resizable(False)
        self.set_position(1)
        #
        self.vbox = Gtk.Box(orientation=1, spacing=10)
        self.add(self.vbox)
        #
        self._startbtn = Gtk.Button(label="Inizia")
        self._startbtn.connect("clicked", self._btnpause)
        self.vbox.pack_start(self._startbtn, True, False, 1)
        #
        self._micbtn = Gtk.Button(label="Microfono")
        self._micbtn.connect("clicked", self.set_mic)
        self.vbox.pack_start(self._micbtn, True, False, 1)
        #
        self._closebtn = Gtk.Button(label="Esci")
        self._closebtn.connect("clicked", self.t_exit)
        self.vbox.pack_start(self._closebtn, True, False, 1)
        
        #
        if is_ready == 0:
            global mic_win
            if not mic_win:
                win = MicWindow()
                win.show_all()
                mic_win = 1
        #
        self.show_all()
    
    def _btnpause(self, w):
        global ddata
        if ddata:
            w.set_label("Inizia")
            ddata = False
        else:
            w.set_label("Ferma")
            ddata = True
            if is_started == 0:
                t_start()
    
    def t_exit(self, w):
        global thread_stop
        thread_stop = True
        Gtk.main_quit()
    
    def set_mic(self, widget):
        global mic_win
        if not mic_win:
            win = MicWindow()
            win.show_all()
            mic_win = 1
    
################## Microphone ##################

class MicWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="")
        self.connect("destroy", self.wclose)
        self.set_border_width(4)
        self.resize(WINW, WINH)
        self.set_keep_above(True)
        #
        self.set_resizable(False)
        self.set_position(1)
        #
        self.vbox = Gtk.Box(orientation=1, spacing=10)
        self.add(self.vbox)
        #
        self.label1 = Gtk.Label(label="      Scegli il microfono      ")
        # 
        self.vbox.pack_start(self.label1, True, True, 1)
        #
        self.miccombo = Gtk.ComboBoxText()
        self.miccombo.props.hexpand = True
        #
        for adev in audio_dev_list:
            if adev["max_input_channels"] == 0:
                continue
            self.miccombo.append(str(adev["index"]), adev["name"])
        #
        mmm = self.miccombo.get_model()
        #
        for ie in range(len(mmm)):
            if str(mmm[ie][0]) == str(mic):
                self.miccombo.set_active(ie)
                break
        #
        self.miccombo.connect('changed', self.miccombo_changed)
        #
        self.vbox.pack_start(self.miccombo, True, True, 1)
        #
        self.button2 = Gtk.Button(label="Chiudi")
        self.button2.connect("clicked", self.cclose)
        self.button2.props.valign = 2
        self.vbox.pack_start(self.button2, True, True, 1)
        #
        
    def miccombo_changed(self, w):
        global mic
        mic = self.miccombo.get_active_text()
    
    def wclose(self, w):
        global mic_win
        mic_win = 0
        #
        with open("cfg.py", "w") as ff:
            ff.write('mic="{}"\n'.format(mic))
            ff.write("msamplerate={}\n".format(msamplerate))
            ff.write("numch={}".format(numch))
        #
        global thread_stop
        thread_stop = True
        #
        self.destroy()
    
    def cclose(self, w):
        self.destroy()
    
########

if len(sys.argv) == 2 and sys.argv[1] == "-p":
    m = mainWindow()
else:
    m = StatusIcon()
Gtk.main()
