import os
import requests
from gtts import gTTS

TOKEN = "8418320009:AAFQYO8kc8T8_xxgwgBY4ozIPMiwfitR1iQ"
URL = f"https://api.telegram.org/bot{TOKEN}/"

def get_updates(offset=None):
    params = {'timeout': 100, 'offset': offset}
    response = requests.get(URL + 'getUpdates', params=params)
    return response.json()

def send_message(chat_id, text):
    requests.post(URL + 'sendMessage', json={'chat_id': chat_id, 'text': text})

def main():
    print("Bot is running...")
    offset = None
    while True:
        updates = get_updates(offset)
        if 'result' in updates:
            for update in updates['result']:
                offset = update['update_id'] + 1
                if 'message' in update and 'text' in update['message']:
                    chat_id = update['message']['chat']['id']
                    text = update['message']['text']
                    
                    # رد تجريبي بسيط بالعامية السورية
                    if text == "مرحبة" or text == "مرحبا":
                        send_message(chat_id, "أهلاً ومرحباً يا نقولا، منور يا غالي!")
                    else:
                        send_message(chat_id, f"وصلتني رسالتك: {text}")

if __name__ == '__main__':
    main()
