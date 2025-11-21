from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/download', methods=['POST'])
def download_audio():
    try:
        data = request.json
        video_url = data.get('url')
        
        if not video_url:
            return jsonify({'error': 'No URL provided'}), 400
        
        logger.info(f"Downloading: {video_url}")
        
        temp_dir = tempfile.mkdtemp()
        output_template = os.path.join(temp_dir, 'audio')
        
        # NUCLEAR OPTION - Every trick in the book
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'verbose': True,
            # iOS client - most reliable
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'mweb'],
                    'player_skip': ['configs', 'webpage'],
                    'skip': ['hls', 'dash'],
                }
            },
            # iOS app headers
            'http_headers': {
                'User-Agent': 'com.google.ios.youtube/19.29.1 (iPhone16,2; U; CPU iOS 17_5_1 like Mac OS X;)',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'X-Youtube-Client-Name': '5',
                'X-Youtube-Client-Version': '19.29.1',
            },
            # Additional bypass options
            'geo_bypass': True,
            'nocheckcertificate': True,
            'prefer_insecure': False,
            'no_check_certificate': True,
            # Retry settings
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                logger.info(f"Successfully downloaded: {info.get('title', 'Unknown')}")
        except Exception as e:
            logger.error(f"yt-dlp error: {str(e)}")
            return jsonify({'error': f'Download failed: {str(e)}'}), 500
            
        audio_file = output_template + '.mp3'
        
        # Check if file exists and has content
        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return jsonify({'error': 'Audio file not created'}), 500
        
        file_size = os.path.getsize(audio_file)
        if file_size == 0:
            logger.error("Audio file is empty")
            return jsonify({'error': 'Audi
