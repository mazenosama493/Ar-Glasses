import tkinter as tk
from tkinter import Label, StringVar
from PIL import Image, ImageTk
import cv2
import threading
import time
from functions import *
from dic import *
from vosk import Model

# Setup GUI
root = tk.Tk()
root.title("AR EyeConic")
root.attributes('-fullscreen', True)

try:
    logo_image = Image.open("logo.png")
    logo_image = logo_image.resize((100, 100), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_image)
except Exception as e:
    print(f"Error loading logo: {e}")
    logo_photo = None

# Header Frame
header_frame = tk.Frame(root, bg='black')
header_frame.pack(side=tk.TOP, fill=tk.X)

if logo_photo:
    logo_label = tk.Label(header_frame, image=logo_photo, bg='black')
    logo_label.image = logo_photo
    logo_label.pack(side=tk.LEFT, padx=10, pady=5)

title_label = tk.Label(header_frame, text="AR EyeConic", font=("Arial", 20), 
                      bg='black', fg='white')
title_label.pack(side=tk.LEFT, padx=10)

# Main Content Frame
content_frame = tk.Frame(root, bg='black')
content_frame.pack(fill=tk.BOTH, expand=True)

# Left Panel - Text Display (30% width)
left_panel = tk.Frame(content_frame, bg='#121212', width=int(root.winfo_screenwidth()*0.3))
left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
left_panel.pack_propagate(False)

# Right Panel - Camera View (70% width)
right_panel = tk.Frame(content_frame, bg='black')
right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

video_label = Label(right_panel)
video_label.pack(fill=tk.BOTH, expand=True)

# Text Display Elements
custom_font = ("Segoe UI", 12)
title_font = ("Segoe UI Semibold", 14)

# Interaction Text
interaction_frame = tk.Frame(left_panel, bg='#1E1E1E')
interaction_frame.pack(fill=tk.X, padx=5, pady=(5, 2), expand=True)

interaction_text = tk.StringVar()
interaction_label = tk.Label(
    interaction_frame, 
    textvariable=interaction_text, 
    font=title_font,
    bg='#1E1E1E',
    fg='#4FC3F7',
    justify=tk.LEFT,
    wraplength=int(root.winfo_screenwidth()*0.3) - 20,
    anchor='w'
)
interaction_label.pack(fill=tk.X, padx=5, pady=2, expand=True)

# Response Text
response_frame = tk.Frame(left_panel, bg='#1E1E1E')
response_frame.pack(fill=tk.X, padx=5, pady=2, expand=True)

response_text = tk.StringVar()
response_label = tk.Label(
    response_frame, 
    textvariable=response_text, 
    font=custom_font,
    bg='#1E1E1E',
    fg='#FFFFFF',
    justify=tk.LEFT,
    wraplength=int(root.winfo_screenwidth()*0.3) - 20,
    anchor='w'
)
response_label.pack(fill=tk.X, padx=5, pady=2, expand=True)

# Translation Text
translation_frame = tk.Frame(left_panel, bg='#252525')
translation_frame.pack(fill=tk.X, padx=5, pady=2, expand=True)

translation_text = tk.StringVar()
translation_label = tk.Label(
    translation_frame, 
    textvariable=translation_text, 
    font=custom_font,
    bg='#252525',
    fg='#81C784',
    justify=tk.LEFT,
    wraplength=int(root.winfo_screenwidth()*0.3) - 20,
    anchor='w'
)
translation_label.pack(fill=tk.X, padx=5, pady=2, expand=True)

# Image Text
image_text_frame = tk.Frame(left_panel, bg='#252525')
image_text_frame.pack(fill=tk.X, padx=5, pady=(2, 5), expand=True)

image_text = tk.StringVar()
image_text_label = tk.Label(
    image_text_frame, 
    textvariable=image_text, 
    font=custom_font,
    bg='#252525',
    fg='#FFB74D',
    justify=tk.LEFT,
    wraplength=int(root.winfo_screenwidth()*0.3) - 20,
    anchor='w'
)
image_text_label.pack(fill=tk.X, padx=5, pady=2, expand=True)

# Separator
tk.Frame(left_panel, bg='#333333', height=1).pack(fill=tk.X, pady=1)

background_label = Label(root, bg='black')
background_label.pack(fill=tk.BOTH, expand=True)

# Camera Control
camera_running = True
camera_thread = None

def show_loading_screen(message="Loading..."):
    global camera_running
    camera_running = False
    time.sleep(0.1)
    video_label.pack_forget()
    background_label.pack(fill=tk.BOTH, expand=True)
    loading_text = tk.StringVar()
    loading_text.set(message)
    loading_label = tk.Label(root, textvariable=loading_text, 
                           font=("Arial", 24), bg="black", fg="white")
    loading_label.place(relx=0.65, rely=0.5, anchor=tk.CENTER)
    root.update()
    return loading_label

def hide_loading_screen(loading_label):
    global camera_running, camera_thread
    loading_label.destroy()
    background_label.pack_forget()
    video_label.pack(fill=tk.BOTH, expand=True)
    camera_running = True
    if camera_thread is None or not camera_thread.is_alive():
        camera_thread = threading.Thread(target=update_camera, daemon=True)
        camera_thread.start()

# Camera Setup
cap = cv2.VideoCapture(0)
model_path = vosk_model_paths["en"]
model = Model(model_path)
eng_model, eng_tokenizer = translate_en()

def update_camera():
    while camera_running:
        ret, frame = cap.read()
        if ret:
            w = video_label.winfo_width()
            h = video_label.winfo_height()
            if w > 0 and h > 0:
                frame = cv2.resize(frame, (w, h))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = ImageTk.PhotoImage(Image.fromarray(frame))
                video_label.config(image=img)
                video_label.image = img
        time.sleep(0.03)

def display_output(text):
    response_text.set(text)
    left_panel.update_idletasks()

def display_output2(text):
    interaction_text.set(text)
    left_panel.update_idletasks()

def display_output3(text):
    image_text.set(f"Image Text: {text}")
    left_panel.update_idletasks()

def display_output4(text):
    translation_text.set(f"Translated: {text}")
    left_panel.update_idletasks()

def voice_loop():
    user = "mazen"
    global model_path, model

    while True:
        model = reset(model_path)
        if not display_output2("Say Hi to David"):
            display_output2("Say Hi to David")
        text = get_audio(model, display_output, display_output2)
        if "hi david" in text:
            if connected_func(model, display_output, display_output2):
                break
            display_output2(f"Hello {user}, how are you?")
            speak(f"hello {user} how are you")
            data = tool_detection(model, display_output, display_output2)

            if data == "speech":
                l1 = get_lang1(model, display_output, display_output2)
                l2 = get_lang2(model, display_output, display_output2)
                if l1 != "en":
                    model_path = recognition_model(l1)
                    model = Model(model_path)
                loading_label = show_loading_screen("Loading speech translation...")
                x = translate_model(l1, l2, display_output2)
                hide_loading_screen(loading_label)
                
                while True:
                    if not x:
                        break
                    text = get_audio(model, display_output, display_output2)
                    if text == "get out" or translate_to_english(text, eng_model, eng_tokenizer).lower().strip("!? .") == "get out":
                        display_output2("Goodbye!")
                        speak("Goodbye!")
                        display_output4("")
                        break
                    if text:
                        translated_text = translate_text(text, x, display_output2)
                        display_output4(translated_text)
                        speak(translated_text)
                    else:
                        display_output2("No text recognized")
                        speak("No text recognized")

            elif data == "image":
                l3 = get_lang3(model, display_output, display_output2)
                l2 = get_lang2(model, display_output, display_output2)
                loading_label = show_loading_screen("Loading image translation...")
                m = translate_model(l3, l2, display_output2)
                hide_loading_screen(loading_label)
                
                while True:
                    if not m:
                        break
                    model = reset(model_path)
                    if not capture_image_from_camera(cap, model, display_output, display_output2):
                        break
                    filename = "captured_image.jpg"
                    file1 = filepath(filename)
                    lang = img_lang_det(l3)
                    t = recognize_text(file1, lang)
                    display_output3(t)
                    translated_text = translate_text(t, m, display_output2)
                    speak(translated_text)
                    display_output4(translated_text)
                    if not detect_continue(model, display_output2):
                        display_output2("Goodbye!")
                        speak("Goodbye!")
                        display_output4("")
                        display_output3("")
                        break

# Start threads
threading.Thread(target=update_camera, daemon=True).start()
threading.Thread(target=voice_loop, daemon=True).start()

root.mainloop()
cap.release()