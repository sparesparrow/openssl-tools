#!/usr/bin/env python3
"""
OpenSSL Tools Copy Utilities
Based on ngapy-dev patterns for file copying and metadata handling
"""

import hashlib
import logging
import os
import shutil
import stat
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Tuple
import json


def get_file_metadata(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Get comprehensive file metadata following ngapy-dev patterns"""
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Get file stats
    stat_info = filepath.stat()
    
    # Calculate hashes
    md5_hash = hashlib.md5()
    sha1_hash = hashlib.sha1()
    sha256_hash = hashlib.sha256()
    
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
            sha1_hash.update(chunk)
            sha256_hash.update(chunk)
    
    return {
        'path': str(filepath),
        'name': filepath.name,
        'stem': filepath.stem,
        'suffix': filepath.suffix,
        'size': stat_info.st_size,
        'mtime': stat_info.st_mtime,
        'ctime': stat_info.st_ctime,
        'atime': stat_info.st_atime,
        'mode': stat_info.st_mode,
        'uid': stat_info.st_uid,
        'gid': stat_info.st_gid,
        'MD5': md5_hash.hexdigest(),
        'SHA1': sha1_hash.hexdigest(),
        'SHA256': sha256_hash.hexdigest(),
        'is_file': filepath.is_file(),
        'is_dir': filepath.is_dir(),
        'is_symlink': filepath.is_symlink(),
        'is_absolute': filepath.is_absolute(),
        'parent': str(filepath.parent),
        'exists': filepath.exists()
    }


def copy_file_with_metadata(source: Union[str, Path], 
                           target: Union[str, Path],
                           preserve_metadata: bool = True,
                           create_backup: bool = False,
                           logger: Optional[logging.Logger] = None) -> bool:
    """Copy file with metadata preservation following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.copy_tools')
    
    source_path = Path(source)
    target_path = Path(target)
    
    if not source_path.exists():
        logger.error(f"Source file does not exist: {source_path}")
        return False
    
    # Create backup if requested and target exists
    if create_backup and target_path.exists():
        backup_path = target_path.with_suffix(target_path.suffix + '.bak')
        try:
            shutil.copy2(target_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")
    
    # Ensure target directory exists
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        if preserve_metadata:
            # Use copy2 to preserve metadata
            shutil.copy2(source_path, target_path)
        else:
            # Use copy for basic copy
            shutil.copy(source_path, target_path)
        
        logger.info(f"Copied file: {source_path} -> {target_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to copy file {source_path} -> {target_path}: {e}")
        return False


def copy_directory_with_metadata(source: Union[str, Path], 
                               target: Union[str, Path],
                               preserve_metadata: bool = True,
                               ignore_patterns: Optional[List[str]] = None,
                               logger: Optional[logging.Logger] = None) -> bool:
    """Copy directory with metadata preservation following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.copy_tools')
    
    source_path = Path(source)
    target_path = Path(target)
    
    if not source_path.exists():
        logger.error(f"Source directory does not exist: {source_path}")
        return False
    
    if not source_path.is_dir():
        logger.error(f"Source is not a directory: {source_path}")
        return False
    
    # Ensure target directory exists
    target_path.mkdir(parents=True, exist_ok=True)
    
    try:
        if ignore_patterns:
            # Use copytree with ignore function
            def ignore_func(dir_path, filenames):
                ignored = []
                for pattern in ignore_patterns:
                    for filename in filenames:
                        if pattern in filename:
                            ignored.append(filename)
                return ignored
            
            shutil.copytree(source_path, target_path, 
                           ignore=ignore_func, 
                           dirs_exist_ok=True)
        else:
            # Use copytree without ignore
            shutil.copytree(source_path, target_path, 
                           dirs_exist_ok=True)
        
        logger.info(f"Copied directory: {source_path} -> {target_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to copy directory {source_path} -> {target_path}: {e}")
        return False


def copy_files_by_pattern(source_dir: Union[str, Path], 
                         target_dir: Union[str, Path],
                         pattern: str,
                         preserve_metadata: bool = True,
                         logger: Optional[logging.Logger] = None) -> List[Path]:
    """Copy files matching pattern following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.copy_tools')
    
    source_dir = Path(source_dir)
    target_dir = Path(target_dir)
    
    if not source_dir.exists():
        logger.error(f"Source directory does not exist: {source_dir}")
        return []
    
    # Find matching files
    matching_files = list(source_dir.rglob(pattern))
    
    if not matching_files:
        logger.info(f"No files found matching pattern '{pattern}' in {source_dir}")
        return []
    
    # Ensure target directory exists
    target_dir.mkdir(parents=True, exist_ok=True)
    
    copied_files = []
    
    for source_file in matching_files:
        # Calculate relative path
        relative_path = source_file.relative_to(source_dir)
        target_file = target_dir / relative_path
        
        # Ensure target subdirectory exists
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        if copy_file_with_metadata(source_file, target_file, preserve_metadata, logger=logger):
            copied_files.append(target_file)
    
    logger.info(f"Copied {len(copied_files)} files matching pattern '{pattern}'")
    return copied_files


def sync_directories(source_dir: Union[str, Path], 
                   target_dir: Union[str, Path],
                   delete_extra: bool = False,
                   preserve_metadata: bool = True,
                   logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """Sync directories following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.copy_tools')
    
    source_dir = Path(source_dir)
    target_dir = Path(target_dir)
    
    if not source_dir.exists():
        logger.error(f"Source directory does not exist: {source_dir}")
        return {'success': False, 'error': 'Source directory does not exist'}
    
    # Ensure target directory exists
    target_dir.mkdir(parents=True, exist_ok=True)
    
    stats = {
        'files_copied': 0,
        'files_updated': 0,
        'files_skipped': 0,
        'files_deleted': 0,
        'directories_created': 0,
        'errors': []
    }
    
    try:
        # Walk through source directory
        for root, dirs, files in os.walk(source_dir):
            root_path = Path(root)
            relative_path = root_path.relative_to(source_dir)
            target_root = target_dir / relative_path
            
            # Create target directory if it doesn't exist
            if not target_root.exists():
                target_root.mkdir(parents=True, exist_ok=True)
                stats['directories_created'] += 1
            
            # Process files
            for file in files:
                source_file = root_path / file
                target_file = target_root / file
                
                # Check if target file exists and is newer
                if target_file.exists():
                    source_mtime = source_file.stat().st_mtime
                    target_mtime = target_file.stat().st_mtime
                    
                    if source_mtime <= target_mtime:
                        stats['files_skipped'] += 1
                        continue
                    else:
                        stats['files_updated'] += 1
                else:
                    stats['files_copied'] += 1
                
                # Copy file
                if not copy_file_with_metadata(source_file, target_file, preserve_metadata, logger=logger):
                    stats['errors'].append(f"Failed to copy {source_file}")
        
        # Delete extra files if requested
        if delete_extra:
            for root, dirs, files in os.walk(target_dir):
                root_path = Path(root)
                relative_path = root_path.relative_to(target_dir)
                source_root = source_dir / relative_path
                
                for file in files:
                    target_file = root_path / file
                    source_file = source_root / file
                    
                    if not source_file.exists():
                        try:
                            target_file.unlink()
                            stats['files_deleted'] += 1
                        except Exception as e:
                            stats['errors'].append(f"Failed to delete {target_file}: {e}")
        
        logger.info(f"Directory sync completed: {stats}")
        return {'success': True, 'stats': stats}
        
    except Exception as e:
        logger.error(f"Directory sync failed: {e}")
        return {'success': False, 'error': str(e), 'stats': stats}


def create_file_manifest(directory: Union[str, Path], 
                        manifest_path: Union[str, Path],
                        include_metadata: bool = True,
                        logger: Optional[logging.Logger] = None) -> bool:
    """Create file manifest following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.copy_tools')
    
    directory = Path(directory)
    manifest_path = Path(manifest_path)
    
    if not directory.exists():
        logger.error(f"Directory does not exist: {directory}")
        return False
    
    manifest = {
        'directory': str(directory),
        'created_at': str(Path().cwd()),
        'files': []
    }
    
    try:
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                file_info = {
                    'path': str(file_path.relative_to(directory)),
                    'size': file_path.stat().st_size
                }
                
                if include_metadata:
                    file_info.update(get_file_metadata(file_path))
                
                manifest['files'].append(file_info)
        
        # Write manifest
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Created file manifest: {manifest_path} ({len(manifest['files'])} files)")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create file manifest: {e}")
        return False


def verify_file_integrity(file_path: Union[str, Path], 
                         expected_hash: str,
                         hash_algorithm: str = 'MD5',
                         logger: Optional[logging.Logger] = None) -> bool:
    """Verify file integrity using hash following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.copy_tools')
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.error(f"File does not exist: {file_path}")
        return False
    
    try:
        # Get file metadata
        metadata = get_file_metadata(file_path)
        
        # Get actual hash
        actual_hash = metadata.get(hash_algorithm.upper())
        if not actual_hash:
            logger.error(f"Hash algorithm {hash_algorithm} not available")
            return False
        
        # Compare hashes
        if actual_hash.lower() == expected_hash.lower():
            logger.info(f"File integrity verified: {file_path}")
            return True
        else:
            logger.error(f"File integrity check failed: {file_path}")
            logger.error(f"Expected: {expected_hash}")
            logger.error(f"Actual: {actual_hash}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to verify file integrity: {e}")
        return False


def create_symlink_safely(source: Union[str, Path], 
                         target: Union[str, Path],
                         logger: Optional[logging.Logger] = None) -> bool:
    """Create symlink safely following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.copy_tools')
    
    source_path = Path(source)
    target_path = Path(target)
    
    if not source_path.exists():
        logger.error(f"Source does not exist: {source_path}")
        return False
    
    # Remove existing target
    if target_path.exists():
        try:
            if target_path.is_symlink():
                target_path.unlink()
            elif target_path.is_dir():
                shutil.rmtree(target_path)
            else:
                target_path.unlink()
            logger.debug(f"Removed existing target: {target_path}")
        except Exception as e:
            logger.error(f"Failed to remove existing target: {e}")
            return False
    
    # Ensure target directory exists
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Create symlink
        target_path.symlink_to(source_path)
        logger.info(f"Created symlink: {source_path} -> {target_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create symlink: {e}")
        return False


def copy_with_permissions(source: Union[str, Path], 
                        target: Union[str, Path],
                        permissions: Optional[int] = None,
                        logger: Optional[logging.Logger] = None) -> bool:
    """Copy file with specific permissions following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.copy_tools')
    
    source_path = Path(source)
    target_path = Path(target)
    
    if not source_path.exists():
        logger.error(f"Source file does not exist: {source_path}")
        return False
    
    # Ensure target directory exists
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Copy file
        shutil.copy2(source_path, target_path)
        
        # Set permissions
        if permissions is not None:
            os.chmod(target_path, permissions)
            logger.debug(f"Set permissions {oct(permissions)} for {target_path}")
        else:
            # Preserve source permissions
            source_permissions = source_path.stat().st_mode
            os.chmod(target_path, source_permissions)
            logger.debug(f"Preserved permissions {oct(source_permissions)} for {target_path}")
        
        logger.info(f"Copied file with permissions: {source_path} -> {target_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to copy file with permissions: {e}")
        return False


def get_directory_tree(directory: Union[str, Path], 
                      max_depth: Optional[int] = None,
                      include_files: bool = True,
                      include_dirs: bool = True,
                      logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """Get directory tree structure following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.copy_tools')
    
    directory = Path(directory)
    
    if not directory.exists():
        logger.error(f"Directory does not exist: {directory}")
        return {}
    
    def _build_tree(path: Path, current_depth: int = 0) -> Dict[str, Any]:
        tree = {
            'name': path.name,
            'path': str(path),
            'is_dir': path.is_dir(),
            'is_file': path.is_file(),
            'size': path.stat().st_size if path.is_file() else 0,
            'children': []
        }
        
        if path.is_dir() and (max_depth is None or current_depth < max_depth):
            try:
                for child in sorted(path.iterdir()):
                    if (include_files and child.is_file()) or (include_dirs and child.is_dir()):
                        tree['children'].append(_build_tree(child, current_depth + 1))
            except PermissionError:
                logger.warning(f"Permission denied accessing {path}")
        
        return tree
    
    try:
        tree = _build_tree(directory)
        logger.debug(f"Built directory tree for {directory}")
        return tree
    except Exception as e:
        logger.error(f"Failed to build directory tree: {e}")
        return {}


def ensure_target_exists(target: Union[str, Path]) -> None:
    """Ensure target directory exists following ngapy-dev patterns"""
    target_path = Path(target)
    target_path.parent.mkdir(parents=True, exist_ok=True)