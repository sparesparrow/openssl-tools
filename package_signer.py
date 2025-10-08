#!/usr/bin/env python3
"""
OpenSSL Tools - Package Signer
Implements package signing with cosign for supply chain security.
"""

import subprocess
import os
import logging
import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import tempfile
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PackageSigner:
    """Handles package signing and verification using cosign."""
    
    def __init__(self, key_path: Optional[Path] = None, 
                 key_password: Optional[str] = None,
                 cosign_path: Optional[Path] = None):
        self.key_path = key_path or Path.home() / ".openssl-signing-key"
        self.key_password = key_password or os.getenv("COSIGN_PASSWORD")
        self.cosign_path = cosign_path or self._find_cosign()
        self.public_key_path = self.key_path.with_suffix('.pub')
        self.signature_dir = Path.home() / ".openssl-signatures"
        self.signature_dir.mkdir(exist_ok=True)
        
    def _find_cosign(self) -> Optional[Path]:
        """Find cosign executable."""
        cosign_path = shutil.which("cosign")
        if cosign_path:
            return Path(cosign_path)
            
        # Try common locations
        common_paths = [
            Path("/usr/local/bin/cosign"),
            Path("/usr/bin/cosign"),
            Path.home() / "bin/cosign"
        ]
        
        for path in common_paths:
            if path.exists() and path.is_file():
                return path
                
        return None
        
    def generate_keypair(self, force: bool = False) -> bool:
        """
        Generate a new signing keypair.
        
        Args:
            force: If True, overwrite existing keys
            
        Returns:
            bool: True if keypair was generated successfully
        """
        if self.key_path.exists() and not force:
            logger.info("Signing key already exists. Use --force to regenerate.")
            return True
            
        if not self.cosign_path:
            logger.error("cosign not found. Please install cosign first.")
            return False
            
        try:
            # Generate new keypair
            logger.info("Generating new signing keypair...")
            
            cmd = [
                str(self.cosign_path), "generate-key-pair",
                "--output-key-prefix", str(self.key_path.with_suffix(''))
            ]
            
            # Set password if provided
            if self.key_password:
                env = os.environ.copy()
                env["COSIGN_PASSWORD"] = self.key_password
                subprocess.run(cmd, check=True, env=env)
            else:
                subprocess.run(cmd, check=True)
                
            logger.info(f"Generated keypair: {self.key_path}")
            logger.info(f"Public key: {self.public_key_path}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate keypair: {e}")
            return False
            
    def sign_package(self, package_path: Path, 
                    signature_path: Optional[Path] = None,
                    metadata: Optional[Dict] = None) -> bool:
        """
        Sign a package for supply chain security.
        
        Args:
            package_path: Path to the package to sign
            signature_path: Path to save the signature (optional)
            metadata: Additional metadata to include in signature
            
        Returns:
            bool: True if signing was successful
        """
        if not self.key_path.exists():
            logger.error("Signing key not found. Generate a keypair first.")
            return False
            
        if not self.cosign_path:
            logger.error("cosign not found. Please install cosign first.")
            return False
            
        if not package_path.exists():
            logger.error(f"Package not found: {package_path}")
            return False
            
        try:
            # Generate signature path if not provided
            if signature_path is None:
                signature_path = self.signature_dir / f"{package_path.name}.sig"
                
            logger.info(f"Signing package: {package_path}")
            
            # Prepare cosign command
            cmd = [
                str(self.cosign_path), "sign-blob",
                "--key", str(self.key_path),
                "--output-signature", str(signature_path),
                str(package_path)
            ]
            
            # Add metadata if provided
            if metadata:
                metadata_file = self._create_metadata_file(metadata)
                cmd.extend(["--bundle", str(metadata_file)])
                
            # Set password if provided
            env = os.environ.copy()
            if self.key_password:
                env["COSIGN_PASSWORD"] = self.key_password
                
            subprocess.run(cmd, check=True, env=env)
            
            # Create signature manifest
            self._create_signature_manifest(package_path, signature_path, metadata)
            
            logger.info(f"Package signed successfully: {signature_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to sign package: {e}")
            return False
            
    def verify_signature(self, package_path: Path, 
                        signature_path: Path) -> bool:
        """
        Verify a package signature.
        
        Args:
            package_path: Path to the package
            signature_path: Path to the signature file
            
        Returns:
            bool: True if signature is valid
        """
        if not self.public_key_path.exists():
            logger.error("Public key not found.")
            return False
            
        if not self.cosign_path:
            logger.error("cosign not found. Please install cosign first.")
            return False
            
        try:
            logger.info(f"Verifying signature for: {package_path}")
            
            cmd = [
                str(self.cosign_path), "verify-blob",
                "--key", str(self.public_key_path),
                "--signature", str(signature_path),
                str(package_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Signature verification successful")
                return True
            else:
                logger.error(f"Signature verification failed: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to verify signature: {e}")
            return False
            
    def sign_directory(self, directory_path: Path,
                      recursive: bool = True,
                      file_patterns: List[str] = None) -> Dict[str, bool]:
        """
        Sign all files in a directory.
        
        Args:
            directory_path: Path to the directory
            recursive: If True, sign files recursively
            file_patterns: List of file patterns to include (e.g., ['*.tar.gz', '*.zip'])
            
        Returns:
            Dict mapping file paths to signing success status
        """
        if not directory_path.exists() or not directory_path.is_dir():
            logger.error(f"Directory not found: {directory_path}")
            return {}
            
        results = {}
        
        # Default file patterns
        if file_patterns is None:
            file_patterns = ['*.tar.gz', '*.zip', '*.deb', '*.rpm', '*.exe', '*.dmg']
            
        # Find files to sign
        files_to_sign = []
        for pattern in file_patterns:
            if recursive:
                files_to_sign.extend(directory_path.rglob(pattern))
            else:
                files_to_sign.extend(directory_path.glob(pattern))
                
        logger.info(f"Found {len(files_to_sign)} files to sign")
        
        for file_path in files_to_sign:
            if file_path.is_file():
                success = self.sign_package(file_path)
                results[str(file_path)] = success
                
        return results
        
    def create_signed_manifest(self, package_dir: Path,
                             manifest_path: Optional[Path] = None) -> bool:
        """
        Create a manifest of all signed packages in a directory.
        
        Args:
            package_dir: Directory containing packages
            manifest_path: Path to save the manifest (optional)
            
        Returns:
            bool: True if manifest was created successfully
        """
        if manifest_path is None:
            manifest_path = package_dir / "signature_manifest.json"
            
        try:
            manifest = {
                "created_at": datetime.now().isoformat(),
                "packages": [],
                "signer": {
                    "public_key": str(self.public_key_path),
                    "key_fingerprint": self._get_key_fingerprint()
                }
            }
            
            # Find all signature files
            signature_files = list(self.signature_dir.glob("*.sig"))
            
            for sig_file in signature_files:
                # Find corresponding package
                package_name = sig_file.stem
                package_path = package_dir / package_name
                
                if package_path.exists():
                    package_info = {
                        "package": str(package_path),
                        "signature": str(sig_file),
                        "size": package_path.stat().st_size,
                        "modified": datetime.fromtimestamp(package_path.stat().st_mtime).isoformat(),
                        "hash": self._calculate_file_hash(package_path)
                    }
                    manifest["packages"].append(package_info)
                    
            # Save manifest
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
                
            logger.info(f"Created signature manifest: {manifest_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create manifest: {e}")
            return False
            
    def verify_manifest(self, manifest_path: Path) -> Dict[str, bool]:
        """
        Verify all signatures in a manifest.
        
        Args:
            manifest_path: Path to the signature manifest
            
        Returns:
            Dict mapping package paths to verification results
        """
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
                
            results = {}
            
            for package_info in manifest.get("packages", []):
                package_path = Path(package_info["package"])
                signature_path = Path(package_info["signature"])
                
                if package_path.exists() and signature_path.exists():
                    success = self.verify_signature(package_path, signature_path)
                    results[str(package_path)] = success
                else:
                    results[str(package_path)] = False
                    logger.warning(f"Package or signature not found: {package_path}")
                    
            return results
            
        except Exception as e:
            logger.error(f"Failed to verify manifest: {e}")
            return {}
            
    def _create_metadata_file(self, metadata: Dict) -> Path:
        """Create a temporary metadata file for cosign."""
        metadata_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(metadata, metadata_file)
        metadata_file.close()
        return Path(metadata_file.name)
        
    def _create_signature_manifest(self, package_path: Path, 
                                 signature_path: Path,
                                 metadata: Optional[Dict] = None):
        """Create a signature manifest entry."""
        manifest_entry = {
            "package": str(package_path),
            "signature": str(signature_path),
            "signed_at": datetime.now().isoformat(),
            "size": package_path.stat().st_size,
            "hash": self._calculate_file_hash(package_path)
        }
        
        if metadata:
            manifest_entry["metadata"] = metadata
            
        # Save individual manifest entry
        manifest_file = signature_path.with_suffix('.manifest.json')
        with open(manifest_file, 'w') as f:
            json.dump(manifest_entry, f, indent=2)
            
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
        
    def _get_key_fingerprint(self) -> str:
        """Get the fingerprint of the public key."""
        if not self.public_key_path.exists():
            return "unknown"
            
        try:
            # Read public key and calculate fingerprint
            key_content = self.public_key_path.read_text()
            hasher = hashlib.sha256()
            hasher.update(key_content.encode())
            return hasher.hexdigest()[:16]  # First 16 characters
        except Exception:
            return "unknown"
            
    def install_cosign(self) -> bool:
        """
        Install cosign if not available.
        
        Returns:
            bool: True if cosign was installed successfully
        """
        if self.cosign_path and self.cosign_path.exists():
            logger.info("cosign is already installed")
            return True
            
        try:
            logger.info("Installing cosign...")
            
            # Download and install cosign
            install_script = """
            set -e
            COSIGN_VERSION=2.0.0
            wget -O cosign https://github.com/sigstore/cosign/releases/download/v${COSIGN_VERSION}/cosign-linux-amd64
            chmod +x cosign
            sudo mv cosign /usr/local/bin/
            """
            
            subprocess.run(install_script, shell=True, check=True)
            
            # Update cosign path
            self.cosign_path = Path("/usr/local/bin/cosign")
            
            logger.info("cosign installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install cosign: {e}")
            return False


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenSSL Package Signer")
    parser.add_argument("--key-path", type=Path, help="Path to signing key")
    parser.add_argument("--password", help="Key password")
    parser.add_argument("--generate-key", action="store_true", help="Generate new keypair")
    parser.add_argument("--sign", type=Path, help="Sign a package")
    parser.add_argument("--verify", nargs=2, metavar=("PACKAGE", "SIGNATURE"), 
                       help="Verify package signature")
    parser.add_argument("--sign-dir", type=Path, help="Sign all packages in directory")
    parser.add_argument("--create-manifest", type=Path, help="Create signature manifest")
    parser.add_argument("--verify-manifest", type=Path, help="Verify signature manifest")
    parser.add_argument("--install-cosign", action="store_true", help="Install cosign")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing files")
    
    args = parser.parse_args()
    
    signer = PackageSigner(
        key_path=args.key_path,
        key_password=args.password
    )
    
    if args.install_cosign:
        success = signer.install_cosign()
        if not success:
            sys.exit(1)
            
    if args.generate_key:
        success = signer.generate_keypair(force=args.force)
        if not success:
            sys.exit(1)
            
    if args.sign:
        success = signer.sign_package(args.sign)
        if not success:
            sys.exit(1)
            
    if args.verify:
        package_path, signature_path = Path(args.verify[0]), Path(args.verify[1])
        success = signer.verify_signature(package_path, signature_path)
        if not success:
            sys.exit(1)
            
    if args.sign_dir:
        results = signer.sign_directory(args.sign_dir)
        failed_count = sum(1 for success in results.values() if not success)
        if failed_count > 0:
            print(f"Failed to sign {failed_count} packages")
            sys.exit(1)
            
    if args.create_manifest:
        success = signer.create_signed_manifest(args.create_manifest)
        if not success:
            sys.exit(1)
            
    if args.verify_manifest:
        results = signer.verify_manifest(args.verify_manifest)
        failed_count = sum(1 for success in results.values() if not success)
        if failed_count > 0:
            print(f"Failed to verify {failed_count} packages")
            sys.exit(1)


if __name__ == "__main__":
    import sys
    main()