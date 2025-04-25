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
root.title("AR Glasses Assistant")
root.attributes('-fullscreen', True)


# Video frame
video_label = Label(root)
video_label.pack(fill=tk.BOTH, expand=True)


bottom_text = tk.StringVar()
bottom_label = tk.Label(root, textvariable=bottom_text, font=("Arial", 16), bg="black", fg="white")
bottom_label.place(relx=0.5, rely=0.95, anchor=tk.S)


bottom_text2=tk.StringVar()
bottom_label2=tk.Label(root, textvariable=bottom_text2, font=("Arial", 16), bg="black", fg="white")
bottom_label2.place(relx=0.5, rely=0.9, anchor=tk.S)


bottom_text3=tk.StringVar()
bottom_label3=tk.Label(root, textvariable=bottom_text3, font=("Arial", 16), bg="black", fg="white")
bottom_label3.place(relx=0.9, rely=0.5, anchor=tk.S)

bottom_text4=tk.StringVar()
bottom_label4=tk.Label(root, textvariable=bottom_text4, font=("Arial", 16), bg="black", fg="white")
bottom_label4.place(relx=0.1, rely=0.5, anchor=tk.S)

model_path = vosk_model_paths["en"]
model = Model(model_path)
eng_model, eng_tokenizer = translate_en()

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

def update_camera():
    while True:
        ret, frame = cap.read()
        if ret:
            w = video_label.winfo_width()
            h = video_label.winfo_height()
            frame = cv2.resize(frame, (w, h))

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(Image.fromarray(frame))
            video_label.config(image=img)
            video_label.image = img
        time.sleep(0.03)

def display_output(text):
    bottom_text.set(text)
def display_output2(text):
    bottom_text2.set(text)
def display_output3(text): 
    bottom_text3.set(text)
def display_output4(text):
    bottom_text4.set(text)

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
                x = translate_model(l1, l2)
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
                            translated_text = translate_text(text, x)
                            display_output4(f"Translated: {translated_text}")
                            speak(translated_text)
                        else:
                            display_output2("No text recognized")
                            speak("No text recognized")

            elif data == "image":
                l1 = get_lang1(model, display_output, display_output2)
                l2 = get_lang2(model, display_output, display_output2)
                loading_label = show_loading_screen("Loading image translation...")
                m = translate_model(l1, l2)
                hide_loading_screen(loading_label)
                
                while True:
                    if m:
                        pass
                    else:
                        break
                    model = reset(model_path)
                    capture_image_from_camera(cap, model, display_output, display_output2)
                    if capture_image_from_camera(cap, model, display_output, display_output2):
                        pass
                    else:
                        break
                    filename = "captured_image.jpg"
                    file1 = filepath(filename)
                    lang = img_lang_det(l1)
                    t = recognize_text(file1, lang)
                    print(t)
                    display_output3(f"Image Text: {t}")
                    translated_text = translate_text(t, m)
                    speak(translated_text)
                    display_output4(f"Translated: {translated_text}")
                    print(translated_text)
                    speak("do you want to continue yes or no")
                    display_output2("do you want to continue yes or no")
                    model = reset(model_path)
                    b = get_audio(model, display_output, display_output2)
                    if b == "yes":
                        pass
                    else:
                        break
                        
threading.Thread(target=update_camera, daemon=True).start()
threading.Thread(target=voice_loop, daemon=True).start()

root.mainloop()
cap.release()
