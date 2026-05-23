/**
 * PDF Signature Frontend
 * Handles PDF display, signature box positioning, and submission
 */

let pdfDoc = null;
let currentPage = 1;
let canvas = document.getElementById('pdfCanvas');
let ctx = canvas.getContext('2d');
let signatureBox = document.getElementById('signatureBox');
let isDragging = false;
let dragOffsetX = 0;
let dragOffsetY = 0;

// Get URL params
const urlParams = new URLSearchParams(window.location.search);
const recordId = urlParams.get('record_id');
const fileId = urlParams.get('file_id');

// Set timestamp
document.getElementById('timestamp').value = new Date().toLocaleString();

// Signature box drag handlers
signatureBox.addEventListener('mousedown', (e) => {
    isDragging = true;
    dragOffsetX = e.clientX - signatureBox.getBoundingClientRect().left;
    dragOffsetY = e.clientY - signatureBox.getBoundingClientRect().top;
});

document.addEventListener('mousemove', (e) => {
    if (isDragging) {
        signatureBox.style.position = 'fixed';
        signatureBox.style.left = (e.clientX - dragOffsetX) + 'px';
        signatureBox.style.top = (e.clientY - dragOffsetY) + 'px';
    }
});

document.addEventListener('mouseup', () => {
    isDragging = false;
});

/**
 * Load PDF from Lark
 * TODO: Implement actual PDF fetching from Lark
 */
async function loadPDF() {
    try {
        // Placeholder: will fetch actual PDF from backend
        // const response = await fetch(`/api/pdf/${recordId}/${fileId}`);
        // const blob = await response.blob();
        
        document.getElementById('status').textContent = 'Ready to sign';
        // TODO: Render PDF using PDF.js
    } catch (error) {
        console.error('Error loading PDF:', error);
        document.getElementById('status').textContent = 'Error loading PDF: ' + error.message;
    }
}

/**
 * Submit signature and timestamp
 */
async function submitSignature() {
    try {
        const timestamp = document.getElementById('timestamp').value;
        const signaturePosition = signatureBox.getBoundingClientRect();

        const signatureData = {
            record_id: recordId,
            file_id: fileId,
            timestamp: timestamp,
            position: {
                x: signaturePosition.x,
                y: signaturePosition.y,
                width: signaturePosition.width,
                height: signaturePosition.height
            }
        };

        document.getElementById('signBtn').disabled = true;
        document.getElementById('signBtn').textContent = 'Signing...';

        const response = await fetch('/api/sign', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(signatureData)
        });

        if (!response.ok) {
            throw new Error(`Signing failed: ${response.statusText}`);
        }

        const result = await response.json();
        
        if (result.status === 'success') {
            alert('PDF signed successfully!');
            window.close();
        } else {
            alert('Signing error: ' + result.message);
        }
    } catch (error) {
        console.error('Error submitting signature:', error);
        alert('Error: ' + error.message);
    } finally {
        document.getElementById('signBtn').disabled = false;
        document.getElementById('signBtn').textContent = 'Sign PDF';
    }
}

/**
 * Cancel signing
 */
function cancelSigning() {
    if (confirm('Cancel signing?')) {
        window.close();
    }
}

// Load PDF on page load
window.addEventListener('load', loadPDF);
