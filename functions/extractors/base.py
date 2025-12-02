"""
Base extractor with common functionality for all video sites.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
import asyncio
import random
import yt_dlp


class BaseExtractor(ABC):
    """Abstract base class for all extractors with common utilities."""

    HOST = ""  # Override in subclass
    
    # User agents for rotation
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
    ]

    def can_extract(self, url: str) -> bool:
        """Check if this extractor can handle the given URL."""
        return self.HOST in url

    def _get_random_user_agent(self) -> str:
        """Get a random user agent for rotation."""
        return random.choice(self.USER_AGENTS)

    def _get_base_opts(self, for_download: bool = False) -> dict:
        """Get base yt-dlp options with good defaults."""
        opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            # Network robustness
            'socket_timeout': 30,
            'retries': 5,
            'fragment_retries': 5,
            'extractor_retries': 3,
            'file_access_retries': 3,
            # Bypass common restrictions
            'nocheckcertificate': True,
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            # Prevent hanging
            'sleep_interval': 0,
            'max_sleep_interval': 0,
            'sleep_interval_requests': 0,
            # Don't check formats (faster, more compatible)
            'no_check_formats': True,
            # Default extractor args for YouTube compatibility
            'extractor_args': {
                'youtube': {
                    'player_client': ['default'],
                }
            },
        }
        
        if for_download:
            opts.update({
                'writeinfojson': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'http_chunk_size': 10485760,  # 10MB chunks
                'concurrent_fragment_downloads': 4,
            })
        
        return opts

    async def _run_in_executor(self, func):
        """Run a blocking function in a thread executor."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func)

    async def _with_timeout(self, coro, timeout_seconds: int = 300):
        """Run a coroutine with a timeout."""
        try:
            return await asyncio.wait_for(coro, timeout=timeout_seconds)
        except asyncio.TimeoutError:
            raise Exception(f"Operation timed out after {timeout_seconds} seconds")

    async def _retry(self, operation, max_retries: int = 3, delay: float = 2.0):
        """Retry an operation with exponential backoff."""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return await operation()
            except Exception as e:
                last_exception = e
                error_str = str(e).lower()
                
                # Don't retry on certain errors
                if '403' in error_str or 'forbidden' in error_str:
                    raise  # Access denied - retrying won't help
                if 'not found' in error_str or '404' in error_str:
                    raise  # Video doesn't exist
                
                if attempt < max_retries - 1:
                    wait_time = delay * (attempt + 1) + random.uniform(0, 1)
                    await asyncio.sleep(wait_time)
        
        raise last_exception

    def _get_filename(self, info: dict, output_path: str) -> str:
        """Determine the output filename from info dict."""
        if output_path and '%(title)s' in output_path:
            title = info.get('title', 'video')
            # Sanitize title for filename
            title = "".join(c for c in title if c.isalnum() or c in ' ._-')[:100]
            ext = info.get('ext', 'mp4')
            return output_path.replace('%(title)s', title).replace('%(ext)s', ext)
        elif output_path:
            return output_path
        else:
            return f"{info.get('title', 'video')}.{info.get('ext', 'mp4')}"

    @abstractmethod
    async def extract_info(self, url: str) -> Dict[str, Any]:
        """Extract video information from the given URL."""
        pass

    @abstractmethod
    async def download(self, url: str, format_id: str = "best", output_path: str = None) -> str:
        """Download video from the given URL."""
        pass
