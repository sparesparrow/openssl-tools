#!/usr/bin/env python3
"""
API client utilities for OpenSSL tools
"""

import os
import requests
import logging
from typing import Dict, Any, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class APIClient:
    """Generic API client"""
    
    def __init__(self, base_url: str, token: Optional[str] = None):
        """Initialize API client"""
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Make GET request"""
        try:
            url = urljoin(self.base_url, endpoint)
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"GET request failed: {e}")
            return None
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Make POST request"""
        try:
            url = urljoin(self.base_url, endpoint)
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"POST request failed: {e}")
            return None
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Make PUT request"""
        try:
            url = urljoin(self.base_url, endpoint)
            response = self.session.put(url, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"PUT request failed: {e}")
            return None
    
    def delete(self, endpoint: str) -> bool:
        """Make DELETE request"""
        try:
            url = urljoin(self.base_url, endpoint)
            response = self.session.delete(url)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"DELETE request failed: {e}")
            return False