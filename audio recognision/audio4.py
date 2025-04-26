import tkinter as tk
from tkinter import messagebox
import speech_recognition as sr
from transformers import pipeline
import threading

# Setup sentiment analysis model
sentiment_analyzer = pipeline("sentiment-analysis")

# Function to get speech input
def get_voice_input():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return None

# Function to respond based on mood
def generate_response(text):
    result = sentiment_analyzer(text)[0]
    label = result['label']
    score = result['score']

    if label == "POSITIVE":
        return "😊 I'm glad you're feeling good today!", label, score
    elif label == "NEGATIVE":
        return "💙 I'm here for you. Take it slow and be kind to yourself.", label, score
    else:
        return "📝 Thanks for sharing. Every emotion is valid.", label, score

# Function to handle voice input and update UI
def start_mood_check():
    status_label.config(text="🎙️ Listening...", fg="orange")
    threading.Thread(target=process_voice_input).start()

def process_voice_input():
    mood_text = get_voice_input()

    if mood_text:
        response, sentiment, confidence = generate_response(mood_text)
        text_display.config(state='normal')
        text_display.delete(1.0, tk.END)
        text_display.insert(tk.END, "💭 You said:\n", "heading")
        text_display.insert(tk.END, f"{mood_text}\n\n")
        text_display.insert(tk.END, "🎯 Sentiment Analysis:\n", "heading")
        text_display.insert(tk.END, f"{sentiment} (Confidence: {confidence:.2f})\n\n")
        text_display.insert(tk.END, "🤖 AI Response:\n", "heading")
        text_display.insert(tk.END, f"{response}")
        text_display.tag_configure("heading", font=("Calibri", 13, "bold"), foreground="#DB7093")
        text_display.config(state='disabled')
        status_label.config(text="✨ Mood analysis complete!", fg="#FF1493")
    else:
        messagebox.showerror("Error", "Couldn't understand you. Please try again.")
        status_label.config(text="❌ Error recognizing speech.", fg="red")

# Create GUI with enhanced styling
app = tk.Tk()
app.title("🌟 MoodCheck AI")
app.geometry("700x600")  # Slightly larger window
app.resizable(False, False)
app.configure(bg="#FFF0F5")  # Lighter pink background

# Custom Fonts
TITLE_FONT = ("Candara", 28, "bold")
BUTTON_FONT = ("Candara", 16, "bold")
TEXT_FONT = ("Calibri", 13)
STATUS_FONT = ("Calibri", 13, "italic")

# Create main container with padding
main_frame = tk.Frame(app, bg="#FFF0F5", padx=30, pady=20)
main_frame.pack(fill='both', expand=True)

# Decorative header
header_frame = tk.Frame(main_frame, bg="#FFF0F5")
header_frame.pack(fill='x', pady=(0, 20))

title_label = tk.Label(
    header_frame,
    text="✨ Welcome to MoodCheck AI ✨",
    font=TITLE_FONT,
    bg="#FFF0F5",
    fg="#FF1493"  # Deep pink for title
)
title_label.pack(pady=(10, 5))

subtitle_label = tk.Label(
    header_frame,
    text="Share your thoughts, and I'll analyze your mood",
    font=("Calibri", 14, "italic"),
    bg="#FFF0F5",
    fg="#DB7093"
)
subtitle_label.pack()

# Enhanced button styling
def on_enter(e):
    record_button.config(bg="#FF1493", fg="white")

def on_leave(e):
    record_button.config(bg="#DB7093", fg="white")

record_button = tk.Button(
    main_frame,
    text="🎤  Start Mood Check  🎤",
    font=BUTTON_FONT,
    bg="#DB7093",
    fg="white",
    activebackground="#FF1493",
    activeforeground="white",
    command=start_mood_check,
    bd=0,  # Flat design
    relief="flat",
    padx=20,
    pady=10,
    cursor="hand2"  # Hand cursor on hover
)
record_button.pack(pady=20)
record_button.bind("<Enter>", on_enter)
record_button.bind("<Leave>", on_leave)

# Enhanced text display
text_frame = tk.Frame(main_frame, bg="#FFF0F5", pady=10)
text_frame.pack(fill='both', expand=True)

text_display = tk.Text(
    text_frame,
    height=12,
    width=60,
    font=TEXT_FONT,
    bd=0,
    relief="flat",
    wrap="word",
    bg="#FFFFFF",  # White background
    padx=15,
    pady=15
)
text_display.pack(pady=10)
text_display.config(state='disabled')

# Add a decorative border around text display
text_border = tk.Frame(
    text_frame,
    bg="#DB7093",
    padx=2,
    pady=2
)
text_border.place(relwidth=1, relheight=1, anchor='center')
text_display.lift()  # Bring text display to front

# Enhanced status label
status_label = tk.Label(
    main_frame,
    text="",
    font=STATUS_FONT,
    bg="#FFF0F5",
    fg="#DB7093"
)
status_label.pack(pady=15)

app.mainloop()
