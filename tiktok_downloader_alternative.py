import yt_dlp
import os
import re

class TikTokDownloader:
    def __init__(self):
        self.output_dir = "downloads"
        
        # Create downloads directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Configure yt-dlp options with a simpler filename pattern
        self.ydl_opts = {
            'format': 'best',
            # Use video ID for filename instead of video title
            'outtmpl': os.path.join(self.output_dir, '%(id)s.%(ext)s'),
            'quiet': False,
            'no_warnings': True,
        }

    def extract_video_id(self, url):
        """Extract video ID from TikTok URL"""
        pattern = r'video/(\d+)'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None

    def download_video(self, url):
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([url])
            print(f"Video successfully downloaded to {self.output_dir}")
            return True
        except Exception as e:
            print(f"Error downloading video: {str(e)}")
            return False

def main():
    downloader = TikTokDownloader()
    
    while True:
        url = input("Enter TikTok video URL (or 'q' to quit): ")
        
        if url.lower() == 'q':
            break
            
        downloader.download_video(url)

if __name__ == "__main__":
    main() 