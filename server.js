const express = require('express');
const cors = require('cors');
const ytdl = require('@distube/ytdl-core'); // Zmieniona biblioteka
const app = express();

app.use(cors());

app.get('/download', async (req, res) => {
    try {
        const videoUrl = req.query.url;
        if (!videoUrl) return res.status(400).send("Brak URL");

        res.header('Content-Disposition', 'attachment; filename="audio.mp3"');
        
        // Pobieranie strumieniowe z dodatkowymi nagłówkami
        ytdl(videoUrl, { 
            quality: 'highestaudio',
            filter: 'audioonly',
            requestOptions: {
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                }
            }
        }).pipe(res);
        
    } catch (err) {
        console.error("Błąd:", err);
        res.status(500).send("Błąd pobierania");
    }
});

const PORT = process.env.PORT || 10000; // Render używa portu 10000
app.listen(PORT, () => console.log(`Serwer działa na porcie ${PORT}`));
