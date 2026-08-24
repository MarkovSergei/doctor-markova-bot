import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Токен бота
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8770604625:AAHRjA_vHeE0kSzcnMm3T51OhzcEoklTz9c')

# URL сайта
SITE_URL = 'https://doctor-markova.ru/podpiska'

# Секретный ключ для связи с сайтом
API_KEY = os.environ.get('API_KEY', '')


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


@app.route('/api/grant_access', methods=['POST'])
def grant_access():
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'bad request'})

    api_key = data.get('api_key', '')
    telegram_id = data.get('telegram_id', '')
    invite_link = data.get('invite_link', '')
    end_date = data.get('end_date', '')
    user_name = data.get('user_name', '')
    subscription_name = data.get('subscription_name', '')

    if api_key != API_KEY or not api_key:
        return jsonify({'success': False, 'error': 'wrong key'})

    if not telegram_id or not invite_link:
        return jsonify({'success': False, 'error': 'missing data'})

    # Сообщение клиенту
    client_text = (
        '✅ Оплата получена\n\n'
        f'Подписка: {subscription_name}\n'
        f'Активна до: {end_date}\n\n'
        f'Ссылка на канал:\n{invite_link}\n\n'
        'Нажмите «Вступить» и ожидайте подтверждения.'
    )

    send_message(telegram_id, client_text)

    # Сообщение жене
    admin_chat_id = os.environ.get('ADMIN_CHAT_ID', '')
    if admin_chat_id:
        admin_text = (
            '🔔 Новая оплата\n\n'
            f'Имя: {user_name}\n'
            f'Подписка: {subscription_name}\n'
            f'Ожидайте заявку на вступление в канал.'
        )
        send_message(admin_chat_id, admin_text)

    return jsonify({'success': True})


@app.route('/', methods=['GET'])
def index():
    return 'Bot is running'

@app.route('/test_route', methods=['GET'])
def test_route():
    return 'OK'
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
