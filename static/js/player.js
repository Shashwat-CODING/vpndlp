document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('playForm');
    const urlInput = document.getElementById('youtubeUrl');
    const playerContainer = document.getElementById('playerContainer');
    const errorContainer = document.getElementById('errorContainer');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const videoTitle = document.getElementById('videoTitle');

    // Custom player elements
    const playPauseBtn = document.getElementById('playPauseBtn');
    const progressBar = document.getElementById('progressBar');
    const progressBarInner = progressBar.querySelector('.progress-bar');
    const currentTimeSpan = document.getElementById('currentTime');
    const durationSpan = document.getElementById('duration');
    const volumeSlider = document.getElementById('volumeSlider');
    const muteBtn = document.getElementById('muteBtn');

    // Hidden audio element for actual playback
    const audio = new Audio();
    let isDragging = false;

    // Format time in MM:SS
    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        seconds = Math.floor(seconds % 60);
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    // Update play/pause button icon
    function updatePlayPauseIcon() {
        playPauseBtn.innerHTML = `<i class="bi bi-${audio.paused ? 'play' : 'pause'}-fill"></i>`;
    }

    // Update mute button icon
    function updateMuteIcon() {
        muteBtn.innerHTML = `<i class="bi bi-volume-${audio.muted ? 'mute' : 'up'}-fill"></i>`;
    }

    // Event listeners for custom player
    playPauseBtn.addEventListener('click', () => {
        if (audio.paused) {
            audio.play().catch(error => {
                console.error('Playback failed:', error);
                errorContainer.textContent = 'Failed to play audio. Please try again.';
                errorContainer.classList.remove('d-none');
            });
        } else {
            audio.pause();
        }
    });

    muteBtn.addEventListener('click', () => {
        audio.muted = !audio.muted;
        updateMuteIcon();
    });

    volumeSlider.addEventListener('input', (e) => {
        audio.volume = e.target.value / 100;
        if (audio.muted) {
            audio.muted = false;
            updateMuteIcon();
        }
    });

    progressBar.addEventListener('mousedown', (e) => {
        isDragging = true;
        const rect = progressBar.getBoundingClientRect();
        const pos = (e.clientX - rect.left) / rect.width;
        audio.currentTime = pos * audio.duration;
    });

    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            const rect = progressBar.getBoundingClientRect();
            const pos = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
            audio.currentTime = pos * audio.duration;
        }
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
    });

    // Audio element event listeners
    audio.addEventListener('play', updatePlayPauseIcon);
    audio.addEventListener('pause', updatePlayPauseIcon);
    audio.addEventListener('timeupdate', () => {
        if (!isDragging) {
            const progress = (audio.currentTime / audio.duration) * 100;
            progressBarInner.style.width = `${progress}%`;
            currentTimeSpan.textContent = formatTime(audio.currentTime);
        }
    });
    audio.addEventListener('loadedmetadata', () => {
        durationSpan.textContent = formatTime(audio.duration);
    });
    audio.addEventListener('error', () => {
        errorContainer.textContent = 'Error playing audio. Please try a different video.';
        errorContainer.classList.remove('d-none');
        playerContainer.classList.add('d-none');
    });

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Reset state
        errorContainer.classList.add('d-none');
        loadingSpinner.classList.remove('d-none');
        playerContainer.classList.remove('d-none');

        const formData = new FormData();
        formData.append('url', urlInput.value);

        try {
            const response = await fetch('/play', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                videoTitle.textContent = data.title;
                audio.src = data.audio_path;
                await audio.play();
            } else {
                throw new Error(data.error || 'Failed to process video');
            }
        } catch (error) {
            errorContainer.textContent = error.message;
            errorContainer.classList.remove('d-none');
            playerContainer.classList.add('d-none');
        } finally {
            loadingSpinner.classList.add('d-none');
        }
    });
});