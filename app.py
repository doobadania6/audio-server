from flask import Flask, request, Response
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__)
# Pozwala na zapytania z Twojej strony na GitHub Pages
CORS(app)

@app.route('/')
def home():
    return "Serwer AudioStitcher działa! Użyj ścieżki /download?url=LINK", 200

@app.route('/download')
def download():
    url = request.args.get('url')
    if not url:
        return "Brak URL", 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        # Udajemy przeglądarkę, by uniknąć blokad "bot"
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            
            # Pobieramy dane z YouTube i przekazujemy je do przeglądarki
            def generate():
                r = requests.get(audio_url, stream=True, timeout=30)
                for chunk in r.iter_content(chunk_size=128 * 1024): # 128KB kawałki
                    if chunk:
                        yield chunk

            return Response(
                generate(),
                mimetype="audio/mpeg",
                headers={
                    "Content-Disposition": f"attachment; filename=audio.mp3",
                    "Access-Control-Allow-Origin": "*" # Dodatkowe zabezpieczenie CORS
                }
            )
    except Exception as e:
        print(f"Błąd: {str(e)}")
        return f"Błąd serwera: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
