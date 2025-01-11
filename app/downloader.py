import yt_dlp
import os
import time

class TikTokDownloader:
    def __init__(self, app=None):
        if app:
            self.output_dir = app.config['DOWNLOAD_FOLDER']
        else:
            self.output_dir = "downloads"
        
        # Create downloads directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def get_video_info(self, url):
        """Get available video formats"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                
                # Filter for video formats
                video_formats = []
                for f in formats:
                    if f.get('vcodec') != 'none':
                        height = f.get('height', 0)
                        filesize = f.get('filesize', 0)
                        if height > 0 and filesize > 0:  # Only include valid formats
                            video_formats.append({
                                'resolution': f.get('resolution', 'N/A'),
                                'format_id': f.get('format_id', 'N/A'),
                                'filesize': filesize,
                                'height': height,
                                'is_audio': False
                            })
                
                # Sort by filesize first to get the best quality versions
                video_formats.sort(key=lambda x: x['filesize'], reverse=True)
                
                # Take the two largest files with unique heights
                final_formats = []
                seen_heights = set()
                
                for fmt in video_formats:
                    if len(final_formats) >= 2:
                        break
                        
                    if fmt['height'] not in seen_heights:
                        size_mb = fmt['filesize'] / (1024 * 1024)
                        final_formats.append({
                            'resolution': 'HD' if fmt['height'] >= 720 else 'Standard',
                            'format_id': fmt['format_id'],
                            'filesize': f"{size_mb:.1f}MB",
                            'quality': f'Quality ({fmt["height"]}p)',
                            'is_audio': False
                        })
                        seen_heights.add(fmt['height'])
                
                # Add MP3 option
                final_formats.append({
                    'resolution': 'Audio Only',
                    'format_id': 'bestaudio/best',
                    'filesize': 'Variable',
                    'quality': 'MP3 Audio',
                    'is_audio': True
                })
                
                return final_formats
                
        except Exception as e:
            print(f"Error getting video info: {str(e)}")
            return []

    def download_video(self, url, selected_format=None):
        try:
            if selected_format:
                # Generate filename
                is_audio = selected_format.get('is_audio', False)
                ext = 'mp3' if is_audio else 'mp4'
                filename = f"tiktok_{int(time.time())}.{ext}"
                filepath = os.path.join(self.output_dir, filename)
                
                # Configure download options
                if is_audio:
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': filepath,
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                        'prefer_ffmpeg': True,
                        'keepvideo': False,
                    }
                else:
                    ydl_opts = {
                        'format': selected_format['format_id'],
                        'outtmpl': filepath,
                        'merge_output_format': 'mp4',
                    }

                print(f"Starting download with options: {ydl_opts}")
                
                # Download the file
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    error_code = ydl.download([url])
                    print(f"Download completed with code: {error_code}")

                # For audio downloads, the final file will have .mp3 extension
                if is_audio:
                    mp3_path = filepath.rsplit('.', 1)[0] + '.mp3'
                    if os.path.exists(mp3_path):
                        print(f"Audio file found at: {mp3_path}")
                        return mp3_path
                    else:
                        print(f"Audio file not found at: {mp3_path}")
                else:
                    if os.path.exists(filepath):
                        print(f"Video file found at: {filepath}")
                        return filepath
                    else:
                        print(f"Video file not found at: {filepath}")

                return False

            return False
            
        except Exception as e:
            print(f"Error downloading: {str(e)}")
            import traceback
            traceback.print_exc()  # Print full error traceback
            return False 

    def get_video_metadata(self, url):
        """Get video metadata including thumbnail"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'thumbnail': info.get('thumbnail', ''),
                    'title': info.get('title', ''),
                    'duration': info.get('duration', 0)
                }
        except Exception as e:
            print(f"Error getting video metadata: {str(e)}")
            return {} 