"""
PDF Signing Handler
Embeds signature and timestamp into PDFs
"""

import logging
from io import BytesIO
from datetime import datetime
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import RectangleObject, NameObject, TextStringObject

logger = logging.getLogger(__name__)

class SigningHandler:
    """Handle PDF signing operations"""
    
    def __init__(self):
        self.dpi = 72  # Standard PDF DPI
    
    def create_signature_image(self, width: int, height: int, timestamp: str) -> Image.Image:
        """
        Create a signature image with timestamp text
        
        Args:
            width: Signature box width in pixels
            height: Signature box height in pixels
            timestamp: Timestamp string to embed
        
        Returns:
            PIL Image object
        """
        # Create white background
        sig_image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(sig_image)
        
        # Add border
        border_color = (0, 0, 0)
        draw.rectangle([(0, 0), (width-1, height-1)], outline=border_color, width=2)
        
        # Add timestamp text
        try:
            # Try to use a nice font, fall back to default
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        except:
            font = ImageFont.load_default()
        
        # Draw timestamp text centered
        text = f"Signed\n{timestamp}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill=(0, 0, 0), font=font)
        
        return sig_image
    
    def pixel_to_pdf_coords(self, 
                           pixel_x: float, 
                           pixel_y: float, 
                           page_width: float, 
                           page_height: float,
                           canvas_width: int = 800,
                           canvas_height: int = 600) -> Tuple[float, float]:
        """
        Convert browser canvas pixel coordinates to PDF coordinates
        
        PDF coordinates: origin at bottom-left, Y increases upward
        Canvas coordinates: origin at top-left, Y increases downward
        
        Args:
            pixel_x: X position in canvas pixels
            pixel_y: Y position in canvas pixels
            page_width: PDF page width in points
            page_height: PDF page height in points
            canvas_width: Canvas display width in pixels
            canvas_height: Canvas display height in pixels
        
        Returns:
            Tuple of (pdf_x, pdf_y) in PDF points
        """
        # Scale from canvas to PDF
        scale_x = page_width / canvas_width
        scale_y = page_height / canvas_height
        
        # Convert to PDF coordinates
        pdf_x = pixel_x * scale_x
        pdf_y = page_height - (pixel_y * scale_y)  # Flip Y axis
        
        return pdf_x, pdf_y
    
    def sign_pdf(self,
                 pdf_content: bytes,
                 signature_x: float,
                 signature_y: float,
                 signature_width: float,
                 signature_height: float,
                 timestamp: str,
                 page_index: int = 0) -> bytes:
        """
        Add signature and timestamp to a PDF
        
        Args:
            pdf_content: Original PDF file content
            signature_x: X position in PDF points
            signature_y: Y position in PDF points
            signature_width: Width in PDF points
            signature_height: Height in PDF points
            timestamp: Timestamp string
            page_index: Page index to sign (0-based)
        
        Returns:
            Signed PDF content as bytes
        """
        try:
            # Read original PDF
            pdf_reader = PdfReader(BytesIO(pdf_content))
            pdf_writer = PdfWriter()
            
            if page_index >= len(pdf_reader.pages):
                raise ValueError(f"Page {page_index} not found in PDF")
            
            page = pdf_reader.pages[page_index]
            page_width = float(page.mediabox[2])
            page_height = float(page.mediabox[3])
            
            logger.info(f"PDF page size: {page_width} x {page_height} points")
            
            # Create signature image
            sig_img_width = int(signature_width)
            sig_img_height = int(signature_height)
            signature_image = self.create_signature_image(sig_img_width, sig_img_height, timestamp)
            
            # Save image to bytes
            img_buffer = BytesIO()
            signature_image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Overlay image on PDF
            # Create a new PDF with just the image overlay
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import pt
            
            overlay_buffer = BytesIO()
            c = canvas.Canvas(overlay_buffer, pagesize=(page_width, page_height))
            
            # Convert pixel position to PDF coordinates
            # signature_x, signature_y are already in PDF space from frontend
            c.drawImage(img_buffer, 
                       signature_x, 
                       page_height - signature_y - signature_height,  # Adjust for PDF coords
                       width=signature_width, 
                       height=signature_height,
                       preserveAspectRatio=False)
            
            c.save()
            overlay_buffer.seek(0)
            
            # Merge overlay with original page
            overlay_reader = PdfReader(overlay_buffer)
            overlay_page = overlay_reader.pages[0]
            page.merge_page(overlay_page)
            
            # Add all pages to writer
            pdf_writer.add_page(page)
            for i, p in enumerate(pdf_reader.pages):
                if i != page_index:
                    pdf_writer.add_page(p)
            
            # Write output
            output_buffer = BytesIO()
            pdf_writer.write(output_buffer)
            output_buffer.seek(0)
            
            signed_pdf = output_buffer.getvalue()
            logger.info(f"PDF signed successfully ({len(signed_pdf)} bytes)")
            
            return signed_pdf
            
        except Exception as e:
            logger.error(f"Error signing PDF: {e}")
            raise
    
    def validate_signature_params(self,
                                 signature_x: float,
                                 signature_y: float,
                                 signature_width: float,
                                 signature_height: float,
                                 page_width: float,
                                 page_height: float) -> bool:
        """
        Validate that signature parameters are within PDF bounds
        
        Args:
            signature_x, signature_y: Position
            signature_width, signature_height: Dimensions
            page_width, page_height: PDF page dimensions
        
        Returns:
            True if valid
        """
        if signature_width <= 0 or signature_height <= 0:
            raise ValueError("Signature dimensions must be positive")
        
        if signature_x < 0 or signature_y < 0:
            raise ValueError("Signature position cannot be negative")
        
        if (signature_x + signature_width) > page_width:
            raise ValueError(f"Signature extends beyond page width")
        
        if (signature_y + signature_height) > page_height:
            raise ValueError(f"Signature extends beyond page height")
        
        return True


# Global handler instance
_signing_handler = None

def get_signing_handler() -> SigningHandler:
    """Get or create the signing handler singleton"""
    global _signing_handler
    if _signing_handler is None:
        _signing_handler = SigningHandler()
    return _signing_handler
