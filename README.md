# ByteBot – Multilingual Voice-Based AI Insurance Chatbot

## 📌 Overview
**ByteBot** is a multilingual, voice-enabled AI chatbot built for the **InsureBot Quest 2025** hackathon.  
It allows users to ask insurance-related questions in **five languages** — English, Hindi, Telugu, Tamil, and Kannada — and get answers with **voice output**.  

The bot is designed to answer FAQs, explain policies, guide claim processes, and provide details about **ValuEnable** services.

---

## 🚀 Features
- 🎙 **Voice Input & Output** – Speak to the bot and receive spoken replies.
- 🌍 **Multilingual Support** – Real-time translation in 5 languages.
- 📄 **Insurance Knowledge Base** – Powered by `faq_data.json` for quick and accurate answers.
- 📊 **User Interaction Logging** – Tracks queries for improvement.
- ⚡ **Fast & Lightweight** – Runs locally or can be deployed to cloud.

---

## 🛠 Tech Stack
- **Backend:** Python (Flask)
- **Frontend:** HTML, CSS, JavaScript
- **AI & Voice:** SpeechRecognition, gTTS, Deep Translator
- **Knowledge Base:** JSON file

---

## 📥 Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager
- Internet connection (for APIs)

### Steps
```bash
# 1. Clone the repository
git clone https://github.com/Sahithi544/bytebot-round-2.git
cd bytebot-round-2

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the Flask server
python app.py

# 4. Open chatbot.html in your browser
