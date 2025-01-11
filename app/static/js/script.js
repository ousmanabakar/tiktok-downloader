document.addEventListener('DOMContentLoaded', function() {
    const videoUrlInput = document.getElementById('videoUrl');
    const checkButton = document.getElementById('checkButton');
    const downloadButton = document.getElementById('downloadButton');
    const qualityOptions = document.getElementById('qualityOptions');
    const optionsContainer = document.getElementById('optionsContainer');
    const status = document.getElementById('status');
    
    let selectedQuality = null;
    let selectedFormat = null;

    checkButton.addEventListener('click', async () => {
        const url = videoUrlInput.value.trim();
        if (!url) {
            status.textContent = 'Please enter a TikTok URL';
            return;
        }

        status.textContent = 'Checking video...';
        checkButton.disabled = true;
        
        try {
            const response = await fetch('/check-video', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url })
            });

            const data = await response.json();
            
            if (data.success) {
                showQualityOptions(data.formats, data.thumbnail);
                status.textContent = 'Select format to download';
            } else {
                status.textContent = data.error || 'Failed to get video info';
            }
        } catch (error) {
            status.textContent = 'Error checking video';
        } finally {
            checkButton.disabled = false;
        }
    });

    function showQualityOptions(formats, thumbnail) {
        const videoPreview = document.getElementById('videoPreview');
        const thumbnailImg = document.getElementById('thumbnailImg');
        
        if (thumbnail) {
            thumbnailImg.src = thumbnail;
            videoPreview.classList.add('show');
        }

        optionsContainer.innerHTML = '';
        formats.forEach((format, index) => {
            const option = document.createElement('div');
            option.className = 'option-item';
            if (format.is_audio) {
                option.classList.add('audio');
            }
            
            const icon = format.is_audio ? 'fa-music' : 'fa-video';
            const text = format.is_audio ? 
                `MP3 Audio (High Quality)` :
                `${format.resolution} (${format.quality}) - ${format.filesize}`;
            
            option.innerHTML = `
                <i class="fas ${icon}"></i>
                <span>${text}</span>
            `;
            
            option.addEventListener('click', () => {
                document.querySelectorAll('.option-item').forEach(item => {
                    item.classList.remove('selected');
                });
                option.classList.add('selected');
                selectedQuality = index;
                selectedFormat = format;
                downloadButton.disabled = false;
                
                // Update download button text based on format
                const buttonText = downloadButton.querySelector('.button-text');
                buttonText.innerHTML = format.is_audio ? 
                    '<i class="fas fa-music"></i> Download MP3' : 
                    '<i class="fas fa-video"></i> Download Video';
            });
            
            optionsContainer.appendChild(option);
        });
        
        qualityOptions.style.display = 'block';
    }

    downloadButton.addEventListener('click', async () => {
        if (selectedQuality === null) return;
        
        const url = videoUrlInput.value.trim();
        status.textContent = 'Downloading...';
        downloadButton.disabled = true;
        toggleLoader(true);
        
        try {
            const response = await fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url,
                    quality_index: selectedQuality
                })
            });

            const data = await response.json();
            
            if (data.success) {
                status.textContent = 'Download completed!';
                
                // Create a download link with suggested filename
                const ext = selectedFormat.is_audio ? 'mp3' : 'mp4';
                const timestamp = new Date().getTime();
                const suggestedName = `tiktok_${timestamp}.${ext}`;
                
                const link = document.createElement('a');
                link.href = data.download_url;
                link.download = suggestedName;
                link.style.display = 'none';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } else {
                status.textContent = data.error || 'Download failed';
            }
        } catch (error) {
            status.textContent = 'Error downloading';
            console.error('Download error:', error);
        } finally {
            downloadButton.disabled = false;
            toggleLoader(false);
        }
    });

    function toggleLoader(show) {
        const buttonText = downloadButton.querySelector('.button-text');
        const loader = downloadButton.querySelector('.loader');
        
        buttonText.style.display = show ? 'none' : 'block';
        loader.style.display = show ? 'block' : 'none';
    }
});