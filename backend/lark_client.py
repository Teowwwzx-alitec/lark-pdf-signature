"""
Lark API Client
Handles authentication and API calls to Lark
"""

import os
import logging
from typing import Optional
import requests
from functools import lru_cache
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class LarkClient:
    """Lark OpenAPI client with token caching"""
    
    def __init__(self):
        self.app_id = os.getenv('LARK_APP_ID')
        self.app_secret = os.getenv('LARK_APP_SECRET')
        self.api_base = os.getenv('LARK_API_BASE', 'https://open.larksuite.com')
        self.tenant_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        
        if not self.app_id or not self.app_secret:
            raise ValueError("LARK_APP_ID and LARK_APP_SECRET must be set")
    
    def get_tenant_token(self) -> str:
        """
        Get or refresh tenant access token
        Tokens are cached and reused until expiration
        """
        # Return cached token if still valid
        if self.tenant_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            logger.debug("Using cached tenant token")
            return self.tenant_token
        
        logger.info("Fetching new tenant token from Lark API")
        url = f"{self.api_base}/open-apis/auth/v3/tenant_access_token/internal"
        
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") != 0:
                raise Exception(f"Lark API error: {data.get('msg')}")
            
            self.tenant_token = data["tenant_access_token"]
            expires_in = data.get("expire", 7200)  # Default 2 hours
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)  # Refresh 5 min early
            
            logger.info(f"Tenant token obtained, expires in {expires_in} seconds")
            return self.tenant_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get tenant token: {e}")
            raise
    
    def get_file(self, file_id: str) -> bytes:
        """
        Download a file from Lark Drive
        
        Args:
            file_id: The file ID from Lark
        
        Returns:
            File content as bytes
        """
        token = self.get_tenant_token()
        url = f"{self.api_base}/open-apis/drive/v1/files/{file_id}/download"
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Downloaded file {file_id}, size: {len(response.content)} bytes")
            return response.content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download file {file_id}: {e}")
            raise
    
    def upload_file(self, file_name: str, file_content: bytes, parent_token: str) -> str:
        """
        Upload a file to Lark Drive
        
        Args:
            file_name: Name for the file
            file_content: File content as bytes
            parent_token: Parent folder token (usually a record ID or folder ID)
        
        Returns:
            The uploaded file ID
        """
        token = self.get_tenant_token()
        url = f"{self.api_base}/open-apis/drive/v1/files"
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        files = {
            'file': (file_name, file_content, 'application/pdf')
        }
        
        data = {
            'parent_token': parent_token,
            'parent_type': 'bitable_file'  # Lark Base/Sheet
        }
        
        try:
            response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("code") != 0:
                raise Exception(f"Lark API error: {result.get('msg')}")
            
            file_id = result["data"]["file_id"]
            logger.info(f"File uploaded, ID: {file_id}")
            return file_id
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to upload file: {e}")
            raise
    
    def update_record(self, table_id: str, record_id: str, fields: dict) -> bool:
        """
        Update a Lark Base record with new field values
        
        Args:
            table_id: The table ID in Lark Base
            record_id: The record ID to update
            fields: Dictionary of field_name -> value to update
        
        Returns:
            True if successful
        """
        token = self.get_tenant_token()
        url = f"{self.api_base}/open-apis/bitable/v1/apps/tables/{table_id}/records/{record_id}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "fields": fields
        }
        
        try:
            response = requests.put(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("code") != 0:
                raise Exception(f"Lark API error: {result.get('msg')}")
            
            logger.info(f"Record {record_id} updated successfully")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update record {record_id}: {e}")
            raise
    
    def get_record(self, table_id: str, record_id: str) -> dict:
        """
        Get a Lark Base record
        
        Args:
            table_id: The table ID in Lark Base
            record_id: The record ID to fetch
        
        Returns:
            Record data as dictionary
        """
        token = self.get_tenant_token()
        url = f"{self.api_base}/open-apis/bitable/v1/apps/tables/{table_id}/records/{record_id}"
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("code") != 0:
                raise Exception(f"Lark API error: {result.get('msg')}")
            
            logger.info(f"Record {record_id} retrieved")
            return result.get("data", {})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get record {record_id}: {e}")
            raise


# Singleton instance
_lark_client = None

def get_lark_client() -> LarkClient:
    """Get or create the Lark client singleton"""
    global _lark_client
    if _lark_client is None:
        _lark_client = LarkClient()
    return _lark_client
