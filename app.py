from flask import Flask, request, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Serwer AudioStitcher v4 (Cobalt Engine) działa!", 200

@app.route('/download')
def download():
    video_url = request.args.get('url')
    if not video_url:
        return "Brak URL", 400

    # Konfiguracja zapytania do Cobalt API
    # Pobieramy tylko audio, w formacie mp3
    cobalt_api_url = "https://api.cobalt.tools/api/json"
    payload = {
        "url": video_url,
        "isAudioOnly": True,
        "audioFormat": "mp3",
        "vCodec": "h264", # standard
        "aCodec": "mp3",
        "isNoTTWatermark": True
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        # 1. Prosimy Cobalt o wygenerowanie linku do pliku
        response = requests.post(cobalt_api_url, json=payload, headers=headers)
        data = response.json()

        if data.get('status') == 'stream' or data.get('status') == 'picker':
            file_url = data.get('url')
            
            # 2. Pobieramy plik z Cobalt i przesyłamy do Twojej strony
            def generate():
                r = requests.get(file_url, stream=True)
                for chunk in r.iter_content(chunk_size=256 * 1024):
                    yield chunk

            return Response(generate(), mimetype="audio/mpeg", headers={
                "Content-Disposition": "attachment; filename=audio.mp3",
                "Access-Control-Allow-Origin": "*"
            })
        else:
            return f"Cobalt Error: {data.get('text', 'Unknown error')}", 500

    except Exception as e:
        return f"Serwer Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)    app.run(host='0.0.0.0', port=10000)
