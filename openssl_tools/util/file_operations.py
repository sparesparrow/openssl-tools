#!/usr/bin/env python3
"""
OpenSSL Tools File Operations Utilities
Based on ngapy-dev patterns for file operations
"""

import hashlib
import logging
import os
import shutil
import stat
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Tuple
import json
import yaml
import zipfile
import tarfile


def ensure_target_exists(target: Union[str, Path]) -> None:
    """Ensure target directory exists following ngapy-dev patterns"""
    target_path = Path(target)
    target_path.parent.mkdir(parents=True, exist_ok=True)


def get_file_metadata(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Get file metadata including MD5 hash following ngapy-dev patterns"""
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Get file stats
    stat_info = filepath.stat()
    
    # Calculate MD5 hash
    md5_hash = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    
    # Calculate SHA256 hash
    sha256_hash = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    
    return {
        'MD5': md5_hash.hexdigest(),
        'SHA256': sha256_hash.hexdigest(),
        'size': stat_info.st_size,
        'mtime': stat_info.st_mtime,
        'ctime': stat_info.st_ctime,
        'mode': stat_info.st_mode,
        'uid': stat_info.st_uid,
        'gid': stat_info.st_gid
    }


def find_first_existing_file(paths: List[Union[str, Path]], filename: str) -> Optional[Path]:
    """Find first existing file in list of paths following ngapy-dev patterns"""
    for path in paths:
        path_obj = Path(path)
        if path_obj.is_dir():
            file_path = path_obj / filename
            if file_path.exists():
                return file_path
        elif path_obj.name == filename and path_obj.exists():
            return path_obj
    return None


def find_executable_in_path(executable_name: str, 
                           additional_paths: Optional[List[Union[str, Path]]] = None) -> Optional[Path]:
    """Find executable in PATH and additional paths following ngapy-dev patterns"""
    # Check system PATH
    import shutil
    system_path = shutil.which(executable_name)
    if system_path:
        return Path(system_path)
    
    # Check additional paths
    if additional_paths:
        for path in additional_paths:
            path_obj = Path(path)
            if path_obj.is_dir():
                exec_path = path_obj / executable_name
                if exec_path.exists() and os.access(exec_path, os.X_OK):
                    return exec_path
            elif path_obj.name == executable_name and path_obj.exists() and os.access(path_obj, os.X_OK):
                return path_obj
    
    return None


def symlink_with_check(source: Union[str, Path], target: Union[str, Path], 
                      is_directory: bool = False, logger: Optional[logging.Logger] = None) -> None:
    """Create symlink with proper error handling following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.file_operations')
    
    source_path = Path(source)
    target_path = Path(target)
    
    # Ensure source exists
    if not source_path.exists():
        raise FileNotFoundError(f"Source does not exist: {source_path}")
    
    # Remove existing target
    if target_path.exists():
        if target_path.is_symlink():
            target_path.unlink()
            logger.debug(f"Removed existing symlink: {target_path}")
        elif target_path.is_dir():
            shutil.rmtree(target_path)
            logger.debug(f"Removed existing directory: {target_path}")
        else:
            target_path.unlink()
            logger.debug(f"Removed existing file: {target_path}")
    
    # Create symlink
    try:
        if is_directory:
            target_path.symlink_to(source_path, target_is_directory=True)
        else:
            target_path.symlink_to(source_path)
        logger.debug(f"Created symlink: {source_path} -> {target_path}")
    except Exception as e:
        logger.error(f"Failed to create symlink {source_path} -> {target_path}: {e}")
        raise


def copy_with_metadata(source: Union[str, Path], target: Union[str, Path], 
                      preserve_metadata: bool = True,
                      logger: Optional[logging.Logger] = None) -> None:
    """Copy file with metadata preservation following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.file_operations')
    
    source_path = Path(source)
    target_path = Path(target)
    
    if not source_path.exists():
        raise FileNotFoundError(f"Source does not exist: {source_path}")
    
    # Ensure target directory exists
    ensure_target_exists(target_path)
    
    # Copy file
    shutil.copy2(source_path, target_path)
    logger.debug(f"Copied file: {source_path} -> {target_path}")
    
    # Preserve additional metadata if requested
    if preserve_metadata:
        try:
            stat_info = source_path.stat()
            os.chmod(target_path, stat_info.st_mode)
            logger.debug(f"Preserved metadata for: {target_path}")
        except Exception as e:
            logger.warning(f"Failed to preserve metadata for {target_path}: {e}")


def remove_directory_tree(path: Union[str, Path], 
                        ignore_errors: bool = True,
                        logger: Optional[logging.Logger] = None) -> None:
    """Remove directory tree with error handling following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.file_operations')
    
    path_obj = Path(path)
    
    if not path_obj.exists():
        logger.debug(f"Path does not exist, skipping removal: {path_obj}")
        return
    
    try:
        shutil.rmtree(path_obj, ignore_errors=ignore_errors)
        logger.info(f"Removed directory tree: {path_obj}")
    except Exception as e:
        if ignore_errors:
            logger.warning(f"Failed to remove directory tree {path_obj}: {e}")
        else:
            logger.error(f"Failed to remove directory tree {path_obj}: {e}")
            raise


def create_backup(filepath: Union[str, Path], 
                 backup_suffix: str = '.bak',
                 logger: Optional[logging.Logger] = None) -> Optional[Path]:
    """Create backup of file following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.file_operations')
    
    filepath = Path(filepath)
    
    if not filepath.exists():
        logger.warning(f"File does not exist for backup: {filepath}")
        return None
    
    backup_path = filepath.with_suffix(filepath.suffix + backup_suffix)
    
    try:
        shutil.copy2(filepath, backup_path)
        logger.info(f"Created backup: {filepath} -> {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Failed to create backup {backup_path}: {e}")
        raise


def restore_backup(filepath: Union[str, Path], 
                  backup_suffix: str = '.bak',
                  logger: Optional[logging.Logger] = None) -> bool:
    """Restore file from backup following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.file_operations')
    
    filepath = Path(filepath)
    backup_path = filepath.with_suffix(filepath.suffix + backup_suffix)
    
    if not backup_path.exists():
        logger.warning(f"Backup does not exist: {backup_path}")
        return False
    
    try:
        shutil.copy2(backup_path, filepath)
        logger.info(f"Restored from backup: {backup_path} -> {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to restore from backup {backup_path}: {e}")
        return False


def find_files_by_pattern(directory: Union[str, Path], 
                         pattern: str,
                         recursive: bool = True,
                         logger: Optional[logging.Logger] = None) -> List[Path]:
    """Find files by pattern following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.file_operations')
    
    directory = Path(directory)
    
    if not directory.exists():
        logger.warning(f"Directory does not exist: {directory}")
        return []
    
    try:
        if recursive:
            files = list(directory.rglob(pattern))
        else:
            files = list(directory.glob(pattern))
        
        logger.debug(f"Found {len(files)} files matching pattern '{pattern}' in {directory}")
        return files
    except Exception as e:
        logger.error(f"Failed to find files by pattern '{pattern}' in {directory}: {e}")
        return []


def get_directory_size(directory: Union[str, Path], 
                      logger: Optional[logging.Logger] = None) -> int:
    """Get directory size in bytes following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.file_operations')
    
    directory = Path(directory)
    total_size = 0
    
    try:
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        logger.debug(f"Directory size: {total_size} bytes ({total_size / 1024 / 1024:.2f} MB)")
        return total_size
    except Exception as e:
        logger.error(f"Failed to calculate directory size for {directory}: {e}")
        return 0


def create_temporary_directory(prefix: str = 'openssl_tools_',
                             suffix: str = '',
                             logger: Optional[logging.Logger] = None) -> Path:
    """Create temporary directory following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.file_operations')
    
    try:
        temp_dir = Path(tempfile.mkdtemp(prefix=prefix, suffix=suffix))
        logger.debug(f"Created temporary directory: {temp_dir}")
        return temp_dir
    except Exception as e:
        logger.error(f"Failed to create temporary directory: {e}")
        raise


def create_temporary_file(prefix: str = 'openssl_tools_',
                         suffix: str = '.tmp',
                         content: Optional[str] = None,
                         logger: Optional[logging.Logger] = None) -> Path:
    """Create temporary file following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.file_operations')
    
    try:
        with tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix, delete=False) as f:
            temp_file = Path(f.name)
            if content:
                f.write(content.encode('utf-8'))
            logger.debug(f"Created temporary file: {temp_file}")
            return temp_file
    except Exception as e:
        logger.error(f"Failed to create temporary file: {e}")
        raise


def read_json_file(filepath: Union[str, Path], 
                  logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """Read JSON file following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.file_operations')
    
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"JSON file not found: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.debug(f"Read JSON file: {filepath}")
        return data
    except Exception as e:
        logger.error(f"Failed to read JSON file {filepath}: {e}")
        raise


def write_json_file(data: Dict[str, Any], filepath: Union[str, Path],
                   indent: int = 2,
                   logger: Optional[logging.Logger] = None) -> None:
    """Write JSON file following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.file_operations')
    
    filepath = Path(filepath)
    ensure_target_exists(filepath)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        logger.debug(f"Wrote JSON file: {filepath}")
    except Exception as e:
        logger.error(f"Failed to write JSON file {filepath}: {e}")
        raise


def read_yaml_file(filepath: Union[str, Path], 
                  logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """Read YAML file following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.file_operations')
    
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"YAML file not found: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        logger.debug(f"Read YAML file: {filepath}")
        return data or {}
    except Exception as e:
        logger.error(f"Failed to read YAML file {filepath}: {e}")
        raise


def write_yaml_file(data: Dict[str, Any], filepath: Union[str, Path],
                   default_flow_style: bool = False,
                   logger: Optional[logging.Logger] = None) -> None:
    """Write YAML file following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.file_operations')
    
    filepath = Path(filepath)
    ensure_target_exists(filepath)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=default_flow_style, 
                     allow_unicode=True, sort_keys=False)
        logger.debug(f"Wrote YAML file: {filepath}")
    except Exception as e:
        logger.error(f"Failed to write YAML file {filepath}: {e}")
        raise


def create_archive(source_dir: Union[str, Path], 
                  archive_path: Union[str, Path],
                  archive_format: str = 'zip',
                  logger: Optional[logging.Logger] = None) -> None:
    """Create archive following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.file_operations')
    
    source_dir = Path(source_dir)
    archive_path = Path(archive_path)
    
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")
    
    ensure_target_exists(archive_path)
    
    try:
        if archive_format == 'zip':
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in source_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(source_dir)
                        zipf.write(file_path, arcname)
        elif archive_format == 'tar':
            with tarfile.open(archive_path, 'w') as tarf:
                tarf.add(source_dir, arcname=source_dir.name)
        else:
            raise ValueError(f"Unsupported archive format: {archive_format}")
        
        logger.info(f"Created {archive_format} archive: {archive_path}")
    except Exception as e:
        logger.error(f"Failed to create archive {archive_path}: {e}")
        raise


def extract_archive(archive_path: Union[str, Path], 
                   extract_dir: Union[str, Path],
                   logger: Optional[logging.Logger] = None) -> None:
    """Extract archive following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.file_operations')
    
    archive_path = Path(archive_path)
    extract_dir = Path(extract_dir)
    
    if not archive_path.exists():
        raise FileNotFoundError(f"Archive not found: {archive_path}")
    
    ensure_target_exists(extract_dir)
    
    try:
        if archive_path.suffix == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                zipf.extractall(extract_dir)
        elif archive_path.suffix in ['.tar', '.tar.gz', '.tgz']:
            with tarfile.open(archive_path, 'r') as tarf:
                tarf.extractall(extract_dir)
        else:
            raise ValueError(f"Unsupported archive format: {archive_path.suffix}")
        
        logger.info(f"Extracted archive: {archive_path} -> {extract_dir}")
    except Exception as e:
        logger.error(f"Failed to extract archive {archive_path}: {e}")
        raise


def compare_files(file1: Union[str, Path], file2: Union[str, Path],
                 logger: Optional[logging.Logger] = None) -> bool:
    """Compare two files following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.file_operations')
    
    file1 = Path(file1)
    file2 = Path(file2)
    
    if not file1.exists():
        logger.warning(f"File 1 does not exist: {file1}")
        return False
    
    if not file2.exists():
        logger.warning(f"File 2 does not exist: {file2}")
        return False
    
    try:
        # Compare file sizes first
        if file1.stat().st_size != file2.stat().st_size:
            logger.debug(f"Files differ in size: {file1} vs {file2}")
            return False
        
        # Compare file contents
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            while True:
                chunk1 = f1.read(4096)
                chunk2 = f2.read(4096)
                if chunk1 != chunk2:
                    logger.debug(f"Files differ in content: {file1} vs {file2}")
                    return False
                if not chunk1:  # End of file
                    break
        
        logger.debug(f"Files are identical: {file1} vs {file2}")
        return True
    except Exception as e:
        logger.error(f"Failed to compare files {file1} vs {file2}: {e}")
        return False


def get_file_extension(filepath: Union[str, Path]) -> str:
    """Get file extension following ngapy-dev patterns"""
    return Path(filepath).suffix.lower()


def is_binary_file(filepath: Union[str, Path]) -> bool:
    """Check if file is binary following ngapy-dev patterns"""
    filepath = Path(filepath)
    
    if not filepath.exists():
        return False
    
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            return b'\0' in chunk
    except Exception:
        return False


def get_file_line_count(filepath: Union[str, Path],
                       logger: Optional[logging.Logger] = None) -> int:
    """Get file line count following ngapy-dev patterns"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.file_operations')
    
    filepath = Path(filepath)
    
    if not filepath.exists():
        logger.warning(f"File does not exist: {filepath}")
        return 0
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            line_count = sum(1 for _ in f)
        logger.debug(f"File line count: {line_count} lines in {filepath}")
        return line_count
    except Exception as e:
        logger.error(f"Failed to count lines in {filepath}: {e}")
        return 0