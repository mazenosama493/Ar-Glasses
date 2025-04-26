import tkinter as tk
from tkinter import Label,StringVar
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

# Create a frame for the header that will contain the logo
header_frame = tk.Frame(root, bg='black')
header_frame.pack(side=tk.TOP, fill=tk.X)

# Add the logo to the header
if logo_photo:
    logo_label = tk.Label(header_frame, image=logo_photo, bg='black')
    logo_label.image = logo_photo  # Keep a reference
    logo_label.pack(side=tk.LEFT, padx=10, pady=5)

# Add application title next to the logo
title_label = tk.Label(header_frame, text="AR EyeConic", font=("Arial", 20), 
                      bg='black', fg='white')
title_label.pack(side=tk.LEFT, padx=10)

# Modify your existing video label to account for the header
video_label = Label(root)
video_label.pack(fill=tk.BOTH, expand=True)


# First, let's create a modern frame to contain all the text elements
text_display_frame = tk.Frame(root, bg='#121212')  # Dark background
text_display_frame.place(relx=0, rely=0.7, relwidth=1, relheight=0.3)  # Takes bottom 30% of screen

# Custom font setup
custom_font = ("Segoe UI", 14)  # More modern than Arial
title_font = ("Segoe UI Semibold", 16)

# Main interaction text (previously bottom_text2)
interaction_frame = tk.Frame(text_display_frame, bg='#1E1E1E', bd=0, highlightthickness=0)
interaction_frame.pack(fill=tk.X, padx=20, pady=(10, 5))

interaction_text = tk.StringVar()
interaction_label = tk.Label(
    interaction_frame, 
    textvariable=interaction_text, 
    font=title_font,
    bg='#1E1E1E',
    fg='#4FC3F7',  # Light blue accent color
    justify=tk.LEFT,
    wraplength=root.winfo_screenwidth() - 40  # Auto-wrap text
)
interaction_label.pack(fill=tk.X, padx=10, pady=5)

# Assistant response text (previously bottom_text)
response_frame = tk.Frame(text_display_frame, bg='#1E1E1E', bd=0, highlightthickness=0)
response_frame.pack(fill=tk.X, padx=20, pady=5)

response_text = tk.StringVar()
response_label = tk.Label(
    response_frame, 
    textvariable=response_text, 
    font=custom_font,
    bg='#1E1E1E',
    fg='#FFFFFF',  # Pure white
    justify=tk.LEFT,
    wraplength=root.winfo_screenwidth() - 40
)
response_label.pack(fill=tk.X, padx=10, pady=5)

# Translated text display (previously bottom_text4)
translation_frame = tk.Frame(text_display_frame, bg='#252525', bd=0, highlightthickness=0)
translation_frame.pack(fill=tk.X, padx=20, pady=5)

translation_text = tk.StringVar()
translation_label = tk.Label(
    translation_frame, 
    textvariable=translation_text, 
    font=custom_font,
    bg='#252525',
    fg='#81C784',  # Soft green for translations
    justify=tk.LEFT,
    wraplength=root.winfo_screenwidth() - 40
)
translation_label.pack(fill=tk.X, padx=10, pady=5)

# Image text display (previously bottom_text3)
image_text_frame = tk.Frame(text_display_frame, bg='#252525', bd=0, highlightthickness=0)
image_text_frame.pack(fill=tk.X, padx=20, pady=(5, 10))

image_text = tk.StringVar()
image_text_label = tk.Label(
    image_text_frame, 
    textvariable=image_text, 
    font=custom_font,
    bg='#252525',
    fg='#FFB74D',  # Soft orange for image text
    justify=tk.LEFT,
    wraplength=root.winfo_screenwidth() - 40
)
image_text_label.pack(fill=tk.X, padx=10, pady=5)

# Add subtle separators between sections
separator_style = {"bg": "#333333", "height": 1}
tk.Frame(text_display_frame, **separator_style).pack(fill=tk.X, pady=2)

background_label = Label(root, bg='black')  # Background label
background_label.pack(fill=tk.BOTH, expand=True)

# Camera control variables
camera_running = True
camera_thread = None

def show_loading_screen(message="Loading translation model..."):
    global camera_running
    
    # Stop camera
    camera_running = False
    time.sleep(0.1)  # Give thread time to stop
    
    # Hide video and show background
    video_label.pack_forget()
    background_label.pack(fill=tk.BOTH, expand=True)
    
    # Create loading text
    loading_text = tk.StringVar()
    loading_text.set(message)
    loading_label = tk.Label(root, textvariable=loading_text, 
                            font=("Arial", 24), bg="black", fg="white")
    loading_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    root.update()
    return loading_label

def hide_loading_screen(loading_label):
    global camera_running, camera_thread
    
    # Remove loading elements
    loading_label.destroy()
    background_label.pack_forget()
    
    # Restart camera
    video_label.pack(fill=tk.BOTH, expand=True)
    camera_running = True
    if camera_thread is None or not camera_thread.is_alive():
        camera_thread = threading.Thread(target=update_camera, daemon=True)
        camera_thread.start()

# OpenCV setup
cap = cv2.VideoCapture(0)

model_path = vosk_model_paths["en"]
model = Model(model_path)
eng_model, eng_tokenizer = translate_en()

camera_running = True
camera_thread = None

def update_camera():
    while camera_running:
        ret, frame = cap.read()
        if ret:
            # Get available space (window height minus header)
            w = video_label.winfo_width()
            h = root.winfo_height() - header_frame.winfo_height()
            
            # Only resize if we have valid dimensions
            if w > 0 and h > 0:
                frame = cv2.resize(frame, (w, h))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = ImageTk.PhotoImage(Image.fromarray(frame))
                video_label.config(image=img)
                video_label.image = img
        time.sleep(0.03)

def display_output(text):
    """For assistant responses"""
    response_text.set(text)

def display_output2(text):
    """For user interactions/questions"""
    interaction_text.set(text)

def display_output3(text): 
    """For image text recognition"""
    image_text.set(f"Image Text: {text}")

def display_output4(text):
    """For translations"""
    translation_text.set(f"Translated: {text}")

def voice_loop():
    user = "mazen"
    global model_path, model

    while True:
        model = reset(model_path)
        text = get_audio(model, display_output, display_output2)
        if "hi david" in text:
            if connected_func(model, display_output, display_output2):
                break
            else:
                pass
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
                x = translate_model(l1, l2,display_output2)
                hide_loading_screen(loading_label)
                
                while True:
                    if x:
                        pass
                    else:
                        break
                    text = get_audio(model, display_output, display_output2)
                    if text == "get out" or translate_to_english(text, eng_model, eng_tokenizer).lower().strip("!? .") == "get out":
                        display_output2("i will be happy to help you good bye")
                        speak("i will be happy to help you good bye")
                        break
                    else:
                        if text:
                            translated_text = translate_text(text, x,display_output2)
                            display_output4(f"Translated: {translated_text}")
                            speak(translated_text)
                        else:
                            display_output2("No text recognized")
                            speak("No text recognized")

            elif data == "image":
                l3 = get_lang3(model, display_output, display_output2)
                l2 = get_lang2(model, display_output, display_output2)
                loading_label = show_loading_screen("Loading image translation...")
                m = translate_model(l3, l2,display_output2)
                hide_loading_screen(loading_label)
                
                while True:
                    if m:
                        pass
                    else:
                        break
                    model = reset(model_path)
                    if capture_image_from_camera(cap, model, display_output, display_output2):
                        pass
                    else:
                        break
                    filename = "captured_image.jpg"
                    file1 = filepath(filename)
                    lang = img_lang_det(l3)
                    t = recognize_text(file1, lang)
                    print(t)
                    display_output3(f"Image Text: {t}")
                    translated_text = translate_text(t, m,display_output2)
                    speak(translated_text)
                    display_output4(f"Translated: {translated_text}")
                    print(translated_text)
                    if detect_continue(model, display_output2):
                        pass
                    else:
                        break
                        
threading.Thread(target=update_camera, daemon=True).start()
threading.Thread(target=voice_loop, daemon=True).start()

root.mainloop()
cap.release()
