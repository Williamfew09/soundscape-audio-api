from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import uuid

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download_audio():
    try:
        data = request.json
        video_url = data.get('url')
        
        if not video_url:
            return jsonify({'error': 'No URL provided'}), 400
        
        temp_dir = tempfile.mkdtemp()
        output_template = os.path.join(temp_dir, 'audio.%(ext)s')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(video_url, download=True)
            
        audio_file = os.path.join(temp_dir, 'audio.mp3')
        
        if not os.path.exists(audio_file):
            return jsonify({'error': 'Audio file not created'}), 500
            
        return send_file(
            audio_file,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='audio.mp3'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'audio-converter'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
