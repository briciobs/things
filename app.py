from flask import Flask, request
import requests

app = Flask(__name__)

# Configurações
TELEGRAM_TOKEN = '7918365164:AAEWb87TDtNhxuqXGjgZr7xfRS-jj6Oce8I'
CHATGPT_API_KEY = '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'
THINGSBOARD_URL = 'https://demo.thingsboard.io'
THINGSBOARD_DEVICE_ID = '73a10a10-10c9-11f0-a06a-293553b9bcfe'
THINGSBOARD_TOKEN = 'axy8mmolhkve0ufplsau'

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    user_message = data['message']['text']
    chat_id = data['message']['chat']['id']

    # Consulta dados do ThingsBoard
    headers = {
        'X-Authorization': f'Bearer {THINGSBOARD_TOKEN}'
    }
    params = {
        'keys': 'equipamento,temperatura_1,temperatura_2,temperatura_3,corrente_fase_1,corrente_fase_2,corrente_fase_3,vibacao'
    }
    tb_response = requests.get(
        f'{THINGSBOARD_URL}/api/plugins/telemetry/DEVICE/{THINGSBOARD_DEVICE_ID}/values/timeseries',
        headers=headers,
        params=params
    )
    tb_data = tb_response.json()

    # Preparar dados para o ChatGPT
    prompt = f"""O equipamento '{tb_data.get('equipamento', [{}])[0].get('value', 'desconhecido')}' reportou:
    - Temperatura 1: {tb_data.get('temperatura_1', [{}])[0].get('value', 'N/A')} ºC
    - Temperatura 2: {tb_data.get('temperatura_2', [{}])[0].get('value', 'N/A')} ºC
    - Temperatura 3: {tb_data.get('temperatura_3', [{}])[0].get('value', 'N/A')} ºC
    - Corrente Fase 1: {tb_data.get('corrente_fase_1', [{}])[0].get('value', 'N/A')} A
    - Corrente Fase 2: {tb_data.get('corrente_fase_2', [{}])[0].get('value', 'N/A')} A
    - Corrente Fase 3: {tb_data.get('corrente_fase_3', [{}])[0].get('value', 'N/A')} A
    - Vibração: {tb_data.get('vibacao', [{}])[0].get('value', 'N/A')}

Gere um resumo amigável para o usuário em português."""

    # Chamada para ChatGPT
    gpt_response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {CHATGPT_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'user', 'content': prompt}]
        }
    )

    gpt_message = gpt_response.json()['choices'][0]['message']['content']

    # Enviar resposta no Telegram
    requests.post(
        f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage',
        data={
            'chat_id': chat_id,
            'text': gpt_message
        }
    )

    return '', 200

if __name__ == '__main__':
    app.run()
