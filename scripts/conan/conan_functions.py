#!/usr/bin/env python3
"""
Conan Functions Module
Core functions for Conan package management
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Dict, List

def get_default_conan():
    """Get default Conan installation"""
    try:
        result = subprocess.run(["conan", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            return "conan"
    except FileNotFoundError:
        pass
    
    # Try to find conan in various locations
    conan_paths = [
        "/usr/local/bin/conan",
        "/usr/bin/conan",
        os.path.expanduser("~/.local/bin/conan"),
        "C:\\Python\\Scripts\\conan.exe",
        "C:\\Program Files\\Python\\Scripts\\conan.exe"
    ]
    
    for path in conan_paths:
        if os.path.exists(path):
            try:
                result = subprocess.run([path, "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    return path
            except Exception:
                continue
    
    raise RuntimeError("Conan not found in PATH or standard locations")

def validate_conan_installation():
    """Validate Conan installation and configuration"""
    try:
        conan_cmd = get_default_conan()
        
        # Check version
        result = subprocess.run([conan_cmd, "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            return False, "Conan command failed"
        
        version_info = result.stdout.strip()
        if "Conan version 2." not in version_info:
            return False, f"Unsupported Conan version: {version_info}"
        
        # Check profile detection
        result = subprocess.run([conan_cmd, "profile", "detect", "--force"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            return False, "Profile detection failed"
        
        return True, "Conan installation valid"
        
    except Exception as e:
        return False, f"Validation error: {e}"

def get_conan_profiles() -> List[str]:
    """Get list of available Conan profiles"""
    try:
        conan_cmd = get_default_conan()
        result = subprocess.run([conan_cmd, "profile", "list"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            profiles = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            return profiles
    except Exception:
        pass
    
    return []

def create_default_profile():
    """Create default Conan profile if it doesn't exist"""
    try:
        conan_cmd = get_default_conan()
        subprocess.run([conan_cmd, "profile", "detect", "--force"], 
                      capture_output=True, text=True)
        return True
    except Exception:
        return False
