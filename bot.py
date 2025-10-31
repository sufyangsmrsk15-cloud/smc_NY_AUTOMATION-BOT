from flask import Flask, request
from datetime import datetime
import requests
import schedule
import time
import threading

app = Flask(__name__)

# ---- Your Keys ----
TELEGRAM_TOKEN = "8240984541:AAGM_pPVfBNFYwx_WLPdGFkzebA_Wa87Wa4"
CHAT_ID = "8410854765"
AI_API_KEY = "AIzaSyAbik-sFqtpI6p-NzZkvScGfoBq-_iAI6E"

ny_session_active = False

# ---- Telegram Send Function ----
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

# ---- Google AI Studio (Gemini) Validation ----
def validate_signal_with_ai(signal_text):
    prompt = f"""
    Analyze this trading alert:
    {signal_text}

    Tell me if it matches Smart Money Concept (stop hunt + CHoCH + imbalance).
    Reply only 'TRUE' if yes, 'FALSE' if fake.
    """
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key=" + AI_API_KEY
    response = requests.post(url, json={"contents":[{"parts":[{"text":prompt}]}]})
    result = response.json()
    return "TRUE" in str(result)

# ---- Flask Webhook ----
@app.route('/webhook', methods=['POST'])
def webhook():
    global ny_session_active
    if not ny_session_active:
        return {"message": "Session inactive"}

    data = request.get_json()
    alert_message = data.get("message", "No message")
    
    if validate_signal_with_ai(alert_message):
        send_telegram(f"✅ Smart Money Setup Confirmed\n\n{alert_message}")
    else:
        send_telegram(f"⚠ Fake signal ignored:\n{alert_message}")
    return {"status": "ok"}

# ---- NY Session Scheduler ----
def start_ny_session():
    global ny_session_active
    ny_session_active = True
    send_telegram("📈 New York Session Started — Smart Money Auto Mode ON")

def end_ny_session():
    global ny_session_active
    ny_session_active = False
    send_telegram("🕓 New York Session Ended — Auto Mode OFF")

schedule.every().day.at("17:30").do(start_ny_session)  # 5:30 PM PKT
schedule.every().day.at("21:30").do(end_ny_session)    # 9:30 PM PKT

def scheduler_thread():
    while True:
        schedule.run_pending()
        time.sleep(60)

threading.Thread(target=scheduler_thread).start()

import os

if _name_ == '_main_':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
