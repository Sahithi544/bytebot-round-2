import json
import os
import sounddevice as sd
import wavio
import speech_recognition as sr
from gtts import gTTS
from googletrans import Translator
from fuzzywuzzy import fuzz
import spacy
import playsound
import re
from datetime import datetime

# Load NLP model and translator once
nlp = spacy.load("en_core_web_md")
translator = Translator()

# Load FAQ (your existing faq_data.json)
with open("faq_data.json", "r", encoding="utf-8") as f:
    faq = json.load(f)

# Response cache
response_cache = {}

LOG_FILE = "conversation_log.txt"

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def get_audio():
    """Record short audio from server mic and return transcript + detected language."""
    fs = 44100
    duration = 1.7  # seconds (adjust if needed)
    filename = "input.wav"
    print("🎤 Listening... Speak now.")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    wavio.write(filename, recording, fs, sampwidth=2)

    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)

    try:
        transcript = recognizer.recognize_google(audio)
        lang = detect_language(transcript)
        print(f"🗣 You said: {transcript}")
        print(f"🌐 Language Detected: {lang}")
        return transcript.lower(), lang
    except sr.UnknownValueError:
        return "", "en"
    except Exception as e:
        print("Speech recognition error:", e)
        return "", "en"

def detect_language(text):
    try:
        lang = translator.detect(text).lang
        return lang if lang in ["en", "hi", "te", "ta", "kn"] else "en"
    except Exception:
        return "en"

def find_best_match(user_input):
    """Return best matching question key from faq or None."""
    user_input_proc = preprocess(user_input)
    best_score = 0
    best_question = None

    for question in faq:
        question_proc = preprocess(question)
        try:
            nlp_score = nlp(user_input_proc).similarity(nlp(question_proc))
        except Exception:
            nlp_score = 0
        fuzzy_score = fuzz.ratio(user_input_proc, question_proc) / 100
        keyword_bonus = 0.2 if any(word in user_input_proc for word in question_proc.split()) else 0
        final_score = (nlp_score + fuzzy_score) / 2 + keyword_bonus

        if final_score > best_score:
            best_score = final_score
            best_question = question

    return best_question if best_score > 0.65 else None

def speak(text, lang_code):
    """Speak text using gTTS in the requested language code (defaults to en)."""
    try:
        # translate if needed (we're keeping simple: reply is in English)
        translated = text
        print(f"🤖 Bot says: {translated}")
        tts = gTTS(text=translated, lang='en')  # using English TTS for simplicity
        filename = "response.mp3"
        tts.save(filename)
        playsound.playsound(filename)
        os.remove(filename)
    except Exception as e:
        print("Speech (TTS) error:", e)

def log_conversation(user_text, bot_text, lang):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] User ({lang}): {user_text}\n")
        f.write(f"[{timestamp}] Bot: {bot_text}\n\n")

def chatbot():
    """
    Main entry used by Flask app.
    Records audio (server mic), recognizes text, finds FAQ match, speaks and logs result,
    and returns (user_text, bot_reply).
    """
    user_input, user_lang = get_audio()

    if not user_input:
        response = "Sorry, I couldn't understand that."
    elif user_input in response_cache:
        response = response_cache[user_input]
        print("⚡ From Cache")
    else:
        # For matching, translate to English if not English (but keep responses English)
        try:
            translated_input = translator.translate(user_input, dest="en").text if user_lang != "en" else user_input
        except Exception:
            translated_input = user_input

        best_match = find_best_match(translated_input)
        response = faq[best_match] if best_match else "I'm sorry, I don't have an answer to that."
        response_cache[user_input] = response

    # speak the response (English)
    speak(response, user_lang)

    # log conversation
    log_conversation(user_input, response, user_lang)

    # return values to Flask so frontend can display them
    return user_input, response
