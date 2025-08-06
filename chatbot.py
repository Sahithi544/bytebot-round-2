
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

# Load NLP model and Translator
nlp = spacy.load("en_core_web_md")
translator = Translator()

# Load knowledge base
with open("faq_data.json", "r", encoding="utf-8") as f:
    faq = json.load(f)

# Cache responses
response_cache = {}

# Preprocess text
def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

# Record and recognize voice
def get_audio():
    fs = 44100
    duration = 1.7
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
        print(f"🗣 You said: {transcript}")
        lang = detect_language(transcript)
        print(f"🌐 Language Detected: {lang}")
        return transcript.lower(), lang
    except:
        return "", "en"

# Detect language
def detect_language(text):
    try:
        lang = translator.detect(text).lang
        return lang if lang in ["en", "hi", "te", "ta", "kn"] else "en"
    except:
        return "en"

# Match user question
def find_best_match(user_input):
    user_input = preprocess(user_input)
    best_score = 0
    best_question = None

    for question in faq:
        question_processed = preprocess(question)
        nlp_score = nlp(user_input).similarity(nlp(question_processed))
        fuzzy_score = fuzz.ratio(user_input, question_processed) / 100
        keyword_bonus = 0.2 if any(word in user_input for word in question_processed.split()) else 0
        final_score = (nlp_score + fuzzy_score) / 2 + keyword_bonus

        if final_score > best_score:
            best_score = final_score
            best_question = question

    return best_question if best_score > 0.65 else None

# Speak reply
def speak(text, lang_code):
    try:
        translated = translator.translate(text, dest=lang_code).text if lang_code != "en" else text
        print(f"🤖 Bot says: {translated}")
        tts = gTTS(text=translated, lang=lang_code)
        filename = "response.mp3"
        tts.save(filename)
        playsound.playsound(filename)
        os.remove(filename)
    except Exception as e:
        print("❌ Speech Error:", e)

# Main bot
def chatbot():
    user_input, user_lang = get_audio()
    if not user_input:
        response = "Sorry, I couldn't understand that."
    elif user_input in response_cache:
        response = response_cache[user_input]
        print("⚡ From Cache")
    else:
        translated_input = translator.translate(user_input, dest="en").text if user_lang != "en" else user_input
        best_match = find_best_match(translated_input)
        response = faq[best_match] if best_match else "I'm sorry, I don't have an answer to that."
        response_cache[user_input] = response
    speak(response, user_lang) 