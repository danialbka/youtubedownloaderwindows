# YouTube Downloader TUI - Windows Edition

A simple terminal application for downloading YouTube videos on Windows.

## Requirements

- Python 3.8 or higher
- FFmpeg (for merging video/audio streams)

## Quick Start

1. Double-click `start_youtube_tui.bat`
2. The script will automatically install required dependencies (`yt-dlp`, `rich`)
3. Select option **1** to download a video
4. Paste a YouTube URL and press Enter
5. Choose your preferred quality from the available formats
6. Select where to save the file

## Features

### Download YouTube Videos
- Paste any YouTube URL (youtube.com or youtu.be links)
- See video information before downloading (title, duration, views, etc.)
- Choose from actual available formats for each video
- Supports resolutions up to 4K/8K when available

### Smart Format Selection
The app shows you the real formats available for each video:
- **Best quality** - Automatically picks the highest quality
- **Specific resolutions** - 2160p, 1440p, 1080p, 720p, etc.
- **Audio only** - Download just the audio track

### Save Location Options
- **Default**: `%USERPROFILE%\Downloads\YouTubeDownloads`
- **Last used**: Remembers your last custom folder
- **Custom**: Enter any folder path

### Manage Downloads
- View all downloaded files with sizes and dates
- Clear downloads folder when needed

## Menu Options

| Option | Description |
|--------|-------------|
| 1 | Download a YouTube video |
| 2 | List downloaded files |
| 3 | Clear downloads folder |
| 4 | Exit |

## Troubleshooting

### "Python is not installed"
Download Python from [python.org](https://python.org) and make sure to check **"Add Python to PATH"** during installation.

### "FFmpeg not found" or video has no audio
Install FFmpeg:
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add `C:\ffmpeg\bin` to your system PATH

### Download fails or times out
- Check your internet connection
- Some videos may be age-restricted or region-locked
- Try updating yt-dlp: `pip install -U yt-dlp`

## Files

| File | Purpose |
|------|---------|
| `start_youtube_tui.bat` | Main launcher (run this) |
| `youtube_tui.py` | Python application |
| `functions/` | Extractor modules |
| `.yt_settings.json` | Saved preferences (auto-created) |

## License

This tool uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) for downloading.
