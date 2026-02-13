import os
import sys
import traceback
from colorama import Fore, init
from tqdm import tqdm
import yt_dlp

init(autoreset=True)

# ==========================
# CONFIGURAZIONE GRAFICA
# ==========================
TITLE_COLOR = Fore.MAGENTA
MENU_COLOR = Fore.CYAN
INPUT_COLOR = Fore.YELLOW
OK_COLOR = Fore.GREEN
ERR_COLOR = Fore.RED
INFO_COLOR = Fore.BLUE

DOWNLOAD_DIR = "download_audio"
FFMPEG_PATH = r"C:\ffmpeg\bin"   # <-- FORZATO QUI (IGNORA IL PATH DI WINDOWS)

# ==========================
# UTILITÀ GRAFICHE
# ==========================
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def header():
    print(TITLE_COLOR + "=" * 60)
    print(TITLE_COLOR + "      🎧 YT PLAYLIST AUDIO DOWNLOADER")
    print(TITLE_COLOR + "=" * 60 + "\n")

def pause():
    input(INPUT_COLOR + "\nPremi INVIO per continuare...")

# ==========================
# PROGRESS BAR STABILE
# ==========================
class TqdmLogger:
    def __init__(self):
        self.pbar = None

    def hook(self, d):
        try:
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                downloaded = d.get("downloaded_bytes", 0)

                if total:
                    if not self.pbar:
                        self.pbar = tqdm(
                            total=total,
                            unit="B",
                            unit_scale=True,
                            desc="Scaricamento",
                        )
                    self.pbar.n = downloaded
                    self.pbar.refresh()

            elif d["status"] == "finished":
                if self.pbar:
                    self.pbar.close()
                    self.pbar = None
                print(OK_COLOR + "✔ Download completato, conversione in MP3...")

        except Exception:
            pass  # La UI non deve mai rompersi

# ==========================
# CHECK FFMPEG
# ==========================
def check_ffmpeg():
    ffmpeg_exe = os.path.join(FFMPEG_PATH, "ffmpeg.exe")
    ffprobe_exe = os.path.join(FFMPEG_PATH, "ffprobe.exe")

    return os.path.isfile(ffmpeg_exe) and os.path.isfile(ffprobe_exe)

# ==========================
# DOWNLOAD PLAYLIST
# ==========================
def download_playlist_audio(url):
    if not check_ffmpeg():
        print(ERR_COLOR + "FFmpeg non trovato in C:\\ffmpeg\\bin")
        print(INFO_COLOR + "Assicurati che esistano:")
        print(INFO_COLOR + "  C:\\ffmpeg\\bin\\ffmpeg.exe")
        print(INFO_COLOR + "  C:\\ffmpeg\\bin\\ffprobe.exe")
        return

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    logger = TqdmLogger()

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(
            DOWNLOAD_DIR, "%(playlist_index)02d - %(title)s.%(ext)s"
        ),
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,

        # ===== BYPASS YOUTUBE 2026 =====
        "cookiefile": "cookies.txt",
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36"
        ),
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
                "player_skip": ["webpage"]
            }
        },

        # ===== FORZA FFMPEG (IGNORA WINDOWS) =====
        "ffmpeg_location": FFMPEG_PATH,

        "progress_hooks": [logger.hook],

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    try:
        print(INFO_COLOR + "\nConnessione a YouTube (modalità stealth)... 🥷")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        if not info:
            print(ERR_COLOR + "❌ Impossibile leggere la playlist.")
            return

        print(OK_COLOR + "\n🎉 Playlist scaricata correttamente!")
        print(INFO_COLOR + f"File salvati in: {os.path.abspath(DOWNLOAD_DIR)}")

    except yt_dlp.utils.DownloadError as e:
        print(ERR_COLOR + "\n❌ Errore yt-dlp:")
        print(ERR_COLOR + str(e))

    except Exception as e:
        print(ERR_COLOR + "\n💥 Errore imprevisto:")
        print(ERR_COLOR + str(e))
        print(ERR_COLOR + traceback.format_exc())

# ==========================
# SELEZIONE CARTELLA DOWNLOAD (SOLO INPUT TESTUALE)
# ==========================
def select_download_directory():
    global DOWNLOAD_DIR

    clear()
    header()

    print(INFO_COLOR + f"Cartella attuale: {os.path.abspath(DOWNLOAD_DIR)}\n")
    print(MENU_COLOR + "Premi INVIO per usare questa cartella")
    print(MENU_COLOR + "Oppure inserisci un nuovo percorso completo\n")

    path = input(INPUT_COLOR + "Percorso: ").strip()

    if path == "":
        return

    try:
        # Se non esiste la crea automaticamente
        os.makedirs(path, exist_ok=True)
        DOWNLOAD_DIR = path
        print(OK_COLOR + "\n✔ Cartella impostata correttamente.")
    except Exception as e:
        print(ERR_COLOR + f"\nErrore nel creare la cartella: {e}")
        pause()

# ==========================
# MENU PRINCIPALE
# ==========================
def main_menu():
    while True:
        clear()
        header()
        print(MENU_COLOR + "1) Scarica audio da playlist YouTube")
        print(MENU_COLOR + "2) Esci\n")

        choice = input(INPUT_COLOR + "Selezione: ").strip()

        if choice == "1":
            url = input(INPUT_COLOR + "\nInserisci URL playlist: ").strip()

            if not url.startswith("http"):
                print(ERR_COLOR + "URL non valido.")
                pause()
                continue

            select_download_directory()

            clear()
            header()
            print(INFO_COLOR + f"Download in: {os.path.abspath(DOWNLOAD_DIR)}\n")

            download_playlist_audio(url)
            pause()

        elif choice == "2":
            print(OK_COLOR + "\nMissione compiuta. Alla prossima, comandante audio 🎶")
            sys.exit(0)

        else:
            print(ERR_COLOR + "Scelta non valida.")
            pause()

# ==========================
# ENTRY POINT
# ==========================
if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(ERR_COLOR + "\n\nInterruzione manuale. Nessun MP3 è stato ferito.")
    except Exception as e:
        print(ERR_COLOR + "\nErrore critico:")
        print(ERR_COLOR + str(e))
        print(ERR_COLOR + traceback.format_exc())
