from flask import Flask, render_template, jsonify
from chatbot import chatbot  # chatbot() returns (user_text, bot_reply)
import os

app = Flask(__name__, template_folder="templates")

@app.route("/")
def home():
    return render_template("chatbot.html")

@app.route("/ask", methods=["POST"])
def ask():
    try:
        user_text, bot_reply = chatbot()  # server-side recording + processing
        return jsonify({"user": user_text, "reply": bot_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Run on default 127.0.0.1:5000
    app.run(debug=True)
