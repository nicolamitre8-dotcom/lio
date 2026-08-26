import os
import time
import requests
from gtts import gTTS
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

TELEGRAM_BOT_TOKEN = "8418320009:AAFQYO8kc8T8_xxgwgBY4ozIPMiwfitR1iQ"
GEMINI_API_KEY = "AQ.Ab8RN6JyEvqvJkRF8LYp_cZoueFSeqZURi"

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

def ask_gemini(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": text}]}]}
    try:
        response = requests.post(url, json=payload, timeout=20)
        res_json = response.json()
        if "candidates" in res_json and len(res_json["candidates"]) > 0:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return "عذراً، لم أتمكن من الحصول على رد."
    except Exception as e:
        return f"حدث خطأ في الاتصال: {e}"

def clean_text_for_tts(text):
    import re
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[*#_`\[\]()~>+=|{}.!?-]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def send_voice(chat_id, text):
    try:
        cleaned = clean_text_for_tts(text)
        if not cleaned:
            cleaned = "محتوى فارغ"
            
        tts = gTTS(text=cleaned, lang='ar', slow=False)
        voice_path = "response.mp3"
        tts.save(voice_path)
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVoice"
        with open(voice_path, 'rb') as f:
            requests.post(url, data={"chat_id": chat_id}, files={"voice": f})
            
        if os.path.exists(voice_path):
            os.remove(voice_path)
    except Exception as e:
        print(f"خطأ في إرسال الصوت: {e}")

def run_bot():
    print("البوت بدأ بالعمل على السحاب...")
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={offset}&timeout=30"
            response = requests.get(url, timeout=35)
            data = response.json()
            
            if "result" in data:
                for update in data["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        user_text = update["message"]["text"]
                        
                        print(f"رسالة واردة: {user_text}")
                        reply = ask_gemini(user_text)
                        
                        send_message(chat_id, reply)
                        send_voice(chat_id, reply)
        except Exception as e:
            print(f"خطأ: {e}")
            time.sleep(5)

if __name__ == '__main__':
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()
    run_bot()
