import yt_dlp
import os
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread

class TikTokDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TikTok Video Downloader")
        self.root.geometry("600x400")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize downloader
        self.downloader = TikTokDownloader()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            self.main_frame, 
            text="TikTok Video Downloader",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # URL Entry
        url_frame = ttk.Frame(self.main_frame)
        url_frame.pack(fill=tk.X, pady=10)
        
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=50)
        url_entry.pack(side=tk.LEFT, padx=5)
        
        check_btn = ttk.Button(
            url_frame,
            text="Check Video",
            command=self.check_video
        )
        check_btn.pack(side=tk.LEFT, padx=5)
        
        # Quality Selection
        self.quality_frame = ttk.LabelFrame(self.main_frame, text="Available Qualities", padding="10")
        self.quality_frame.pack(fill=tk.X, pady=10)
        
        self.quality_var = tk.StringVar()
        self.quality_options = ttk.Frame(self.quality_frame)
        self.quality_options.pack(fill=tk.X)
        
        # Download Button
        self.download_btn = ttk.Button(
            self.main_frame,
            text="Download Video",
            command=self.start_download,
            state=tk.DISABLED
        )
        self.download_btn.pack(pady=10)
        
        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            self.main_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress.pack(fill=tk.X, pady=10)
        
        # Status
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_label = ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            font=("Helvetica", 10)
        )
        status_label.pack(pady=5)

    def check_video(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a TikTok URL")
            return
            
        self.status_var.set("Checking video...")
        self.clear_quality_options()
        
        # Run in thread to prevent GUI freeze
        Thread(target=self._check_video_thread, args=(url,), daemon=True).start()

    def _check_video_thread(self, url):
        try:
            formats = self.downloader.get_video_info(url)
            
            if not formats:
                self.root.after(0, lambda: self.status_var.set("No formats available"))
                return
                
            self.root.after(0, lambda: self.show_quality_options(formats))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))

    def clear_quality_options(self):
        for widget in self.quality_options.winfo_children():
            widget.destroy()
        self.download_btn.config(state=tk.DISABLED)

    def show_quality_options(self, formats):
        self.clear_quality_options()
        self.formats = formats
        
        for i, fmt in enumerate(formats):
            radio = ttk.Radiobutton(
                self.quality_options,
                text=f"{fmt['resolution']} ({fmt['quality']}) - Size: {fmt['filesize']}",
                value=str(i),
                variable=self.quality_var
            )
            radio.pack(anchor=tk.W)
        
        self.quality_var.set("0")  # Select first option by default
        self.download_btn.config(state=tk.NORMAL)
        self.status_var.set("Ready to download")

    def start_download(self):
        url = self.url_var.get().strip()
        selected_idx = int(self.quality_var.get())
        selected_format = self.formats[selected_idx]
        
        self.download_btn.config(state=tk.DISABLED)
        self.status_var.set("Downloading...")
        self.progress_var.set(0)
        
        # Run download in thread
        Thread(target=self._download_thread, args=(url, selected_format), daemon=True).start()

    def _download_thread(self, url, selected_format):
        try:
            success = self.downloader.download_video(url, selected_format)
            if success:
                self.root.after(0, lambda: self.status_var.set("Download completed!"))
                self.root.after(0, lambda: self.progress_var.set(100))
            else:
                self.root.after(0, lambda: self.status_var.set("Download failed"))
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.download_btn.config(state=tk.NORMAL))

class TikTokDownloader:
    # Your existing TikTokDownloader class code here
    # (Keep all the existing methods)
    pass

def main():
    root = tk.Tk()
    app = TikTokDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 