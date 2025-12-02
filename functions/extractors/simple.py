"""
YouTube-only extractor module.
"""

from .base import BaseExtractor
from typing import Dict, Any
import yt_dlp
import asyncio


class YouTubeExtractor(BaseExtractor):
    """
    Optimized extractor for YouTube.
    Handles age-restricted content, live streams, and playlists.
    """
    
    HOST = "youtube.com"
    
    def can_extract(self, url: str) -> bool:
        """Handle youtube.com and youtu.be URLs."""
        return 'youtube.com' in url or 'youtu.be' in url

    def _get_ydl_opts(self, for_download: bool = False) -> dict:
        opts = self._get_base_opts(for_download)
        
        opts.update({
            # YouTube-specific format selection with flexible fallbacks
            'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
            # Handle age-restricted content
            'age_limit': None,
            # Don't download playlists unless explicitly requested
            'noplaylist': True,
            # Extract flat playlist info quickly
            'extract_flat': False,
            # Merge video+audio into mp4
            'merge_output_format': 'mp4',
        })
        
        if for_download:
            opts.update({
                # Post-processing for best quality
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            })
        
        return opts

    async def extract_info(self, url: str) -> Dict[str, Any]:
        async def _extract():
            opts = self._get_ydl_opts(for_download=False)
            with yt_dlp.YoutubeDL(opts) as ydl:
                return await self._run_in_executor(
                    lambda: ydl.extract_info(url, download=False)
                )
        return await self._retry(_extract, max_retries=3)

    async def download(self, url: str, format_id: str = "best", output_path: str = None) -> str:
        async def _download():
            opts = self._get_ydl_opts(for_download=True)
            if format_id != "best":
                opts['format'] = format_id
            opts['outtmpl'] = output_path or '%(title)s.%(ext)s'
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = await self._run_in_executor(
                    lambda: ydl.extract_info(url, download=False)
                )
                await self._with_timeout(
                    self._run_in_executor(lambda: ydl.download([url])),
                    timeout_seconds=600  # 10 min for YouTube
                )
            return self._get_filename(info, output_path)
        
        return await self._retry(_download, max_retries=2)
