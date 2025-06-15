# Chralassistant
this is a virtual assistant i programmed purely in python it is modular so you can change looks etc just by simply replacing the images


this is a fanmade Project by savekillqqp for the itch.io game chrala cant Escape by boxie please support the original creator of the Character and Pixel art :D

this is a simple virtual assistant. ist currently the Version 0.1 beta and only has limited abillities. for now it can just Chat with you and has an idle Animation and talk Image to know when shes Talking.

commands:
hello (activates voice assistant and turns on listening. depending on your specs you have to wait a few seconds before Talking again for her to understand you)
goodbye (deactivates listening so she wont respond untill you say the activation word hello again)



if Auto Installation Fails for some reason (couldnt test cuz my pc alrdy has all the packages).
you will also need python for windows just download it for ubuntu just do sudo apt install python or sudo apt install python3
just manually install them by doing this:

pip install SpeechRecognition pyttsx3 pillow

on ubuntu linux use this guide:

1st set up your venv by doing: 

python3 -m venv .venv

source .venv/bin/activate

then download the pip files in the correct folder for example cd into the chralassistant folder.

then simply:
pip install SpeechRecognition pyttsx3 pillow

then you need to pip install pyaudio. im doing it by itself cause i for example had an error while installing it saying failed to build wheel. what worked for me was doing the following:

sudo apt-get install portaudio19-dev 

pip install pyaudio

after that install tkinter:

 sudo apt update
 sudo apt install python3-tk

then cd to the source folder inside of the chralassistant folder to be able to access the python code, do:

python ChralassistantV0-1.py

to start it. you will probably be asked to install Ollama and youll be send to the ollama official download page. for windows just install it using the installer for linux just follow the guide there. then restart the python programm and itll pull the model for chrala and then you should be able to use it.

the two images are required for the assistant to work :D

and then Restart the .exe file and have fun :D
