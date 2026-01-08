const express = require('express');
const cors = require('cors');
const ytdl = require('@distube/ytdl-core');
const app = express();

// Wyłącza irytujący komunikat o aktualizacji w logach Rendera
process.env.YTDL_NO_UPDATE = 'true';

app.use(cors());

app.get('/download', async (req, res) => {
    try {
        const videoUrl = req.query.url;
        if (!videoUrl) {
            return res.status(400).send("Brak URL");
        }

        // Sprawdź czy URL jest poprawny zanim zaczniesz pobierać
        if (!ytdl.validateURL(videoUrl)) {
            return res.status(400).send("Nieprawidłowy link do YouTube");
        }

        res.header('Content-Disposition', 'attachment; filename="audio.mp3"');
        res.header('Content-Type', 'audio/mpeg');

        const stream = ytdl(videoUrl, { 
            quality: 'highestaudio',
            filter: 'audioonly',
            requestOptions: {
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                }
            }
        });

        // KLUCZOWE: Obsługa błędów wewnątrz strumienia
        stream.on('error', (err) => {
            console.error("Błąd strumienia:", err);
            if (!res.headersSent) {
                res.status(500).send("Błąd podczas przesyłania audio");
            }
        });

        stream.pipe(res);
        
    } catch (err) {
        console.error("Główny błąd serwera:", err);
        if (!res.headersSent) {
            res.status(500).send("Błąd pobierania");
        }
    }
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Serwer AudioStitcher działa na porcie ${PORT}`);
});
