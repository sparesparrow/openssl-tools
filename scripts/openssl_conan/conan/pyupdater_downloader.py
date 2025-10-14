#!/usr/bin/env python3
"""
OpenSSL PyUpdater Downloader
Adapted from ngapy PyUpdater downloader for OpenSSL project
"""

import os
import hashlib
import requests
from pathlib import Path
from typing import List, Optional


class PyUpdaterFileDownloader:
    """File downloader for PyUpdater integration"""
    
    def __init__(self, filename: str, urls: List[str], **kwargs):
        self.filename = filename
        self.urls = urls
        self.hexdigest = kwargs.get("hexdigest")
        self._data = None
        self.timeout = kwargs.get("timeout", 30)
        self.verify_ssl = kwargs.get("verify_ssl", True)
    
    def download_verify_return(self) -> bytes:
        """Download the data from the endpoint and return"""
        for url in self.urls:
            try:
                source_file = os.path.join(url, self.filename)
                if os.path.exists(source_file):
                    with open(source_file, 'rb') as f:
                        self._data = f.read()
                else:
                    # Try HTTP download
                    response = requests.get(
                        source_file, 
                        timeout=self.timeout,
                        verify=self.verify_ssl
                    )
                    response.raise_for_status()
                    self._data = response.content
                
                # Verify hash if provided
                if self.hexdigest:
                    if hashlib.sha256(self._data).hexdigest() != self.hexdigest:
                        raise ValueError(f"Hash verification failed for {self.filename}")
                
                return self._data
                
            except Exception as e:
                print(f"Failed to download from {source_file}: {e}")
                continue
        
        raise RuntimeError(f"Failed to download {self.filename} from all sources")
    
    def download_verify_write(self, target_dir: Optional[Path] = None) -> bool:
        """Write the downloaded data to the target directory"""
        if target_dir is None:
            target_dir = Path.cwd()
        
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        
        target_file = target_dir / self.filename
        
        try:
            data = self.download_verify_return()
            with open(target_file, 'wb') as f:
                f.write(data)
            return True
        except Exception as e:
            print(f"Failed to write {target_file}: {e}")
            return False


class OpenSSLPyUpdaterDownloader:
    """OpenSSL specific PyUpdater downloader"""
    
    def __init__(self, base_urls: List[str] = None):
        self.base_urls = base_urls or [
            "https://github.com/openssl/openssl/releases/download",
            "https://conan.io/center/openssl",
        ]
    
    def download_openssl_source(self, version: str, target_dir: Path) -> bool:
        """Download OpenSSL source code"""
        filename = f"openssl-{version}.tar.gz"
        urls = [os.path.join(url, f"openssl-{version}") for url in self.base_urls]
        
        downloader = PyUpdaterFileDownloader(filename, urls)
        return downloader.download_verify_write(target_dir)
    
    def download_conan_package(self, package_name: str, version: str, target_dir: Path) -> bool:
        """Download Conan package"""
        filename = f"{package_name}-{version}.tar.gz"
        urls = [os.path.join(url, package_name) for url in self.base_urls]
        
        downloader = PyUpdaterFileDownloader(filename, urls)
        return downloader.download_verify_write(target_dir)
    
    def download_build_tools(self, target_dir: Path) -> bool:
        """Download build tools"""
        tools = [
            "cmake",
            "ninja",
            "perl",
            "nasm",
        ]
        
        success = True
        for tool in tools:
            filename = f"{tool}.tar.gz"
            urls = [os.path.join(url, "tools") for url in self.base_urls]
            
            downloader = PyUpdaterFileDownloader(filename, urls)
            if not downloader.download_verify_write(target_dir):
                print(f"Warning: Failed to download {tool}")
                success = False
        
        return success


def download_file_from_urls(filename: str, urls: List[str], target_dir: Path = None) -> bool:
    """Download a file from multiple URLs"""
    if target_dir is None:
        target_dir = Path.cwd()
    
    downloader = PyUpdaterFileDownloader(filename, urls)
    return downloader.download_verify_write(target_dir)


def download_openssl_release(version: str, target_dir: Path = None) -> bool:
    """Download OpenSSL release"""
    if target_dir is None:
        target_dir = Path.cwd()
    
    downloader = OpenSSLPyUpdaterDownloader()
    return downloader.download_openssl_source(version, target_dir)


def download_conan_package(package_name: str, version: str, target_dir: Path = None) -> bool:
    """Download Conan package"""
    if target_dir is None:
        target_dir = Path.cwd()
    
    downloader = OpenSSLPyUpdaterDownloader()
    return downloader.download_conan_package(package_name, version, target_dir)


def main():
    """Main entry point for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenSSL PyUpdater Downloader')
    parser.add_argument('--version', help='OpenSSL version to download')
    parser.add_argument('--package', help='Package name to download')
    parser.add_argument('--target', help='Target directory', default='.')
    
    args = parser.parse_args()
    
    target_dir = Path(args.target)
    target_dir.mkdir(parents=True, exist_ok=True)
    
    if args.version:
        success = download_openssl_release(args.version, target_dir)
        if success:
            print(f"Successfully downloaded OpenSSL {args.version}")
        else:
            print(f"Failed to download OpenSSL {args.version}")
    
    if args.package:
        success = download_conan_package(args.package, "latest", target_dir)
        if success:
            print(f"Successfully downloaded {args.package}")
        else:
            print(f"Failed to download {args.package}")


if __name__ == '__main__':
    main()