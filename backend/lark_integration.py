"""
Lark Integration - Record Updates
Handles uploading signed PDFs and updating record fields
"""

import logging
from lark_client import get_lark_client

logger = logging.getLogger(__name__)

class LarkIntegration:
    """Handle Lark-specific operations"""
    
    def __init__(self):
        self.lark_client = get_lark_client()
    
    def upload_signed_pdf(self, signed_pdf_content: bytes, file_name: str, parent_token: str) -> str:
        """
        Upload signed PDF to Lark Drive
        
        Args:
            signed_pdf_content: Signed PDF bytes
            file_name: Name for the file (e.g., "document_signed.pdf")
            parent_token: Parent location token (Base record ID or folder ID)
        
        Returns:
            File ID of uploaded PDF
        """
        try:
            file_id = self.lark_client.upload_file(
                file_name=file_name,
                file_content=signed_pdf_content,
                parent_token=parent_token
            )
            logger.info(f"Signed PDF uploaded: {file_id}")
            return file_id
        except Exception as e:
            logger.error(f"Failed to upload signed PDF: {e}")
            raise
    
    def update_record_timestamp(self, 
                               table_id: str, 
                               record_id: str,
                               timestamp_field: str,
                               timestamp_value: str,
                               signed_file_id: str = None) -> bool:
        """
        Update a Lark Base record with signature timestamp and file
        
        Args:
            table_id: The table ID in Lark Base
            record_id: The record ID to update
            timestamp_field: Name of the datetime field
            timestamp_value: The timestamp value to set
            signed_file_id: Optional file ID of signed PDF
        
        Returns:
            True if successful
        """
        try:
            fields = {}
            
            # Add timestamp
            if timestamp_field:
                fields[timestamp_field] = timestamp_value
            
            # Add signed PDF file if provided
            if signed_file_id:
                # Assuming there's a "Signed PDF" attachment field
                # This depends on your actual Base structure
                fields['Signed PDF'] = [{"file_id": signed_file_id}]
            
            success = self.lark_client.update_record(table_id, record_id, fields)
            logger.info(f"Record {record_id} updated with timestamp and signed PDF")
            return success
            
        except Exception as e:
            logger.error(f"Failed to update record: {e}")
            raise
    
    def mark_signed(self,
                   table_id: str,
                   record_id: str,
                   status_field: str = "Status") -> bool:
        """
        Mark a record as signed
        
        Args:
            table_id: The table ID
            record_id: The record ID
            status_field: Name of the status field
        
        Returns:
            True if successful
        """
        try:
            self.lark_client.update_record(
                table_id,
                record_id,
                {status_field: "Signed"}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to mark record as signed: {e}")
            raise


# Global instance
_lark_integration = None

def get_lark_integration() -> LarkIntegration:
    """Get or create Lark integration instance"""
    global _lark_integration
    if _lark_integration is None:
        _lark_integration = LarkIntegration()
    return _lark_integration
