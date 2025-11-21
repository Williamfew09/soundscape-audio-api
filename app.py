from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import uuid
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/download', methods=['POST'])
def download_audio():
    try:
        data = request.json
        video_url = data.get('url')
        
        if not video_url:
            return jsonify({'error': 'No URL provided'}), 400
        
        logger.info(f"Attempting to download: {video_url}")
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        output_template = os.path.join(temp_dir, 'audio')
        
        # Updated yt-dlp options for 2024
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'no_warnings': False,
            # Critical settings to avoid YouTube blocking
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'android', 'web'],
                    'player_skip': ['webpage', 'configs'],
                }
            },
            # Headers to mimic real browser
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                logger.info(f"Download successful for: {info.get('title', 'Unknown')}")
        except Exception as dl_error:
            logger.error(f"yt-dlp error: {str(dl_error)}")
            return jsonify({'error': f'Download failed: {str(dl_error)}'}), 500
            
        # Find the output file
        audio_file = output_template + '.mp3'
        
        if not os.path.exists(audio_file):
            # Try without extension
            if os.path.exists(output_template):
                audio_file = output_template
            else:
                logger.error(f"Audio file not found at: {audio_file}")
                return jsonify({'error': 'Audio file not created'}), 500
        
        logger.info(f"Sending file: {audio_file}")
        return send_file(
            audio_file,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='audio.mp3'
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'audio-converter', 'version': 'v2.0'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

**4. Commit changes: "Update to latest yt-dlp with iOS client"**

---

## ⏱️ **WAIT FOR RAILWAY REDEPLOY**

Railway will auto-rebuild (3-5 minutes):
- Building...
- Deploying...
- Active! ✅

---

## 🧪 **TEST IT**

Once Railway shows "Active":

**1. Go to n8n**

**2. Make sure "Download Audio" node has:**
```
Method: POST
URL: https://soundscape-audio-api-production.up.railway.app/download

Body (JSON):
{
  "url": "{{ $json.output.Selected[0].url }}"
}

Response Format: File
Put Output in Field: data
