import re
import yt_dlp
import logging
import time
import os
import shutil
import pathlib
from urllib.parse import urlparse, parse_qs

# Configure logging
logger = logging.getLogger(__name__)

# Ensure the cookies file is properly set up
def ensure_cookies_file():
    """
    Make sure the cookies file is properly set up in the appropriate location
    Returns the path to the cookies file if successful, None otherwise
    """
    source_path = os.path.join(pathlib.Path(__file__).parent.absolute(), 'attached_assets', 'cookies.txt')
    target_path = os.path.join(pathlib.Path(__file__).parent.absolute(), 'cookies.txt')
    
    if os.path.exists(source_path):
        try:
            # Copy the file to the target location
            shutil.copy2(source_path, target_path)
            logger.info(f"Cookies file copied to {target_path}")
            return target_path
        except Exception as e:
            logger.error(f"Failed to copy cookies file: {str(e)}")
            # If we can't copy, try to use the original
            if os.path.exists(source_path):
                return source_path
    else:
        logger.warning(f"Cookies file not found at {source_path}")
    
    return None

def validate_youtube_url(url):
    """Validate YouTube URL format"""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    youtube_regex_match = re.match(youtube_regex, url)
    return bool(youtube_regex_match)

def get_audio_stream(url, max_retries=3):
    """
    Get direct stream URL from YouTube video
    
    Args:
        url: YouTube URL
        max_retries: Maximum number of retry attempts
        
    Returns:
        tuple: (stream_url, title)
        
    Raises:
        Exception: If unable to get the audio stream after retries
    """
    # Use our helper function to ensure cookie file is available
    cookie_file = ensure_cookies_file()
    if cookie_file:
        logger.info(f"Using cookies from: {cookie_file}")
    else:
        logger.warning("Unable to find or set up cookies file")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'geo_bypass': True,
        'geo_bypass_country': 'IN',  # Set to India
        'extract_flat': True,
        'no_check_certificates': True,
        'socket_timeout': 30,  # Increase socket timeout for VPN connections
        'retries': 5,  # Internal retries within yt-dlp
    }
    
    # Add cookies file if available
    if cookie_file:
        ydl_opts['cookiefile'] = cookie_file
    
    retry_count = 0
    last_error = None
    
    # Add proxy configuration if environment variables are set
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    
    if http_proxy or https_proxy:
        logger.info(f"Using proxy configuration from environment")
        if http_proxy:
            ydl_opts['proxy'] = http_proxy
        elif https_proxy:
            ydl_opts['proxy'] = https_proxy

    while retry_count < max_retries:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Attempting to extract info from {url} (attempt {retry_count + 1}/{max_retries})")
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise Exception("No video information returned")
                    
                formats = info.get('formats', [])
                if not formats:
                    raise Exception("No formats available for this video")
                
                # Get the best audio format URL
                audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
                
                if audio_formats:
                    # Sort by bitrate and get the best quality
                    best_audio = sorted(audio_formats, key=lambda x: x.get('abr', 0) or 0, reverse=True)[0]
                    stream_url = best_audio.get('url')
                    if not stream_url:
                        raise Exception("Audio URL not found in best audio format")
                    return stream_url, info.get('title', '')
                else:
                    # Fallback to best format if no audio-only format is available
                    if 'url' not in info:
                        raise Exception("URL not found in video info")
                    return info['url'], info.get('title', '')
                    
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Attempt {retry_count + 1}/{max_retries} failed: {last_error}")
            retry_count += 1
            if retry_count < max_retries:
                # Exponential backoff: 2, 4, 8... seconds
                sleep_time = 2 ** retry_count
                logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
    
    # If we've exhausted all retries
    error_msg = f"Failed to get audio stream after {max_retries} attempts: {last_error}"
    logger.error(error_msg)
    raise Exception(error_msg)