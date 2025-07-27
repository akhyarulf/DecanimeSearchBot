from flask import Flask, request
import requests

TOKEN = '7968583463:AAFcqxbNbXdaTYxaaQZGnoG3-mGLu3prx4E'  # ganti dengan token kamu
URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot aktif di Glitch!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')

        if text.startswith('?s '):
            query = text[3:]
            reply = f"Hasil pencarian untuk: {query}"
            # Tambah scraping decanime di sini
        else:
            reply = "Gunakan format: ?s judul"

        requests.post(URL, json={'chat_id': chat_id, 'text': reply})
    return '', 200

if __name__ == '__main__':
    app.run()
