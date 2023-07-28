# gspeechtray
A speech to text program for Italians. Version 0.1

This program is intended to be used with the Italian language (it's impossible for me to extend this program to other languages).

Made in python3 and Gtk3. A microphone is mandatory. Works only with Xorg, and it is a x86-64 program (only for libvosk.so). Pyinput and sounddevice modules and the vosk engine (v. 0.3.45) are provided. For other CPU architectures, give a look at alphacep/voks-api.

This program is just a tray program; download it from the release section and launch it from the terminal: command line: python3 gspeechtray.py; then, it will ask you to choose a proper microphone from the list; then, exit from the program and relaunch it; now the program is ready to be used. The config file cfg.py doesn't need to be changed manually, unless a custom samplerate is needed.

The recognized text will be printed into the active and focused window, such as a text editor. First, from the tray choose "Inizia/Ferma il riconoscimento" (the icon will change: red do not write anything, green is for the active state; anyway, the microphone keeps listening everything). 

How to use: the continuous speech is written as is; for punctuation marks and symbols - as coded in the file sostituzioni.py - just wait for the text to be all written, and then tell them one at a time. Special keywords are: cancella (cancel) for deleting the last character; "a capo" (return) for a new line.

This program may have bugs, and is not finished. If this program is downloaded from the actual web page instead from the release section, the first time the Italian language model package will be downloaded (~ 47 MB). This program has everything it needs to works, but some very common python modules might be requested. The Vosk speech recognition toolkit is used. It works offline (excpet for the language model package, it will be downloaded if the case).
