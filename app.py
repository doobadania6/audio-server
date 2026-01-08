from flask import Flask, request, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Serwer AudioStitcher v5 (Cobalt v10) działa!", 200

@app.route('/download')
def download():
    video_url = request.args.get('url')
    if not video_url:
        return "Brak URL", 400

    # NOWY ADRES API COBALT (v10)
    cobalt_api_url = "https://api.cobalt.tools/"
    
    # Zaktualizowana struktura parametrów dla v10
    payload = {
        "url": video_url,
        "videoQuality": "720", # wymagane przez API, nawet przy audio
        "audioFormat": "mp3",
        "filenameStyle": "pretty",
        "downloadMode": "audio" # kluczowa zmiana w v10
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        # 1. Wysyłamy prośbę do Cobalt
        response = requests.post(cobalt_api_url, json=payload, headers=headers)
        
        # Logowanie dla debugowania w panelu Render
        print(f"Cobalt Response Status: {response.status_code}")
        data = response.json()

        # W v10 sukces zwraca status 'tunnel', 'redirect' lub 'picker'
        if response.status_code == 200 and 'url' in data:
            file_url = data.get('url')
            
            # 2. Przesyłamy strumień do użytkownika
            def generate():
                # Niektóre URL z Cobalt są bezpośrednie, inne wymagają tunelowania
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
        else:
            error_msg = data.get('text', 'Błąd komunikacji z API Cobalt')
            print(f"Szczegóły błędu: {data}")
            return f"Błąd Cobalt: {error_msg}", 500

    except Exception as e:
        print(f"Błąd krytyczny: {str(e)}")
        return f"Serwer Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
