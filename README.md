# 🎧 YT Playlist Audio Downloader

Downloader da terminale per scaricare intere playlist YouTube in formato
MP3, con barra di avanzamento stabile e conversione automatica tramite
FFmpeg.

------------------------------------------------------------------------

## ✨ Funzionalità

-   Download completo di playlist YouTube
-   Conversione automatica in MP3 (192 kbps)
-   Barra di avanzamento e interfaccia con rich
-   Selezione della cartella di destinazione da terminale
-   Gestione errori robusta
-   Forzatura manuale del percorso FFmpeg

------------------------------------------------------------------------

## 📦 Requisiti

-   Python 3.9+
-   FFmpeg installato manualmente
-   Windows

------------------------------------------------------------------------

## 🔧 Installazione

### 1️⃣ Clona la repository

git clone `<url_repo>`{=html} cd `<nome_repo>`{=html}

### 2️⃣ Installa le dipendenze

pip install -r requirements.txt

### 3️⃣ Installa FFmpeg

Assicurati che esistano:

C:`\ffmpeg`{=tex}`\bin`{=tex}`\ffmpeg`{=tex}.exe
C:`\ffmpeg`{=tex}`\bin`{=tex}`\ffprobe`{=tex}.exe

Il percorso è forzato nello script:

FFMPEG_PATH = r"C:`\ffmpeg`{=tex}`\bin`{=tex}"

Se vuoi cambiarlo, modifica quella variabile.

------------------------------------------------------------------------

## 🚀 Utilizzo

Esegui:

python main.py

Seleziona:

1)  Scarica audio da playlist YouTube

Inserisci l'URL della playlist.

Poi scegli la cartella di destinazione (oppure premi INVIO per usare
quella di default).

------------------------------------------------------------------------

## 📁 Output

I file verranno salvati nel formato:

01 - Titolo Brano.mp3 02 - Altro Brano.mp3

------------------------------------------------------------------------

## 🛠 Struttura del progetto

. ├── main.py ├── requirements.txt ├── cookies.txt (opzionale) └──
download_audio/

------------------------------------------------------------------------

## ⚠️ Note

-   Se YouTube blocca il download, puoi usare un file cookies.txt
-   Viene usato yt-dlp con modalità compatibilità avanzata

------------------------------------------------------------------------

## 📄 Licenza

Uso personale.
