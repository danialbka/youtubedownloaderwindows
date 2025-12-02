# YouTube Downloader for Windows

A simple terminal-based YouTube video downloader with a beautiful TUI (Terminal User Interface) for Windows.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

## ✨ Features

- 🎬 **Download YouTube videos** - Supports all YouTube URLs (youtube.com & youtu.be)
- 📊 **Video info preview** - See title, duration, views, and likes before downloading
- 🎯 **Smart format selection** - Choose from actual available formats (up to 4K/8K)
- 🎵 **Audio-only option** - Extract just the audio track
- 📁 **Flexible save locations** - Default folder, last used, or custom path
- 📋 **Download manager** - List and clear downloaded files
- 🎨 **Beautiful TUI** - Rich terminal interface with colors and tables

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/danialbka/youtubedownloaderwindows.git
   cd youtubedownloaderwindows
   ```

2. **Run the application**
   ```
   Double-click start_youtube_tui.bat
   ```
   
   The script will automatically install required dependencies (`yt-dlp`, `rich`).

3. **Download a video**
   - Select option `1` from the menu
   - Paste a YouTube URL
   - Choose your preferred quality
   - Select save location

## 📋 Requirements

- **Python 3.8+** - [Download from python.org](https://python.org) (check "Add Python to PATH")
- **FFmpeg** (optional but recommended) - For merging video/audio streams

## 🎮 Menu Options

| Option | Description |
|--------|-------------|
| 1 | 📥 Download a YouTube video |
| 2 | 📂 List downloaded files |
| 3 | 🗑️ Clear downloads folder |
| 4 | 🚪 Exit |

## 📁 Default Save Location

Downloads are saved to: `%USERPROFILE%\Downloads\YouTubeDownloads`

## 🔧 Troubleshooting

### "Python is not installed"
Download Python from [python.org](https://python.org) and check **"Add Python to PATH"** during installation.

### Video has no audio
Install FFmpeg:
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your system PATH

### Download fails
- Check your internet connection
- Update yt-dlp: `pip install -U yt-dlp`
- Some videos may be age-restricted or region-locked

## 📄 Project Structure

```
├── start_youtube_tui.bat    # Main launcher (run this)
├── youtube_tui.py           # Python application
├── functions/               # Extractor modules
│   └── extractors/
├── build_youtube_tui_exe.bat # Build standalone exe
├── HOW_TO_USE.md            # Detailed usage guide
└── README.md                # This file
```

## 📜 License

This project uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) for downloading videos.

---

Made with ❤️ for Windows users
