import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Токен бота
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8770604625:AAHRjA_vHeE0kSzcnMm3T51OhzcEoklTz9c')

# URL сайта
SITE_URL = 'https://doctor-markova.ru/podpiska'

# Секретный ключ для связи с сайтом
API_KEY = os.environ.get('API_KEY', 'K7mP9xR2vL5nQ8wT3yC6bN4jH1sF0da')


def send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': text
    }
    requests.post(url, json=data, timeout=15)


@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()

    if not update:
        return jsonify({'ok': True})

    # Обработка команды /start
    message = update.get('message')
    if message:
        text = message.get('text', '')
        chat_id = message['chat']['id']
        telegram_id = str(message['from']['id'])

        if text.startswith('/start'):
            # Получаем токен
            parts = text.split(' ')
            token = parts[1] if len(parts) > 1 else ''

            if token:
                # Сообщаем сайту о подтверждении
                confirm_url = f'{SITE_URL}/api/telegram_confirm.php'
                data = {
                    'token': token,
                    'telegram_id': telegram_id,
                    'api_key': API_KEY
                }
                try:
                    r = requests.post(confirm_url, json=data, timeout=15)
                    if r.status_code == 200 and r.json().get('success'):
                        send_message(chat_id, '✅ Telegram подтверждён. Возвращайтесь в личный кабинет.')
                    else:
                        send_message(chat_id, '❌ Не удалось подтвердить. Попробуйте ещё раз.')
                except Exception:
                    send_message(chat_id, '❌ Ошибка связи с сайтом. Попробуйте позже.')
            else:
                send_message(chat_id, 'Здравствуйте! Перейдите по ссылке с сайта для подтверждения.')

    return jsonify({'ok': True})


@app.route('/', methods=['GET'])
def index():
    return 'Bot is running'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
