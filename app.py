from flask import Flask, request, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
# CORS pozwala Twojej stronie na GitHub Pages łączyć się z tym serwerem
CORS(app)

@app.route('/')
def home():
    return "Serwer AudioStitcher v4 (Cobalt Engine) działa!", 200

@app.route('/download')
def download():
    video_url = request.args.get('url')
    if not video_url:
        return "Brak URL", 400

    # Konfiguracja zapytania do Cobalt API (najbardziej stabilny silnik)
    cobalt_api_url = "https://api.cobalt.tools/api/json"
    payload = {
        "url": video_url,
        "isAudioOnly": True,
        "audioFormat": "mp3",
        "vCodec": "h264",
        "aCodec": "mp3",
        "isNoTTWatermark": True
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        # 1. Wysyłamy prośbę o wygenerowanie linku do pliku audio
        response = requests.post(cobalt_api_url, json=payload, headers=headers)
        data = response.json()

        # Status 'stream' lub 'picker' oznacza sukces w Cobalt API
        if data.get('status') in ['stream', 'picker', 'redirect']:
            file_url = data.get('url')
            
            # 2. Pobieramy plik z serwera Cobalt i przesyłamy go strumieniowo do Twojej strony
            def generate():
                r = requests.get(file_url, stream=True, timeout=60)
                for chunk in r.iter_content(chunk_size=256 * 1024): # Kawałki po 256KB
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
        else:
            error_msg = data.get('text', 'Nieznany błąd Cobalt')
            print(f"Błąd Cobalt: {error_msg}")
            return f"Błąd Cobalt: {error_msg}", 500

    except Exception as e:
        print(f"Błąd serwera: {str(e)}")
        return f"Serwer Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
