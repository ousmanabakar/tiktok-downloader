from flask import Flask, render_template, jsonify, request, send_from_directory
from app.downloader import TikTokDownloader
import os

app = Flask(__name__, 
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'templates'),
    static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static')
)

# Set download folder path
app.config['DOWNLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'downloads')

# Initialize downloader
downloader = TikTokDownloader(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check-video', methods=['POST'])
def check_video():
    try:
        url = request.json.get('url')
        formats = downloader.get_video_info(url)
        
        # Get video thumbnail
        video_info = downloader.get_video_metadata(url)
        thumbnail_url = video_info.get('thumbnail', '')
        
        if formats:
            return jsonify({
                'success': True,
                'formats': formats,
                'thumbnail': thumbnail_url
            })
        return jsonify({
            'success': False,
            'error': 'No formats available'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/download', methods=['POST'])
def download_video():
    try:
        url = request.json.get('url')
        quality_index = int(request.json.get('quality_index', 0))
        
        formats = downloader.get_video_info(url)
        if not formats or quality_index >= len(formats):
            return jsonify({
                'success': False,
                'error': 'Invalid quality selection'
            })
            
        selected_format = formats[quality_index]
        filepath = downloader.download_video(url, selected_format)
        
        if filepath:
            filename = os.path.basename(filepath)
            download_url = f'/downloads/{filename}'
            return jsonify({
                'success': True,
                'download_url': download_url
            })
        return jsonify({
            'success': False,
            'error': 'Download failed'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True) 