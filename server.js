const express = require('express');
const cors = require('cors');
const ytdl = require('@distube/ytdl-core');
const app = express();

// Blokada zbędnych komunikatów w logach
process.env.YTDL_NO_UPDATE = 'true';

app.use(cors());

app.get('/download', async (req, res) => {
    const videoUrl = req.query.url;

    if (!videoUrl || !ytdl.validateURL(videoUrl)) {
        return res.status(400).send("Nieprawidłowy link YouTube");
    }

    try {
        // Ustawiamy nagłówki, aby przeglądarka wiedziała, że to plik audio
        res.setHeader('Content-Disposition', 'attachment; filename="audio.mp3"');
        res.setHeader('Content-Type', 'audio/mpeg');

        // Pobieranie audio z optymalizacją bufora (highWaterMark) dla darmowych serwerów
        const stream = ytdl(videoUrl, { 
            quality: 'highestaudio',
            filter: 'audioonly',
            highWaterMark: 1 << 25 // 32MB bufora, aby uniknąć błędów 502/Memory Limit
        });

        stream.on('error', (err) => {
            console.error("Błąd strumienia:", err.message);
            if (!res.headersSent) res.status(500).send("Błąd transmisji");
        });

        // Wysyłanie danych prosto do użytkownika
        stream.pipe(res);

    } catch (err) {
        console.error("Błąd krytyczny:", err.message);
        if (!res.headersSent) res.status(500).send("Błąd serwera");
    }
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Serwer AudioStitcher działa na porcie ${PORT}`);
});
