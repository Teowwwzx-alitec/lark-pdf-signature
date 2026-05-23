/**
 * PDF Signature Frontend
 * Handles PDF display, signature box positioning, and submission
 */

// Setup PDF.js
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.14.159/pdf.worker.min.js';

let pdfDoc = null;
let currentPage = 1;
let canvas = document.getElementById('pdfCanvas');
let ctx = canvas.getContext('2d');
let signatureBox = document.getElementById('signatureBox');
let isDragging = false;
let dragOffsetX = 0;
let dragOffsetY = 0;
let pdfScale = 1;

// Get URL params
const urlParams = new URLSearchParams(window.location.search);
const recordId = urlParams.get('record_id');
const fileId = urlParams.get('file_id');
const tableId = urlParams.get('table_id');

// Validate params
if (!recordId || !fileId) {
    alert('Missing required parameters: record_id and file_id');
    window.close();
}

// Set timestamp
const now = new Date();
document.getElementById('timestamp').value = now.toLocaleString();

// Signature box drag handlers
signatureBox.addEventListener('mousedown', (e) => {
    isDragging = true;
    dragOffsetX = e.clientX - signatureBox.getBoundingClientRect().left;
    dragOffsetY = e.clientY - signatureBox.getBoundingClientRect().top;
    signatureBox.style.cursor = 'grabbing';
});

document.addEventListener('mousemove', (e) => {
    if (isDragging) {
        const pdfContainer = document.querySelector('.pdf-container');
        const containerRect = pdfContainer.getBoundingClientRect();
        
        let newX = e.clientX - containerRect.left - dragOffsetX;
        let newY = e.clientY - containerRect.top - dragOffsetY;
        
        // Clamp to container
        newX = Math.max(0, Math.min(newX, containerRect.width - signatureBox.offsetWidth));
        newY = Math.max(0, Math.min(newY, containerRect.height - signatureBox.offsetHeight));
        
        signatureBox.style.position = 'absolute';
        signatureBox.style.left = newX + 'px';
        signatureBox.style.top = newY + 'px';
    }
});

document.addEventListener('mouseup', () => {
    isDragging = false;
    signatureBox.style.cursor = 'grab';
});

/**
 * Render PDF page
 */
async function renderPage(pageNum) {
    try {
        const page = await pdfDoc.getPage(pageNum);
        
        // Set canvas dimensions based on PDF page
        const viewport = page.getViewport({ scale: pdfScale });
        canvas.width = viewport.width;
        canvas.height = viewport.height;
        
        // Render page
        await page.render({
            canvasContext: ctx,
            viewport: viewport
        }).promise;
        
        document.getElementById('status').textContent = `Page ${pageNum} of ${pdfDoc.numPages}`;
        
    } catch (error) {
        console.error('Error rendering page:', error);
        document.getElementById('status').textContent = 'Error rendering PDF: ' + error.message;
    }
}

/**
 * Load PDF from backend
 */
async function loadPDF() {
    try {
        document.getElementById('status').textContent = 'Loading PDF...';
        
        // Fetch PDF from backend
        const response = await fetch(`/api/pdf/${fileId}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch PDF: ${response.statusText}`);
        }
        
        const pdfData = await response.arrayBuffer();
        pdfDoc = await pdfjsLib.getDocument(pdfData).promise;
        
        // Render first page
        pdfScale = 1.5; // Scale up for better visibility
        await renderPage(1);
        
        // Position signature box
        const canvasRect = canvas.getBoundingClientRect();
        signatureBox.style.position = 'absolute';
        signatureBox.style.left = '50px';
        signatureBox.style.top = '50px';
        
        document.getElementById('status').textContent = 'Ready to sign - drag the signature box to position it';
        
    } catch (error) {
        console.error('Error loading PDF:', error);
        document.getElementById('status').textContent = 'Error loading PDF: ' + error.message;
    }
}

/**
 * Convert canvas/page pixel coordinates to PDF coordinates
 */
function canvasToPdfCoords(canvasX, canvasY, pageWidth, pageHeight) {
    // Get PDF dimensions
    const page = pdfDoc.pages[0]; // Get first page for reference
    
    // Simple conversion: scale based on canvas size
    const canvasWidth = canvas.width;
    const canvasHeight = canvas.height;
    
    // Convert pixel position to PDF points
    const pdfX = (canvasX / canvasWidth) * pageWidth;
    const pdfY = (canvasY / canvasHeight) * pageHeight;
    
    return { pdfX, pdfY };
}

/**
 * Submit signature and timestamp
 */
async function submitSignature() {
    try {
        const timestamp = document.getElementById('timestamp').value;
        const signaturePosition = signatureBox.getBoundingClientRect();
        const pdfContainerRect = document.querySelector('.pdf-container').getBoundingClientRect();
        
        // Position relative to PDF canvas
        const relX = signaturePosition.left - pdfContainerRect.left;
        const relY = signaturePosition.top - pdfContainerRect.top;
        
        const signatureData = {
            record_id: recordId,
            file_id: fileId,
            table_id: tableId || '',
            timestamp: timestamp,
            position: {
                x: relX,
                y: relY,
                width: signaturePosition.width,
                height: signaturePosition.height
            }
        };
        
        document.getElementById('signBtn').disabled = true;
        document.getElementById('signBtn').textContent = 'Signing...';
        document.getElementById('status').textContent = 'Signing PDF...';
        
        const response = await fetch(
            `/api/sign?record_id=${recordId}&file_id=${fileId}`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(signatureData)
            }
        );
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || `Signing failed: ${response.statusText}`);
        }
        
        document.getElementById('status').textContent = 'PDF signed successfully!';
        alert('PDF signed and uploaded successfully!');
        
        // Close window after short delay
        setTimeout(() => {
            window.close();
        }, 2000);
        
    } catch (error) {
        console.error('Error submitting signature:', error);
        alert('Error: ' + error.message);
        document.getElementById('status').textContent = 'Signing failed: ' + error.message;
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

// Make functions global for onclick handlers
window.submitSignature = submitSignature;
window.cancelSigning = cancelSigning;

// Load PDF on page load
window.addEventListener('load', loadPDF);
