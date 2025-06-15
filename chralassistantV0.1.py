
import speech_recognition as sr
import pyttsx3
import subprocess
import threading
import tkinter as tk
import time
import os
import webbrowser
import sys
import math
from PIL import Image, ImageTk

# ------------------ Auto install dependencies ------------------
def install_and_exit(packages):
    print("Installing missing packages:", packages)
    subprocess.check_call([sys.executable, "-m", "pip", "install", *packages])
    print("Packages installed. Please restart the program.")
    sys.exit()

required_packages = {
    "speech_recognition": "speechrecognition",
    "pyttsx3": "pyttsx3",
    "pyaudio": "pyaudio",
    "PIL": "pillow"
}

missing = []
for module, package_name in required_packages.items():
    try:
        __import__(module)
    except ImportError:
        missing.append(package_name)

if missing:
    install_and_exit(missing)

# ------------------ Now import packages after ensured installation ------------------
import speech_recognition as sr
import pyttsx3
from PIL import Image, ImageTk

# Shared state
is_speaking = False
HISTORY_FILE = "chathistory.txt"
ollama_ready = False
loading_message = "Loading Ollama..."
last_heard_text = ""

# For GUI labels global references
main_label = None
heard_label = None
listening_label = None

# ----------------- GUI -----------------
def animate_images(canvas, image_label, main_label_, heard_label_, idle_frames, talking_img):
    frame_index = 0
    while True:
        canvas.update()
        if is_speaking:
            image_label.config(image=talking_img)
        else:
            frame = idle_frames[frame_index]
            image_label.config(image=frame)
            frame_index = (frame_index + 1) % len(idle_frames)

        main_label_.config(text=loading_message)
        heard_label_.config(text=f"Heard: {last_heard_text}" if last_heard_text else "")
        time.sleep(0.1)

def setup_gui():
    global main_label, heard_label, listening_label

    root = tk.Tk()
    root.title("Chralassistant")
    root.geometry("400x550")
    root.configure(bg="black")
    root.resizable(False, False)

    canvas = tk.Canvas(root, width=300, height=450, bg="black", highlightthickness=0)
    canvas.pack()

    # Load animated idle.gif
    idle_gif = Image.open("idle.gif")
    idle_frames = []

    try:
        while True:
            frame = idle_gif.copy().resize((300, 450))
            idle_frames.append(ImageTk.PhotoImage(frame))
            idle_gif.seek(len(idle_frames))  # Go to next frame
    except EOFError:
        pass  # End of frames

    # Load talking image
    talking_image = Image.open("talking.jpg").resize((300, 450))
    talking_img = ImageTk.PhotoImage(talking_image)

    image_label = tk.Label(canvas, bg="black")
    image_label.pack()

    main_label = tk.Label(root, text=loading_message, fg="white", bg="black", font=("Arial", 16))
    main_label.pack(pady=10)

    heard_label = tk.Label(root, text="", fg="gray70", bg="black", font=("Arial", 10))
    heard_label.pack()

    listening_label = tk.Label(root, text="", fg="grey", bg="black", font=("Arial", 14, "italic"))
    listening_label.pack(pady=5)

    threading.Thread(
        target=animate_images,
        args=(canvas, image_label, main_label, heard_label, idle_frames, talking_img),
        daemon=True
    ).start()

    return root

# ----------------- Ollama Checks -----------------
def check_ollama_installed():
    try:
        subprocess.run(["ollama", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def pull_wizard_model():
    try:
        process = subprocess.run(["ollama", "pull", "wizardlm2"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("Failed to pull wizardlm2 model:", e.stderr)
        return False

def startup_checks():
    global ollama_ready, loading_message
    loading_message = "Checking Ollama installation..."
    main_label.after(0, lambda: main_label.config(text=loading_message))

    if not check_ollama_installed():
        loading_message = "Ollama not found. Opening download page..."
        main_label.after(0, lambda: main_label.config(text=loading_message))
        time.sleep(2)
        webbrowser.open("https://ollama.com/download/")
        loading_message = "Please install Ollama and restart the app."
        main_label.after(0, lambda: main_label.config(text=loading_message))
        return

    loading_message = "Pulling wizardlm2 model..."
    main_label.after(0, lambda: main_label.config(text=loading_message))
    if pull_wizard_model():
        loading_message = "Chrala is ready! Starting talking..."
        ollama_ready = True
        main_label.after(0, lambda: main_label.config(text=loading_message))
        time.sleep(1)
    else:
        loading_message = "Failed to prepare model. Check your Ollama setup."
        main_label.after(0, lambda: main_label.config(text=loading_message))
        time.sleep(3)

# ----------------- Memory -----------------
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return ""
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return f.read()

def save_to_history(user_input, assistant_response):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"User: {user_input}\nAssistant: {assistant_response}\n")

# ----------------- Ollama -----------------
def send_to_ollama(user_input):
    instruction = (
        "You are a assistant with a casual, human-like personality. "
        "You must NEVER say you're an AI or talk about how you work. "
        "Do not use phrases like 'as an AI', 'note:', 'remember:', or explain your abilities. "
        "Speak like a real person would: direct, conversational, friendly, and brief. "
        "Your responses should sound natural, without extra politeness or formality. "
        "Avoid rambling or trying to sound smart. Just talk like a normal person helping a friend."
        "Your name is chrala and you are a cat girl and you are adorable and talk like a catgirl"
        "\n\n"
    )

    history = load_history()
    full_prompt = f"{instruction}{history}User: {user_input}\nAssistant:"
    ollama_command = ["ollama", "run", "wizardlm2"]

    try:
        process = subprocess.Popen(
            ollama_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(f"Sending to Ollama:\n{full_prompt}")
        output, error = process.communicate(input=full_prompt)

        if output:
            output = output.strip()
            print("Ollama response:", output)
            save_to_history(user_input, output)
        if error:
            print("Error from Ollama:", error.strip())

        return output if output else None

    except Exception as e:
        print(f"An error occurred while communicating with Ollama: {e}")
        return None

# ----------------- Speech -----------------
def recognize_speech(mic, recognizer):
    global last_heard_text, listening_label

    if listening_label:
        listening_label.after(0, lambda: listening_label.config(text="Listening..."))

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    if listening_label:
        listening_label.after(0, lambda: listening_label.config(text=""))

    try:
        text = recognizer.recognize_google(audio)
        print("You said: " + text)
        last_heard_text = text
        return text
    except sr.UnknownValueError:
        print("Could not understand audio.")
        last_heard_text = "[Could not understand you]"
        return None
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        last_heard_text = "[Speech recognition error]"
        return None

def speak_text(text, engine):
    global is_speaking
    is_speaking = True
    print("Assistant says:", text)
    engine.say(text)
    engine.runAndWait()
    is_speaking = False

# ----------------- Logic -----------------
def listen_for_activation(mic, recognizer):
    print("Listening for activation word...")
    while True:
        text = recognize_speech(mic, recognizer)
        if text and text.lower() == "hello":
            print("Activation word detected. Listening for commands...")
            return

def main_loop(tts_engine, mic, recognizer):
    while True:
        text = recognize_speech(mic, recognizer)
        if text:
            print(f"Recognized command: '{text}'")
            if text.lower() == "goodbye":
                speak_text("Goodbye! I'm here when you need me.", tts_engine)
                return

            response = send_to_ollama(text.strip())
            if response:
                speak_text(response, tts_engine)
            else:
                print("No response from Ollama.")

# ----------------- Entry -----------------
def run_assistant():
    global ollama_ready
    while not ollama_ready:
        time.sleep(0.1)

    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    tts_engine = pyttsx3.init()

    for voice in tts_engine.getProperty('voices'):
        if "female" in voice.name.lower() or "zira" in voice.name.lower():
            tts_engine.setProperty('voice', voice.id)
            break

    while True:
        listen_for_activation(mic, recognizer)
        main_loop(tts_engine, mic, recognizer)

if __name__ == "__main__":
    app = setup_gui()
    threading.Thread(target=startup_checks, daemon=True).start()
    threading.Thread(target=run_assistant, daemon=True).start()
    app.mainloop()

# pyinstaller --noconfirm --onefile --windowed --add-data "idle.gif;." --add-data "talking.jpg;." --icon=catgirl.ico test4.py
