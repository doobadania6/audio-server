from flask import Flask, request, Response, redirect
from flask_cors import CORS
import requests
import random

app = Flask(__name__)
CORS(app)

# Lista publicznych instancji Invidious, które zazwyczaj działają dobrze
INSTANCES = [
    'https://invidious.snopyta.org',
    'https://yewtu.be',
    'https://vid.puffyan.us',
    'https://invidious.kavin.rocks',
    'https://inv.vern.cc'
]

@app.route('/')
def home():
    return "Serwer AudioStitcher v3 (Invidious Proxy) działa!", 200

@app.route('/download')
def download():
    video_url = request.args.get('url')
    if not video_url:
        return "Brak URL", 400

    # Wyciągamy ID filmu z linku
    video_id = ""
    if "v=" in video_url:
        video_id = video_url.split("v=")[1].split("&")[0]
    elif "be/" in video_url:
        video_id = video_url.split("be/")[1].split("?")[0]

    if not video_id:
        return "Nieprawidłowy ID filmu", 400

    # Próbujemy pobrać link audio z różnych instancji Invidious
    random.shuffle(INSTANCES)
    for instance in INSTANCES:
        try:
            api_url = f"{instance}/api/v1/videos/{video_id}"
            data = requests.get(api_url, timeout=5).json()
            
            # Szukamy strumienia audio
            audio_streams = [f for f in data.get('adaptiveFormats', []) if 'audio/' in f.get('type', '')]
            if audio_streams:
                # Wybieramy najlepszą jakość audio
                best_audio = sorted(audio_streams, key=lambda x: int(x.get('bitrate', 0)), reverse=True)[0]
                final_url = best_audio['url']
                
                # Przesyłamy strumień do użytkownika
                def generate():
                    r = requests.get(final_url, stream=True, timeout=30)
                    for chunk in r.iter_content(chunk_size=256 * 1024):
                        yield chunk
                
                return Response(generate(), mimetype="audio/mpeg", headers={
                    "Content-Disposition": "attachment; filename=audio.mp3",
                    "Access-Control-Allow-Origin": "*"
                })
        except:
            continue # Jeśli jedna instancja zawiedzie, próbuje następnej

    return "Wszystkie instancje Invidious są obecnie przeciążone. Spróbuj za minutę.", 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
