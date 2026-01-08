from flask import Flask, request, Response
from flask_cors import CORS
import requests
import random

app = Flask(__name__)
CORS(app)

# Lista działających instancji Cobalt (v10+)
COBALT_INSTANCES = [
    "https://api.cobalt.tools/",
    "https://cobalt.hyra.com/",
    "https://api.v0.pw/",
    "https://cobalt.shitty.moe/"
]

@app.route('/')
def home():
    return "Serwer AudioStitcher v6 (Multi-Cobalt) działa!", 200

@app.route('/download')
def download():
    video_url = request.args.get('url')
    if not video_url:
        return "Brak URL", 400

    payload = {
        "url": video_url,
        "videoQuality": "720",
        "audioFormat": "mp3",
        "filenameStyle": "pretty",
        "downloadMode": "audio"
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Losujemy kolejność sprawdzania serwerów
    instances = list(COBALT_INSTANCES)
    random.shuffle(instances)

    for api_url in instances:
        try:
            print(f"Próba pobrania przez: {api_url}")
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                file_url = data.get('url')
                
                if not file_url:
                    continue

                def generate():
                    r = requests.get(file_url, stream=True, timeout=60)
                    for chunk in r.iter_content(chunk_size=256 * 1024):
                        if chunk:
                            yield chunk

                return Response(
                    generate(), 
                    mimetype="audio/mpeg", 
                    headers={
                        "Content-Disposition": "attachment; filename=audio.mp3",
                        "Access-Control-Allow-Origin": "*"
                    }
                )
        except Exception as e:
            print(f"Serwer {api_url} nie odpowiedział: {str(e)}")
            continue

    return "Błąd: Wszystkie serwery Cobalt są obecnie zajęte. Spróbuj ponownie za chwilę.", 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
