import yt_dlp
import os
import re

class TikTokDownloader:
    def __init__(self):
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
                                'height': height
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
                            'quality': f'Quality ({fmt["height"]}p)'
                        })
                        seen_heights.add(fmt['height'])
                
                # Sort final formats by filesize
                final_formats.sort(key=lambda x: float(x['filesize'].replace('MB', '')), reverse=True)
                
                return final_formats
                
        except Exception as e:
            print(f"Error getting video info: {str(e)}")
            return []

    def download_video(self, url, selected_format=None):
        try:
            # Get available formats
            formats = self.get_video_info(url)
            
            if not formats:
                print("No formats available for this video.")
                return False
            
            # Show available formats
            print("\nAvailable video qualities:")
            for i, fmt in enumerate(formats, 1):
                print(f"{i}. {fmt['resolution']} ({fmt['quality']}) - Size: {fmt['filesize']}")
            
            # If only one format available, use it automatically
            if len(formats) == 1:
                selected_format = formats[0]
                print(f"\nOnly one quality available. Using: {selected_format['resolution']} ({selected_format['quality']}) - Size: {selected_format['filesize']}")
            else:
                # Let user choose format
                while True:
                    try:
                        choice = input(f"\nSelect quality (1-{len(formats)}, or Enter for best quality): ").strip()
                        if choice == "":
                            selected_format = formats[0]
                            print(f"Selected: {selected_format['resolution']} ({selected_format['quality']}) - Size: {selected_format['filesize']}")
                            break
                        choice = int(choice)
                        if 1 <= choice <= len(formats):
                            selected_format = formats[choice-1]
                            print(f"Selected: {selected_format['resolution']} ({selected_format['quality']}) - Size: {selected_format['filesize']}")
                            break
                        else:
                            print(f"Invalid choice. Please enter a number between 1 and {len(formats)}.")
                    except ValueError:
                        print("Please enter a valid number.")
            
            # Configure download options
            ydl_opts = {
                'format': selected_format['format_id'],
                'outtmpl': os.path.join(self.output_dir, '%(id)s.%(ext)s'),
                'quiet': False,
                'no_warnings': True,
                'merge_output_format': 'mp4',
            }
            
            # Download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"\nVideo successfully downloaded to {self.output_dir}")
            return True
            
        except Exception as e:
            print(f"Error downloading video: {str(e)}")
            return False

def main():
    downloader = TikTokDownloader()
    
    while True:
        url = input("\nEnter TikTok video URL (or 'q' to quit): ")
        
        if url.lower() == 'q':
            break
            
        downloader.download_video(url)

if __name__ == "__main__":
    main() 