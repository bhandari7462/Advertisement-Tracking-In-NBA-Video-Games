const youtubeInput = document.getElementById('youtube-url');
const youtubeContainer = document.getElementById('youtube-container');
const expandedContent = document.getElementById('expanded-content');
const initialInput = document.getElementById('initial-input');
const analyzeBtn = document.querySelector('.analyze-btn');
const processingMsg = document.getElementById('processing-msg');

youtubeInput.addEventListener('input', function() {
    const url = this.value.trim();
    if (url) {
        loadYouTubeVideo(url);
    }
});

function loadYouTubeVideo(url) {
    const videoId = extractVideoId(url);
    if (videoId) {
        // Hide initial input and show the expanded content
        initialInput.style.display = 'none';
        expandedContent.classList.add('show');
        
        // Load the video
        const embedUrl = `https://www.youtube.com/embed/${videoId}`;
        youtubeContainer.innerHTML = `<iframe src="${embedUrl}" allowfullscreen></iframe>`;
        youtubeContainer.classList.add('loaded');
        document.querySelector('.youtube-placeholder').style.display = 'none';
        
    } else {
            // If URL is invalid or cleared, revert the view
        youtubeContainer.innerHTML = `<div class="youtube-placeholder"><i>📺</i><div>Waiting for valid URL...</div></div>`;
        youtubeContainer.classList.remove('loaded');
            if (expandedContent.classList.contains('show')) {
            initialInput.style.display = 'block';
            expandedContent.classList.remove('show');
        }
    }
}

function extractVideoId(url) {
    const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/;
    const match = url.match(regex);
    return match ? match[1] : null;
}

function toggleCheckbox(id) {
    const checkbox = document.getElementById(id);
    const item = checkbox.parentElement;
    
    checkbox.checked = !checkbox.checked;
    
    if (checkbox.checked) {
        item.classList.add('selected');
    } else {
        item.classList.remove('selected');
    }
}

function selectRadio(id) {
    document.querySelectorAll('.radio-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    const radioItem = document.getElementById(id).parentElement;
    radioItem.classList.add('selected');
    
    document.getElementById(id).checked = true;
}

function startAnalysis() {
    const youtubeUrl = document.getElementById('youtube-url').value.trim();
    const email = document.getElementById('email').value.trim();
    
    const selectedBrands = [];
    document.querySelectorAll('.checkbox-item input[type="checkbox"]:checked').forEach(checkbox => {
        selectedBrands.push(checkbox.value);
    });
    
    const selectedModel = document.querySelector('input[name="model"]:checked').value;

    if (!youtubeUrl || selectedBrands.length === 0 || !email) {
        alert('Please ensure you have a valid video URL, have selected at least one brand, and entered your email address.');
        return;
    }

    if (!extractVideoId(youtubeUrl)) {
            alert('Please enter a valid YouTube URL.');
        return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert('Please enter a valid email address.');
        return;
    }

    analyzeBtn.classList.add('processing');
    analyzeBtn.innerHTML = '<span class="spinner"></span>Processing...';
    analyzeBtn.disabled = true;

    setTimeout(() => {
        processingMsg.classList.add('show');
        
        const analysisData = {
            youtubeUrl: youtubeUrl,
            brands: selectedBrands,
            model: selectedModel,
            email: email,
            timestamp: new Date().toISOString()
        };
        
        console.log('Analysis started with data:', analysisData);
        fetch("/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(analysisData)
            })
            .then(response => response.json())
            .then(data => {
            console.log("✅ Analysis started:", data);
            alert("✅ Your request has been submitted! You'll receive an email when it's ready.");
            })
            .catch(error => {
            console.error("❌ Error starting analysis:", error);
            alert("❌ Something went wrong. Please try again.");
            });

        setTimeout(() => {
            analyzeBtn.classList.remove('processing');
            analyzeBtn.innerHTML = '🚀 Start Another Analysis';
            analyzeBtn.disabled = false;
        }, 4000); // Keep button disabled a bit longer
    }, 1000);
}
function pollForResult(taskId) {
    const checkInterval = setInterval(() => {
        fetch(`/result/${taskId}`)
            .then(response => {
                if (response.status === 200 && response.headers.get('Content-Type') === 'application/pdf') {
                    clearInterval(checkInterval);
                    document.getElementById('processing-msg').classList.remove('show');

                    response.blob().then(blob => {
                        const url = URL.createObjectURL(blob);
                        const iframe = document.createElement('iframe');
                        iframe.src = url;
                        iframe.style.width = '100%';
                        iframe.style.height = '600px';
                        iframe.style.border = 'none';

                        const viewerContainer = document.createElement('div');
                        viewerContainer.className = 'glass-card';
                        viewerContainer.appendChild(iframe);

                        document.querySelector('.main-content').appendChild(viewerContainer);
                    });
                } else {
                    return response.json();
                }
            })
            .then(data => {
                if (data?.status === "failed") {
                    clearInterval(checkInterval);
                    alert("❌ Analysis failed. Please try again.");
                }
            })
            .catch(err => {
                console.error("Polling error:", err);
                clearInterval(checkInterval);
            });
    }, 3000);
}

// Add some interactive effects to input fields
document.querySelectorAll('.input-field').forEach(input => {
    input.addEventListener('focus', function() {
        this.parentElement.style.transform = 'translateY(-2px)';
    });
    
    input.addEventListener('blur', function() {
        this.parentElement.style.transform = 'translateY(0)';
    });
});