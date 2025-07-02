class QRCodeGenerator {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.currentQRData = null;
    }

    initializeElements() {
        this.textInput = document.getElementById('textInput');
        this.sizeSelect = document.getElementById('sizeSelect');
        this.generateBtn = document.getElementById('generateBtn');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.qrContainer = document.getElementById('qrContainer');
        this.downloadSection = document.getElementById('downloadSection');
        this.errorMessage = document.getElementById('errorMessage');
        this.loadingMessage = document.getElementById('loadingMessage');
    }

    bindEvents() {
        this.generateBtn.addEventListener('click', () => this.generateQRCode());
        this.downloadBtn.addEventListener('click', () => this.downloadQRCode());
        
        // Generate QR code on Enter key press
        this.textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.generateQRCode();
            }
        });

        // Clear messages when input changes
        this.textInput.addEventListener('input', () => {
            this.hideMessages();
        });
    }

    async generateQRCode() {
        const text = this.textInput.value.trim();
        
        if (!text) {
            this.showError('Please enter some text or URL to generate QR code');
            return;
        }

        this.showLoading();
        this.generateBtn.disabled = true;
        
        try {
            const size = parseInt(this.sizeSelect.value);
            const qrData = await this.callBackendAPI(text, size);
            
            this.displayQRCode(qrData);
            this.hideMessages();
            this.showDownloadSection();
            
        } catch (error) {
            this.showError('Failed to generate QR code. Please try again.');
            console.error('QR generation error:', error);
        } finally {
            this.generateBtn.disabled = false;
            this.hideLoading();
        }
    }

    async callBackendAPI(text, size) {
        const response = await fetch('http://localhost:8000/generate-qr', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                size: size
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    }

    displayQRCode(qrData) {
        this.currentQRData = qrData;
        
        // Create image element
        const img = document.createElement('img');
        img.src = `data:image/png;base64,${qrData.image}`;
        img.alt = 'Generated QR Code';
        img.style.maxWidth = '100%';
        img.style.height = 'auto';
        
        // Clear container and add image
        this.qrContainer.innerHTML = '';
        this.qrContainer.appendChild(img);
        this.qrContainer.classList.add('has-qr');
    }

    downloadQRCode() {
        if (!this.currentQRData) {
            this.showError('No QR code to download');
            return;
        }

        try {
            // Create download link
            const link = document.createElement('a');
            link.href = `data:image/png;base64,${this.currentQRData.image}`;
            link.download = `qrcode_${Date.now()}.png`;
            
            // Trigger download
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
        } catch (error) {
            this.showError('Failed to download QR code');
            console.error('Download error:', error);
        }
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorMessage.style.display = 'block';
        this.hideLoading();
    }

    showLoading() {
        this.loadingMessage.style.display = 'block';
        this.hideError();
    }

    hideLoading() {
        this.loadingMessage.style.display = 'none';
    }

    hideError() {
        this.errorMessage.style.display = 'none';
    }

    hideMessages() {
        this.hideError();
        this.hideLoading();
    }

    showDownloadSection() {
        this.downloadSection.style.display = 'block';
    }
}

// Initialize the QR Code Generator when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new QRCodeGenerator();
});

// Fallback for older browsers
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new QRCodeGenerator();
    });
} else {
    new QRCodeGenerator();
}