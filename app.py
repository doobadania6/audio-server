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

    # API COBALT (v10)
    cobalt_api_url = "https://api.cobalt.tools/"
    
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

    try:
        response = requests.post(cobalt_api_url, json=payload, headers=headers)
        data = response.json()

        if response.status_code == 200 and 'url' in data:
            file_url = data.get('url')
            
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
        else:
            error_msg = data.get('text', 'Błąd komunikacji z API Cobalt')
            return f"Błąd Cobalt: {error_msg}", 500

    except Exception as e:
        return f"Serwer Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
