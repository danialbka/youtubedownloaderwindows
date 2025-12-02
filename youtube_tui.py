#!/usr/bin/env python3
"""
YouTube Downloader TUI - focused terminal interface for grabbing YouTube videos.
Paste a YouTube link, pick a format, and save it locally.
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# Windows-specific fixes
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    os.system('')  # Enable ANSI colors in Windows terminal

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
except ImportError:
    print("Installing rich library...")
    os.system(f"{sys.executable} -m pip install rich --quiet")
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.table import Table

from functions.extractors import YouTubeExtractor

# Initialize console with Windows-safe settings
console = Console(force_terminal=True)

# Default download directory
if sys.platform == 'win32':
    DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "YouTubeDownloads")
else:
    DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads", "youtube")

# Settings file to remember preferences
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".yt_settings.json")

YT_EXTRACTOR = YouTubeExtractor()


def load_settings() -> dict:
    """Load saved settings from file."""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_settings(settings: dict):
    """Save settings to file."""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)
    except Exception:
        pass


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """Print the application banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                 🎬 YOUTUBE DOWNLOADER TUI                     ║
║                                                               ║
║   Paste a YouTube link, choose a format, and download it.     ║
╚═══════════════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner, style="bold red", border_style="red"))


def format_duration(seconds):
    """Format duration in seconds to human readable format."""
    if not seconds:
        return "Unknown"
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def format_size(bytes_size):
    """Format bytes to human readable size."""
    if not bytes_size:
        return "Unknown"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def get_video_files(directory: str) -> list:
    """Get list of video/audio files in a directory."""
    extensions = ('.mp4', '.webm', '.mkv', '.m4a', '.mp3')
    if not os.path.exists(directory):
        return []
    return [f for f in os.listdir(directory) if f.lower().endswith(extensions)]


def is_youtube_url(url: str) -> bool:
    """Basic YouTube URL check."""
    check = url.lower()
    return 'youtube.com' in check or 'youtu.be' in check


async def get_video_info(url: str):
    """Get video information."""
    try:
        info = await YT_EXTRACTOR.extract_info(url)
        return info, None
    except Exception as e:
        return None, str(e)


async def download_video(url: str, output_dir: str, format_id: str = "best"):
    """Download video to specified directory."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        output_template = os.path.join(output_dir, '%(title)s.%(ext)s')
        try:
            await YT_EXTRACTOR.download(url, format_id, output_template)
        except Exception as e:
            # If requested format is unavailable, fall back to best
            if format_id != "best" and "Requested format is not available" in str(e):
                console.print("[yellow]Requested format not available, falling back to best...[/yellow]")
                await YT_EXTRACTOR.download(url, "best", output_template)
                format_id = "best"
            else:
                raise

        # Find the downloaded file
        files = get_video_files(output_dir)
        if files:
            files_with_time = [(f, os.path.getmtime(os.path.join(output_dir, f))) for f in files]
            files_with_time.sort(key=lambda x: x[1], reverse=True)
            return os.path.join(output_dir, files_with_time[0][0]), None
        return None, "Download completed but file not found"
    except Exception as e:
        return None, str(e)


def display_video_info(info: dict):
    """Display video information in a nice table."""
    table = Table(title="📋 Video Information", show_header=False, border_style="red")
    table.add_column("Property", style="bold yellow")
    table.add_column("Value", style="white")

    table.add_row("Title", info.get('title', 'Unknown')[:70])
    table.add_row("Duration", format_duration(info.get('duration')))
    table.add_row("Uploader", info.get('uploader', info.get('channel', 'Unknown')))

    if info.get('view_count'):
        table.add_row("Views", f"{info.get('view_count'):,}")

    if info.get('like_count'):
        table.add_row("Likes", f"{info.get('like_count'):,}")

    if info.get('live_status'):
        table.add_row("Type", info.get('live_status'))

    # Show available resolutions
    formats = info.get('formats', [])
    resolutions = set()
    for fmt in formats:
        if fmt.get('height'):
            resolutions.add(fmt.get('height'))
    if resolutions:
        res_str = ", ".join([f"{r}p" for r in sorted(resolutions, reverse=True)[:6]])
        table.add_row("Resolutions", res_str)

    console.print(table)
    console.print()


def display_format_options(info: dict) -> list:
    """Display available format options from the actual video."""
    formats = info.get('formats', [])
    if not formats:
        return []

    options = []
    seen = set()
    
    # Collect unique video formats with height
    video_formats = []
    for fmt in formats:
        height = fmt.get('height')
        vcodec = fmt.get('vcodec', 'none')
        acodec = fmt.get('acodec', 'none')
        if height and vcodec != 'none':
            video_formats.append(fmt)
    
    # Sort by height descending
    video_formats.sort(key=lambda x: x.get('height', 0) or 0, reverse=True)
    
    # Add best quality option first
    options.append({
        "id": "bestvideo+bestaudio/best",
        "desc": "Best quality (video + audio)",
        "resolution": "Best",
        "size": "",
        "type": "video+audio"
    })
    
    # Add actual video resolutions from the video
    for fmt in video_formats:
        height = fmt.get('height')
        if height and height not in seen:
            seen.add(height)
            filesize = fmt.get('filesize') or fmt.get('filesize_approx')
            size_str = format_size(filesize) if filesize else "~"
            fps = fmt.get('fps', '')
            fps_str = f" {fps}fps" if fps and fps > 30 else ""
            
            options.append({
                "id": f"bestvideo[height<={height}]+bestaudio/best[height<={height}]",
                "desc": f"{height}p{fps_str}",
                "resolution": f"{height}p",
                "size": size_str,
                "type": "video+audio"
            })
            
            if len(seen) >= 6:  # Limit to 6 video options
                break
    
    # Add audio-only option
    options.append({
        "id": "bestaudio/best",
        "desc": "Audio only (best quality)",
        "resolution": "Audio",
        "size": "",
        "type": "audio"
    })

    console.print("\n[bold red]📦 Available formats from this video:[/bold red]")

    table = Table(show_header=True, border_style="dim")
    table.add_column("#", style="bold yellow", width=3)
    table.add_column("Quality", style="white")
    table.add_column("Est. Size", style="cyan")
    table.add_column("Type", style="dim")

    for i, opt in enumerate(options, 1):
        table.add_row(str(i), opt['desc'], opt['size'], opt['type'])

    console.print(table)
    return options


def select_format(options: list) -> str:
    """Let user select a format."""
    while True:
        choice = Prompt.ask("\n[bold]Enter choice[/bold]", default="1")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]['id']
        except ValueError:
            pass
        console.print("[red]Invalid choice, try again[/red]")


def select_save_location(default_path: str) -> str:
    """Let user select where to save the file."""
    settings = load_settings()
    last_custom_dir = settings.get('last_custom_dir')
    
    console.print(f"\n[bold red]💾 Save location:[/bold red]")
    console.print(f"   [1] Default: {default_path}")
    if last_custom_dir and os.path.isdir(last_custom_dir):
        console.print(f"   [2] Last used: {last_custom_dir}")
        console.print(f"   [3] Enter new custom path")
        choice = Prompt.ask("Choose option", choices=["1", "2", "3"], default="1")
        
        if choice == "2":
            return last_custom_dir
        elif choice == "3":
            pass  # Fall through to custom path entry
        else:
            return default_path
    else:
        custom = Confirm.ask("Use custom save location?", default=False)
        if not custom:
            return default_path
    
    # Custom path entry
    while True:
        path = Prompt.ask("Enter folder path")
        path = os.path.expanduser(path)
        if os.path.isdir(path):
            # Save this as last custom dir
            settings['last_custom_dir'] = path
            save_settings(settings)
            return path
        if Confirm.ask(f"'{path}' doesn't exist. Create it?"):
            try:
                os.makedirs(path, exist_ok=True)
                # Save this as last custom dir
                settings['last_custom_dir'] = path
                save_settings(settings)
                return path
            except Exception as e:
                console.print(f"[red]Error creating directory: {e}[/red]")


async def main_download_flow():
    """Main download workflow."""
    clear_screen()
    print_banner()

    console.print("[bold green]📎 Paste YouTube URL:[/bold green]")
    url = Prompt.ask("URL").strip()

    if not url:
        console.print("[red]No URL provided![/red]")
        return

    if not is_youtube_url(url):
        console.print("[red]This tool only downloads from YouTube. Please paste a YouTube link.[/red]")
        return

    console.print("\n[yellow]⏳ Fetching video information...[/yellow]")

    with console.status("[bold yellow]Contacting YouTube..."):
        info, error = await get_video_info(url)

    if error:
        console.print(f"\n[bold red]❌ Error:[/bold red] {error}")
        return

    if not info:
        console.print("\n[bold red]❌ Could not get video information[/bold red]")
        return

    console.print()
    display_video_info(info)

    if not Confirm.ask("Download this video?", default=True):
        console.print("[yellow]Download cancelled.[/yellow]")
        return

    format_options = display_format_options(info)
    format_id = select_format(format_options) if format_options else "best"

    save_dir = select_save_location(DEFAULT_DOWNLOAD_DIR)

    console.print(f"\n[bold green]⬇️  Downloading to: {save_dir}[/bold green]")
    console.print("[dim]Download progress will be shown below...[/dim]\n")

    filepath, error = await download_video(url, save_dir, format_id)

    if error:
        console.print(f"\n[bold red]❌ Download failed:[/bold red] {error}")
        return

    if filepath and os.path.exists(filepath):
        file_size = os.path.getsize(filepath)
        console.print(f"\n[bold green]✅ Download complete![/bold green]")
        console.print(f"   📁 File: {os.path.basename(filepath)}")
        console.print(f"   📊 Size: {format_size(file_size)}")
        console.print(f"   📍 Location: {filepath}")
    else:
        console.print("\n[yellow]⚠️  Download may have completed but file not found[/yellow]")


def list_downloads():
    """List all downloaded files."""
    clear_screen()
    console.print(Panel("[bold red]📂 Downloaded YouTube Files[/bold red]", border_style="red"))

    if not os.path.exists(DEFAULT_DOWNLOAD_DIR):
        console.print("[yellow]No downloads folder found.[/yellow]")
        return

    files = get_video_files(DEFAULT_DOWNLOAD_DIR)
    if not files:
        console.print("[yellow]No downloaded files found.[/yellow]")
        return

    table = Table(show_header=True, border_style="red")
    table.add_column("#", style="bold yellow", width=3)
    table.add_column("Filename", style="white")
    table.add_column("Size", style="green")
    table.add_column("Date", style="dim")

    for i, filename in enumerate(sorted(files), 1):
        filepath = os.path.join(DEFAULT_DOWNLOAD_DIR, filename)
        size = format_size(os.path.getsize(filepath))
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d %H:%M")
        table.add_row(str(i), filename[:60], size, mtime)

    console.print(table)
    console.print(f"\n[dim]Location: {DEFAULT_DOWNLOAD_DIR}[/dim]")


def clear_downloads():
    """Clear the downloads folder."""
    if not os.path.exists(DEFAULT_DOWNLOAD_DIR):
        console.print("[yellow]Downloads folder is already empty.[/yellow]")
        return

    files = get_video_files(DEFAULT_DOWNLOAD_DIR)
    if not files:
        console.print("[yellow]No video files to delete.[/yellow]")
        return

    console.print(f"[yellow]Found {len(files)} files to delete.[/yellow]")
    if Confirm.ask("[red]Delete all downloaded files?[/red]", default=False):
        for f in files:
            try:
                os.remove(os.path.join(DEFAULT_DOWNLOAD_DIR, f))
            except Exception as e:
                console.print(f"[red]Error deleting {f}: {e}[/red]")
        console.print("[green]✅ Downloads cleared![/green]")
    else:
        console.print("[yellow]Cancelled.[/yellow]")


def show_main_menu():
    """Show the main menu."""
    clear_screen()
    print_banner()

    menu = """
[bold red]Main Menu:[/bold red]

  [bold yellow]1.[/bold yellow] 📥 Download a YouTube video
  [bold yellow]2.[/bold yellow] 📂 List downloaded files
  [bold yellow]3.[/bold yellow] 🗑️  Clear downloads folder
  [bold yellow]4.[/bold yellow] 🚪 Exit

"""
    console.print(menu)
    return Prompt.ask("[bold]Select option[/bold]", choices=["1", "2", "3", "4"], default="1")


async def main():
    """Main entry point."""
    try:
        while True:
            choice = show_main_menu()

            if choice == "1":
                await main_download_flow()
                console.print("\n[dim]Press Enter to continue...[/dim]")
                input()
            elif choice == "2":
                list_downloads()
                console.print("\n[dim]Press Enter to continue...[/dim]")
                input()
            elif choice == "3":
                clear_downloads()
                console.print("\n[dim]Press Enter to continue...[/dim]")
                input()
            elif choice == "4":
                clear_screen()
                console.print("[bold red]👋 Goodbye![/bold red]")
                break

    except KeyboardInterrupt:
        clear_screen()
        console.print("\n[bold red]👋 Goodbye![/bold red]")


if __name__ == "__main__":
    asyncio.run(main())
