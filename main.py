import sounddevice as sd
import queue
import vosk
import json
from googletrans import Translator
import tkinter as tk
from tkinter import ttk, messagebox
import pyttsx3

# Initialize Vosk model
model = vosk.Model(r"C:\vosk-model-en-us-0.22")
q = queue.Queue()

def callback(indata, frames, time, status):
    """Callback function to handle audio input."""
    q.put(bytes(indata))

def record_audio():
    """Records audio and recognizes speech using Vosk."""
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
        recognizer = vosk.KaldiRecognizer(model, 16000)
        recognized_text = ""
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                result_json = json.loads(result)
                recognized_text = result_json.get('text', '')
                if recognized_text:
                    return recognized_text

def translate_text(text, target_language):
    """Translates the recognized text to the target language."""
    translator = Translator()
    try:
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        messagebox.showerror("Translation Error", f"Translation error: {e}")
        return None

def synthesize_speech(text):
    """Converts translated text to speech."""
    if text:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    else:
        messagebox.showwarning("No Text", "No text to synthesize.")

def save_translation(original, translated):
    """Saves the translation to a text file."""
    with open("translations.txt", "a") as f:
        f.write(f"Original: {original}\nTranslated: {translated}\n\n")

def run_translation():
    """Runs the translation process and updates the GUI."""
    recognized_text = record_audio()
    if recognized_text:
        original_text_var.set(recognized_text)
        target_language = lang_combobox.get()
        translated_text = translate_text(recognized_text, target_language)
        if translated_text:
            translated_text_var.set(translated_text)
            synthesize_speech(translated_text)
            save_translation(recognized_text, translated_text)

def show_help():
    """Displays help information."""
    messagebox.showinfo("Help", "Press 'Start' to record audio. Choose the target language and the translation will be displayed and spoken.")

# Set up the GUI
root = tk.Tk()
root.title("Real-Time Language Translation")

# Create GUI components
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

start_button = tk.Button(frame, text="Start Translation", command=run_translation)
start_button.grid(row=0, column=0, padx=5, pady=5)

help_button = tk.Button(frame, text="Help", command=show_help)
help_button.grid(row=0, column=1, padx=5, pady=5)

lang_label = tk.Label(frame, text="Select Target Language:")
lang_label.grid(row=1, column=0, padx=5, pady=5)

lang_combobox = ttk.Combobox(frame, values=["es", "fr", "de", "zh-CN"], state="readonly")
lang_combobox.set("es")  # Default to Spanish
lang_combobox.grid(row=1, column=1, padx=5, pady=5)

original_text_var = tk.StringVar()
translated_text_var = tk.StringVar()

original_label = tk.Label(frame, textvariable=original_text_var, wraplength=250)
original_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

translated_label = tk.Label(frame, textvariable=translated_text_var, wraplength=250)
translated_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

# Run the GUI
root.mainloop()
