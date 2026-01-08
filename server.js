const express = require('express');
const cors = require('cors');
const ytdl = require('ytdl-core'); // Silnik do YouTube
const app = express();

app.use(cors()); // Pozwala Twojej stronie łączyć się z serwerem

app.get('/download', async (req, res) => {
    try {
        const videoUrl = req.query.url;
        res.header('Content-Disposition', 'attachment; filename="audio.mp3"');
        
        // Pobiera tylko audio w najwyższej jakości i wysyła prosto do Twojej strony
        ytdl(videoUrl, { 
            quality: 'highestaudio',
            filter: 'audioonly' 
        }).pipe(res);
        
    } catch (err) {
        res.status(500).send("Błąd pobierania");
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Serwer działa na porcie ${PORT}`));
