#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema di Estrazione e Conversione Audio da Playlist (Enterprise Edition)
Modulo per il download massivo da YouTube tramite yt-dlp e conversione in formato MP3.
Gestisce in modo asincrono la progressione tramite callback.
"""

import sys
from pathlib import Path
from typing import Callable, Optional, Dict, Any

import yt_dlp
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    DownloadColumn
)

# Importazione del logger aziendale
from custom_logger import logger

# ==========================================
# COSTANTI E CONFIGURAZIONI DI SISTEMA
# ==========================================

# Percorso assoluto richiesto per le dipendenze di conversione
FFMPEG_DIRECTORY = Path(r"C:\ffmpeg\bin")


# ==========================================
# CORE: Logica di Business
# ==========================================

def verify_ffmpeg_installation(target_dir: Path) -> bool:
    """
    Verifica la presenza dei binari FFmpeg e FFprobe necessari per la conversione audio.
    
    :param target_dir: Directory in cui cercare gli eseguibili.
    :return: True se entrambi gli eseguibili sono presenti, False altrimenti.
    """
    ffmpeg_exe = target_dir / "ffmpeg.exe"
    ffprobe_exe = target_dir / "ffprobe.exe"
    return ffmpeg_exe.is_file() and ffprobe_exe.is_file()


def download_playlist_audio(
    target_url: str,
    output_directory: Path,
    ffmpeg_dir: Path,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> bool:
    """
    Gestisce l'estrazione e il download della playlist utilizzando yt-dlp.
    
    :param target_url: URL della risorsa da scaricare.
    :param output_directory: Directory in cui salvare i file audio risultanti.
    :param ffmpeg_dir: Percorso dell'eseguibile FFmpeg.
    :param progress_callback: Funzione di callback per tracciare l'avanzamento.
    :return: True in caso di successo, False in caso di eccezioni critiche.
    """
    if not verify_ffmpeg_installation(ffmpeg_dir):
        logger.error(f"Dipendenze mancanti. FFmpeg o FFprobe non trovati in: {ffmpeg_dir.resolve()}")
        return False

    output_directory.mkdir(parents=True, exist_ok=True)

    # Configurazione ottimizzata e silenziata (gestita dal logger o dalla UI)
    ydl_options = {
        "format": "bestaudio/best",
        "outtmpl": str(output_directory / "%(playlist_index)02d - %(title)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
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
        "ffmpeg_location": str(ffmpeg_dir.resolve()),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    if progress_callback:
        ydl_options["progress_hooks"] = [progress_callback]

    try:
        logger.info(f"Avvio interrogazione server e download risorsa: {target_url}")
        with yt_dlp.YoutubeDL(ydl_options) as ydl:
            info = ydl.extract_info(target_url, download=True)
            
            if not info:
                logger.error("Estrazione fallita: il servizio non ha restituito informazioni valide.")
                return False
                
        logger.info("Elaborazione della playlist completata con successo.")
        return True

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Errore di rete o di parsing durante il download (yt-dlp): {e}")
        return False
    except Exception as e:
        logger.critical(f"Errore: {e}", exc_info=True)
        return False


# ==========================================
# INTERFACCIA: Logica UI e Terminale
# ==========================================

def display_header(console: Console) -> None:
    """Stampa l'intestazione grafica formale all'avvio dell'applicazione."""
    console.clear()
    console.print("[bold magenta]============================================================[/bold magenta]")
    console.print("[bold white]            SISTEMA DI ESTRAZIONE AUDIO PLAYLIST            [/bold white]")
    console.print("[bold magenta]============================================================[/bold magenta]\n")


def manage_directory_configuration(current_dir: Path, console: Console) -> Path:
    """Gestisce l'input per la modifica della directory di lavoro."""
    console.print(f"\n[dim]Directory attuale: {current_dir.resolve()}[/dim]")
    
    new_path_input = Prompt.ask("Inserire il nuovo percorso (Lasciare vuoto per mantenere l'attuale)").strip().strip('"')
    
    if not new_path_input:
        return current_dir

    new_path = Path(new_path_input)
    try:
        new_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory di destinazione aggiornata con successo: {new_path.resolve()}")
        console.print(f"[bold green]Directory operativa impostata su: {new_path.resolve()}[/bold green]")
        return new_path
    except Exception as e:
        logger.error(f"Impossibile accedere o creare la directory {new_path}: {e}")
        console.print("[bold red]Errore: Impossibile configurare il percorso richiesto. Verrà mantenuto quello precedente.[/bold red]")
        return current_dir


def main() -> None:
    """Entry point principale che orchestra i menu e raccoglie gli input dell'utente."""
    console = Console()
    display_header(console)
    logger.info("Avvio del sottosistema di estrazione audio terminale.")

    active_download_dir = Path("download_audio").resolve()

    while True:
        console.print("\n[bold cyan]--- MENU OPERATIVO ---[/bold cyan]")
        console.print("  [cyan]1)[/cyan] Configura ed esegui download da playlist")
        console.print("  [cyan]2)[/cyan] Modifica directory di destinazione")
        console.print("  [cyan]3)[/cyan] Termina applicazione\n")

        user_choice = Prompt.ask("Selezionare l'operazione desiderata", choices=["1", "2", "3"], show_choices=False)

        if user_choice == "1":
            target_url = Prompt.ask("Inserire l'URL della playlist YouTube").strip().strip('"')

            if not target_url.startswith("http"):
                logger.warning(f"URL inserito non conforme: {target_url}")
                console.print("[bold red]Errore: Protocollo o sintassi dell'URL non validi.[/bold red]")
                continue

            if not verify_ffmpeg_installation(FFMPEG_DIRECTORY):
                console.print(f"[bold red]Errore critico: Installazione FFmpeg non rilevata nel percorso {FFMPEG_DIRECTORY}.[/bold red]")
                console.print("L'operazione non può proseguire senza le dipendenze di conversione.")
                continue

            # Riepilogo Operazione pre-esecuzione
            summary_table = Table(title="Riepilogo Parametri Elaborazione", header_style="bold magenta")
            summary_table.add_column("Parametro Strategico", style="dim")
            summary_table.add_column("Valore Definito")
            summary_table.add_row("URL Risorsa", target_url)
            summary_table.add_row("Directory di Salvataggio", str(active_download_dir))
            summary_table.add_row("Sottosistema FFMPEG", str(FFMPEG_DIRECTORY.resolve()))

            console.print("\n")
            console.print(summary_table)
            console.print("\n")

            if not Confirm.ask("Procedere con l'elaborazione dei contenuti?"):
                logger.info("L'operazione di download è stata annullata dall'operatore.")
                console.print("Operazione annullata.")
                continue

            logger.info("Inizio procedura di download.")

            # Gestione Avanzamento Visivo
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                DownloadColumn(),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                
                download_task_id = progress.add_task("[cyan]Analisi risorsa in corso...", total=None)

                def rich_progress_hook(status_dict: Dict[str, Any]) -> None:
                    """Callback interno per connettere la UI ai dati di progressione di yt-dlp."""
                    try:
                        status = status_dict.get("status")
                        
                        if status == "downloading":
                            total_bytes = status_dict.get("total_bytes") or status_dict.get("total_bytes_estimate", 0)
                            downloaded_bytes = status_dict.get("downloaded_bytes", 0)
                            filename = status_dict.get("filename", "Traccia_Audio")
                            
                            safe_name = Path(filename).name
                            
                            if total_bytes > 0:
                                progress.update(download_task_id, total=total_bytes, completed=downloaded_bytes, description=f"[cyan]Download: {safe_name}")
                            else:
                                progress.update(download_task_id, completed=downloaded_bytes, description=f"[cyan]Download: {safe_name}")
                                
                        elif status == "finished":
                            # Completamento forzato della barra prima della conversione FFmpeg
                            if progress.tasks[download_task_id].total is not None:
                                progress.update(download_task_id, completed=progress.tasks[download_task_id].total)
                            progress.update(download_task_id, description="[bold green]Download traccia terminato. Avvio conversione MP3...[/bold green]")
                            logger.debug("Download traccia parziale completato. Passaggio a FFmpeg.")
                            
                    except Exception as e:
                        # Eventuali anomalie nella GUI non devono interrompere l'elaborazione
                        logger.debug(f"Anomalia nel rendering della barra di avanzamento: {e}")

                # Esecuzione isolata della logica core
                operation_success = download_playlist_audio(
                    target_url=target_url,
                    output_directory=active_download_dir,
                    ffmpeg_dir=FFMPEG_DIRECTORY,
                    progress_callback=rich_progress_hook
                )

            if operation_success:
                console.print(f"\n[bold green]--- ELABORAZIONE COMPLETATA ---[/bold green]")
                console.print(f"I file sono stati depositati in: {active_download_dir.resolve()}")
            else:
                console.print("\n[bold red]L'elaborazione è terminata con errori. Consultare i log di sistema per i dettagli.[/bold red]")

            Prompt.ask("\n[dim]Premere Invio per tornare al menu operativo...[/dim]")
            display_header(console)

        elif user_choice == "2":
            active_download_dir = manage_directory_configuration(active_download_dir, console)

        elif user_choice == "3":
            logger.info("Chiusura corretta del sistema richiesta dall'operatore.")
            console.print("[bold green]Disconnessione dal servizio. Terminazione completata.[/bold green]")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Esecuzione interrotta tramite KeyboardInterrupt.")
        Console().print("\n[bold yellow]Sospensione forzata richiesta. Uscita di sicurezza effettuata.[/bold yellow]")
        sys.exit(0)
    except Exception as unexpected_exception:
        logger.critical(f"Errore irreversibile di sistema: {unexpected_exception}", exc_info=True)
        Console().print("\n[bold red]Arresto anomalo del programma. Verificare i registri del logger.[/bold red]")
        sys.exit(1)