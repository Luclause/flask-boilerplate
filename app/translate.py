import json
import requests
from flask_babel import _
from app import app

def translate(text, source_language, dest_language):
    if 'MS_TRANSLATOR_KEY' not in app.config or \
        not app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured.')

    params = {
        'api-version': '3.0',
        'from': source_language,
        'to': dest_language
    }

    header = {
        'Ocp-Apim-Subscription-Key': app.config['MS_TRANSLATOR_KEY'],
        'Ocp-Apim-Subscription-Region': 'australiaeast'
    }

    body = [
        {'Text': text}
    ]

    r = requests.post(
        url = 'https://api.cognitive.microsofttranslator.com/translate',
        params = params,
        headers = header,
        json = body
    )

    if r.status_code != 200:
        return _('Error: the translation service failed.')

    return json.loads(r.content.decode('utf-8-sig'))[0]['translations'][0]['text']