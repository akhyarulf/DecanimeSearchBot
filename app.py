from flask import Flask, request
import requests

TOKEN = '7968583463:AAFcqxbNbXdaTYxaaQZGnoG3-mGLu3prx4E'
URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

app = Flask(__name__)

@app.route('/')
def index():
    return 'Bot is running on Koyeb!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    chat_id = data['message']['chat']['id']
    text = data['message'].get('text', '')

    if text.startswith('?s '):
        query = text[3:]
        reply = f"Hasil pencarian untuk: {query}"
        # Tambahkan logic scraping decanime di sini

        requests.post(URL, json={'chat_id': chat_id, 'text': reply})
    return '', 200

if __name__ == '__main__':
    app.run()