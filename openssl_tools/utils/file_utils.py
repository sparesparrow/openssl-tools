#!/usr/bin/env python3
"""
File utilities for OpenSSL tools
"""

import os
import shutil
import hashlib
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class FileUtils:
    """File utility functions"""
    
    @staticmethod
    def find_files(pattern: str, root_dir: str = '.') -> List[str]:
        """Find files matching pattern"""
        files = []
        for root, dirs, filenames in os.walk(root_dir):
            for filename in filenames:
                if pattern in filename:
                    files.append(os.path.join(root, filename))
        return files
    
    @staticmethod
    def calculate_hash(file_path: str, algorithm: str = 'sha256') -> Optional[str]:
        """Calculate file hash"""
        try:
            hash_func = getattr(hashlib, algorithm)()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return None
    
    @staticmethod
    def ensure_directory(path: str) -> bool:
        """Ensure directory exists"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create directory {path}: {e}")
            return False
    
    @staticmethod
    def copy_file(src: str, dst: str) -> bool:
        """Copy file"""
        try:
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            logger.error(f"Failed to copy {src} to {dst}: {e}")
            return False
    
    @staticmethod
    def move_file(src: str, dst: str) -> bool:
        """Move file"""
        try:
            shutil.move(src, dst)
            return True
        except Exception as e:
            logger.error(f"Failed to move {src} to {dst}: {e}")
            return False
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete file"""
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            logger.error(f"Failed to delete {file_path}: {e}")
            return False
    
    @staticmethod
    def read_text_file(file_path: str) -> Optional[str]:
        """Read text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return None
    
    @staticmethod
    def write_text_file(file_path: str, content: str) -> bool:
        """Write text file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Failed to write {file_path}: {e}")
            return False