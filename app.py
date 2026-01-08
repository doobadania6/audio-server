from flask import Flask, request, Response
from flask_cors import CORS
import yt_dlp
import io

app = Flask(__name__)
CORS(app) # Pozwala Twojej stronie na GitHubie łączyć się z serwerem

@app.route('/download')
def download():
    url = request.args.get('url')
    if not url:
        return "Brak URL", 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        # Ta opcja pomaga omijać blokady bez ciasteczek
        'nocheckcertificate': True,
        'outtmpl': '-',
        'logtostderr': True,
    }

    def generate():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            
            # Przesyłamy strumień audio bezpośrednio do przeglądarki
            import requests
            r = requests.get(audio_url, stream=True)
            for chunk in r.iter_content(chunk_size=1024*1024):
                yield chunk

    return Response(generate(), mimetype="audio/mpeg", 
                    headers={"Content-Disposition": "attachment; filename=audio.mp3"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
