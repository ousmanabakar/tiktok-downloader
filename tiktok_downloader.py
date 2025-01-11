import requests
from TikTokApi import TikTokApi
import os
import re

class TikTokDownloader:
    def __init__(self):
        self.api = TikTokApi()
        self.output_dir = "downloads"
        
        # Create downloads directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def extract_video_id(self, url):
        """Extract video ID from TikTok URL"""
        pattern = r'video/(\d+)'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None

    def download_video(self, url):
        try:
            # Extract video ID from URL
            video_id = self.extract_video_id(url)
            if not video_id:
                raise ValueError("Invalid TikTok URL")

            # Get video info
            video_data = self.api.video(id=video_id)
            
            # Get download URL
            download_url = video_data['itemInfo']['itemStruct']['video']['downloadAddr']
            
            # Generate filename
            filename = f"tiktok_video_{video_id}.mp4"
            filepath = os.path.join(self.output_dir, filename)

            # Download the video
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            # Save the video
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"Video successfully downloaded: {filepath}")
            return filepath

        except Exception as e:
            print(f"Error downloading video: {str(e)}")
            return None

def main():
    downloader = TikTokDownloader()
    
    while True:
        url = input("Enter TikTok video URL (or 'q' to quit): ")
        
        if url.lower() == 'q':
            break
            
        downloader.download_video(url)

if __name__ == "__main__":
    main() 