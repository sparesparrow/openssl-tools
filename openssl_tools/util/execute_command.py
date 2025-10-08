#!/usr/bin/env python3
"""
OpenSSL Tools Command Execution Utilities
Based on ngapy-dev patterns for command execution
"""

import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any, Union
import threading
import queue
import signal


def execute_command(command: Union[str, List[str]], 
                   cwd: Optional[Union[str, Path]] = None,
                   continuous_print: bool = True,
                   print_out: bool = True,
                   print_command: bool = True,
                   print_err_code: bool = True,
                   timeout: Optional[int] = None,
                   env: Optional[Dict[str, str]] = None,
                   shell: bool = True,
                   capture_output: bool = False,
                   logger: Optional[logging.Logger] = None) -> Tuple[int, List[str]]:
    """
    Execute command with proper error handling and logging following ngapy-dev patterns
    
    Args:
        command: Command to execute (string or list)
        cwd: Working directory
        continuous_print: Print output continuously
        print_out: Print stdout
        print_command: Print command before execution
        print_err_code: Print stderr
        timeout: Command timeout in seconds
        env: Environment variables
        shell: Use shell execution
        capture_output: Capture output instead of printing
        logger: Logger instance
    
    Returns:
        Tuple of (return_code, output_lines)
    """
    if logger is None:
        logger = logging.getLogger('openssl_tools.execute_command')
    
    # Prepare command
    if isinstance(command, list):
        cmd_str = ' '.join(str(arg) for arg in command)
    else:
        cmd_str = str(command)
    
    # Log command execution
    if print_command:
        logger.info(f"Executing command: {cmd_str}")
        if cwd:
            logger.debug(f"Working directory: {cwd}")
    
    # Prepare environment
    if env is None:
        env = os.environ.copy()
    else:
        env = {**os.environ, **env}
    
    # Prepare working directory
    if cwd:
        cwd = Path(cwd).resolve()
        if not cwd.exists():
            logger.error(f"Working directory does not exist: {cwd}")
            return 1, [f"Working directory does not exist: {cwd}"]
    
    try:
        # Execute command
        if capture_output:
            result = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            output_lines = result.stdout.splitlines() if result.stdout else []
            error_lines = result.stderr.splitlines() if result.stderr else []
            
            # Log results
            if print_out and output_lines:
                for line in output_lines:
                    logger.debug(f"STDOUT: {line}")
            
            if print_err_code and error_lines:
                for line in error_lines:
                    logger.warning(f"STDERR: {line}")
            
            # Combine output and error
            all_output = output_lines + error_lines
            
            return result.returncode, all_output
            
        else:
            # Real-time output
            if continuous_print and print_out:
                return _execute_with_realtime_output(
                    command, cwd, env, shell, timeout, logger
                )
            else:
                result = subprocess.run(
                    command,
                    cwd=cwd,
                    env=env,
                    shell=shell,
                    timeout=timeout
                )
                return result.returncode, []
                
    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timed out after {timeout} seconds: {cmd_str}")
        return 124, [f"Command timed out after {timeout} seconds"]
    
    except FileNotFoundError as e:
        logger.error(f"Command not found: {e}")
        return 127, [f"Command not found: {e}"]
    
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        return 1, [f"Command execution failed: {e}"]


def _execute_with_realtime_output(command: Union[str, List[str]], 
                                 cwd: Optional[Path],
                                 env: Dict[str, str],
                                 shell: bool,
                                 timeout: Optional[int],
                                 logger: logging.Logger) -> Tuple[int, List[str]]:
    """Execute command with real-time output"""
    output_lines = []
    
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Read output line by line
        for line in iter(process.stdout.readline, ''):
            line = line.rstrip()
            if line:
                output_lines.append(line)
                logger.debug(f"OUTPUT: {line}")
        
        # Wait for process to complete
        return_code = process.wait(timeout=timeout)
        
        return return_code, output_lines
        
    except subprocess.TimeoutExpired:
        process.kill()
        logger.error("Command timed out and was killed")
        return 124, output_lines + ["Command timed out and was killed"]


def execute_command_async(command: Union[str, List[str]], 
                         cwd: Optional[Union[str, Path]] = None,
                         env: Optional[Dict[str, str]] = None,
                         shell: bool = True,
                         logger: Optional[logging.Logger] = None) -> subprocess.Popen:
    """
    Execute command asynchronously
    
    Returns:
        Popen process object
    """
    if logger is None:
        logger = logging.getLogger('openssl_tools.execute_command')
    
    # Prepare command
    if isinstance(command, list):
        cmd_str = ' '.join(str(arg) for arg in command)
    else:
        cmd_str = str(command)
    
    logger.info(f"Executing async command: {cmd_str}")
    
    # Prepare environment
    if env is None:
        env = os.environ.copy()
    else:
        env = {**os.environ, **env}
    
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return process
        
    except Exception as e:
        logger.error(f"Failed to start async command: {e}")
        raise


def execute_command_with_output_queue(command: Union[str, List[str]], 
                                    cwd: Optional[Union[str, Path]] = None,
                                    env: Optional[Dict[str, str]] = None,
                                    shell: bool = True,
                                    logger: Optional[logging.Logger] = None) -> Tuple[subprocess.Popen, queue.Queue]:
    """
    Execute command with output queue for real-time processing
    
    Returns:
        Tuple of (process, output_queue)
    """
    if logger is None:
        logger = logging.getLogger('openssl_tools.execute_command')
    
    output_queue = queue.Queue()
    
    def _output_reader(pipe, queue):
        """Read output from pipe and put in queue"""
        try:
            for line in iter(pipe.readline, ''):
                queue.put(('stdout', line.rstrip()))
            pipe.close()
        except Exception as e:
            queue.put(('error', str(e)))
    
    def _error_reader(pipe, queue):
        """Read error from pipe and put in queue"""
        try:
            for line in iter(pipe.readline, ''):
                queue.put(('stderr', line.rstrip()))
            pipe.close()
        except Exception as e:
            queue.put(('error', str(e)))
    
    # Prepare command
    if isinstance(command, list):
        cmd_str = ' '.join(str(arg) for arg in command)
    else:
        cmd_str = str(command)
    
    logger.info(f"Executing command with output queue: {cmd_str}")
    
    # Prepare environment
    if env is None:
        env = os.environ.copy()
    else:
        env = {**os.environ, **env}
    
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Start output readers
        stdout_thread = threading.Thread(target=_output_reader, args=(process.stdout, output_queue))
        stderr_thread = threading.Thread(target=_error_reader, args=(process.stderr, output_queue))
        
        stdout_thread.daemon = True
        stderr_thread.daemon = True
        
        stdout_thread.start()
        stderr_thread.start()
        
        return process, output_queue
        
    except Exception as e:
        logger.error(f"Failed to start command with output queue: {e}")
        raise


def execute_command_with_retry(command: Union[str, List[str]], 
                              max_retries: int = 3,
                              retry_delay: float = 1.0,
                              cwd: Optional[Union[str, Path]] = None,
                              env: Optional[Dict[str, str]] = None,
                              shell: bool = True,
                              logger: Optional[logging.Logger] = None) -> Tuple[int, List[str]]:
    """
    Execute command with retry logic
    
    Args:
        command: Command to execute
        max_retries: Maximum number of retries
        retry_delay: Delay between retries in seconds
        cwd: Working directory
        env: Environment variables
        shell: Use shell execution
        logger: Logger instance
    
    Returns:
        Tuple of (return_code, output_lines)
    """
    if logger is None:
        logger = logging.getLogger('openssl_tools.execute_command')
    
    last_result = None
    
    for attempt in range(max_retries + 1):
        if attempt > 0:
            logger.info(f"Retry attempt {attempt}/{max_retries} for command")
            time.sleep(retry_delay)
        
        try:
            result = execute_command(
                command, cwd=cwd, env=env, shell=shell,
                continuous_print=False, capture_output=True,
                logger=logger
            )
            
            if result[0] == 0:
                logger.info(f"Command succeeded on attempt {attempt + 1}")
                return result
            
            last_result = result
            logger.warning(f"Command failed on attempt {attempt + 1} with return code {result[0]}")
            
        except Exception as e:
            last_result = (1, [str(e)])
            logger.warning(f"Command failed on attempt {attempt + 1} with exception: {e}")
    
    logger.error(f"Command failed after {max_retries + 1} attempts")
    return last_result


def execute_command_with_timeout(command: Union[str, List[str]], 
                                timeout: int,
                                cwd: Optional[Union[str, Path]] = None,
                                env: Optional[Dict[str, str]] = None,
                                shell: bool = True,
                                logger: Optional[logging.Logger] = None) -> Tuple[int, List[str]]:
    """
    Execute command with timeout
    
    Args:
        command: Command to execute
        timeout: Timeout in seconds
        cwd: Working directory
        env: Environment variables
        shell: Use shell execution
        logger: Logger instance
    
    Returns:
        Tuple of (return_code, output_lines)
    """
    if logger is None:
        logger = logging.getLogger('openssl_tools.execute_command')
    
    logger.info(f"Executing command with {timeout}s timeout")
    
    return execute_command(
        command, cwd=cwd, env=env, shell=shell,
        timeout=timeout, capture_output=True,
        logger=logger
    )


def execute_command_safe(command: Union[str, List[str]], 
                        cwd: Optional[Union[str, Path]] = None,
                        env: Optional[Dict[str, str]] = None,
                        shell: bool = True,
                        logger: Optional[logging.Logger] = None) -> Tuple[bool, List[str]]:
    """
    Execute command safely, returning success status and output
    
    Returns:
        Tuple of (success, output_lines)
    """
    try:
        return_code, output = execute_command(
            command, cwd=cwd, env=env, shell=shell,
            capture_output=True, logger=logger
        )
        return return_code == 0, output
    except Exception as e:
        if logger:
            logger.error(f"Safe command execution failed: {e}")
        return False, [str(e)]


def execute_command_with_validation(command: Union[str, List[str]], 
                                  expected_return_code: int = 0,
                                  expected_output_patterns: Optional[List[str]] = None,
                                  cwd: Optional[Union[str, Path]] = None,
                                  env: Optional[Dict[str, str]] = None,
                                  shell: bool = True,
                                  logger: Optional[logging.Logger] = None) -> Tuple[bool, List[str]]:
    """
    Execute command with validation
    
    Args:
        command: Command to execute
        expected_return_code: Expected return code
        expected_output_patterns: List of patterns that should appear in output
        cwd: Working directory
        env: Environment variables
        shell: Use shell execution
        logger: Logger instance
    
    Returns:
        Tuple of (validation_passed, output_lines)
    """
    if logger is None:
        logger = logging.getLogger('openssl_tools.execute_command')
    
    return_code, output = execute_command(
        command, cwd=cwd, env=env, shell=shell,
        capture_output=True, logger=logger
    )
    
    # Check return code
    if return_code != expected_return_code:
        logger.error(f"Command returned {return_code}, expected {expected_return_code}")
        return False, output
    
    # Check output patterns
    if expected_output_patterns:
        output_text = '\n'.join(output)
        for pattern in expected_output_patterns:
            if pattern not in output_text:
                logger.error(f"Expected pattern not found in output: {pattern}")
                return False, output
    
    logger.info("Command validation passed")
    return True, output


def kill_process_tree(process: subprocess.Popen, logger: Optional[logging.Logger] = None) -> None:
    """Kill process and its children"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.execute_command')
    
    try:
        # Try graceful termination first
        process.terminate()
        
        # Wait a bit for graceful shutdown
        try:
            process.wait(timeout=5)
            logger.info("Process terminated gracefully")
            return
        except subprocess.TimeoutExpired:
            pass
        
        # Force kill if needed
        process.kill()
        process.wait()
        logger.info("Process killed forcefully")
        
    except Exception as e:
        logger.warning(f"Failed to kill process: {e}")


def get_command_output(command: Union[str, List[str]], 
                      cwd: Optional[Union[str, Path]] = None,
                      env: Optional[Dict[str, str]] = None,
                      shell: bool = True,
                      logger: Optional[logging.Logger] = None) -> str:
    """
    Get command output as string
    
    Returns:
        Command output as string
    """
    success, output = execute_command_safe(command, cwd, env, shell, logger)
    return '\n'.join(output) if success else ""


def check_command_exists(command: str, logger: Optional[logging.Logger] = None) -> bool:
    """Check if command exists in PATH"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.execute_command')
    
    try:
        result = subprocess.run(
            ['which', command] if os.name != 'nt' else ['where', command],
            capture_output=True,
            text=True
        )
        exists = result.returncode == 0
        logger.debug(f"Command '{command}' exists: {exists}")
        return exists
    except Exception as e:
        logger.debug(f"Failed to check command existence: {e}")
        return False


def get_command_version(command: str, version_flag: str = '--version',
                       logger: Optional[logging.Logger] = None) -> Optional[str]:
    """Get command version"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.execute_command')
    
    try:
        success, output = execute_command_safe([command, version_flag], logger=logger)
        if success and output:
            return output[0]
    except Exception as e:
        logger.debug(f"Failed to get version for {command}: {e}")
    
    return None