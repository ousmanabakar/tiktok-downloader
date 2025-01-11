document.addEventListener('DOMContentLoaded', function() {
    const videoUrlInput = document.getElementById('videoUrl');
    const checkButton = document.getElementById('checkButton');
    const downloadButton = document.getElementById('downloadButton');
    const qualityOptions = document.getElementById('qualityOptions');
    const optionsContainer = document.getElementById('optionsContainer');
    const status = document.getElementById('status');
    
    let selectedQuality = null;

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
                downloadButton.disabled = false;
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
                window.location.href = data.download_url;
            } else {
                status.textContent = data.error || 'Download failed';
            }
        } catch (error) {
            status.textContent = 'Error downloading';
        } finally {
            downloadButton.disabled = false;
        }
    });
});