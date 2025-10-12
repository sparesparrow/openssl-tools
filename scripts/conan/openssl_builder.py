#!/usr/bin/env python3
"""
OpenSSL Builder Module
Build execution with database tracking and Conan integration
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any, NamedTuple
from dataclasses import dataclass
import json
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestResults:
    """Test execution results"""
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration: float = 0.0


@dataclass
class BuildResult:
    """Result of OpenSSL build"""
    success: bool
    build_dir: Optional[str] = None
    build_time: float = 0.0
    test_results: Optional[TestResults] = None
    db_id: Optional[str] = None
    error: Optional[str] = None


class OpenSSLBuilder:
    """OpenSSL build manager with database tracking"""
    
    def __init__(self, conan_api, profile=None, config_dir=None, openssl_dir=None,
                 jobs=None, clean=False, install=False, test=False, verbose=False, track_db=True):
        self.conan_api = conan_api
        self.profile = profile
        self.config_dir = Path(config_dir or "build-linux-gcc")
        self.openssl_dir = Path(openssl_dir or "openssl-source")
        self.jobs = jobs or self._detect_jobs()
        self.clean = clean
        self.install = install
        self.test = test
        self.verbose = verbose
        self.track_db = track_db
        
        # Database connection for tracking
        self.db_conn = None
        self.db_id = None
        
        if self.track_db:
            self._connect_database()
    
    def _detect_jobs(self) -> int:
        """Detect optimal number of parallel jobs"""
        try:
            return os.cpu_count() or 4
        except:
            return 4
    
    def _connect_database(self):
        """Connect to PostgreSQL database for build tracking"""
        try:
            # Try to get database connection from environment
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                # Try default PostgreSQL connection
                db_url = "postgresql://postgres:postgres@localhost:5432/openssl_tools"
            
            self.db_conn = psycopg2.connect(db_url)
            logger.info("Connected to build tracking database")
        except Exception as e:
            logger.warning(f"Could not connect to database: {e}")
            self.db_conn = None
    
    def _start_build_tracking(self) -> Optional[str]:
        """Start build tracking in database"""
        if not self.db_conn:
            return None
        
        try:
            with self.db_conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    INSERT INTO build_status 
                    (component_name, build_type, platform, compiler, status, started_at)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    RETURNING id
                """, ("openssl", "build", "unknown", "unknown", "running"))
                
                build_id = cur.fetchone()["id"]
                self.db_conn.commit()
                return str(build_id)
        except Exception as e:
            logger.warning(f"Could not start build tracking: {e}")
            return None
    
    def _update_build_tracking(self, build_id: str, status: str, error: str = None):
        """Update build tracking in database"""
        if not self.db_conn or not build_id:
            return
        
        try:
            with self.db_conn.cursor() as cur:
                cur.execute("""
                    UPDATE build_status 
                    SET status = %s, completed_at = NOW(), error_message = %s
                    WHERE id = %s
                """, (status, error, build_id))
                self.db_conn.commit()
        except Exception as e:
            logger.warning(f"Could not update build tracking: {e}")
    
    def _load_config(self) -> Optional[Dict[str, Any]]:
        """Load configuration from config.json"""
        config_file = self.config_dir / "config.json"
        if not config_file.exists():
            return None
        
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load configuration: {e}")
            return None
    
    def _build_make_command(self) -> str:
        """Build the make command"""
        cmd_parts = ["make"]
        
        if self.jobs > 1:
            cmd_parts.append(f"-j{self.jobs}")
        
        if self.verbose:
            cmd_parts.append("VERBOSE=1")
        
        return " ".join(cmd_parts)
    
    def _run_tests(self) -> TestResults:
        """Run OpenSSL tests"""
        if not self.test:
            return TestResults()
        
        try:
            start_time = time.time()
            
            # Run make test
            result = subprocess.run(
                ["make", "test"],
                cwd=self.openssl_dir,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            duration = time.time() - start_time
            
            # Parse test results (simplified)
            test_results = TestResults(duration=duration)
            
            if result.returncode == 0:
                # Try to parse test output for detailed results
                output = result.stdout
                if "All tests successful" in output:
                    test_results.passed = 1
                    test_results.total = 1
                else:
                    # Fallback parsing
                    test_results.passed = 1 if result.returncode == 0 else 0
                    test_results.total = 1
            else:
                test_results.failed = 1
                test_results.total = 1
            
            return test_results
            
        except subprocess.TimeoutExpired:
            return TestResults(failed=1, total=1, duration=1800.0)
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return TestResults(failed=1, total=1)
    
    def build(self) -> BuildResult:
        """Execute OpenSSL build"""
        start_time = time.time()
        
        # Start build tracking
        if self.track_db:
            self.db_id = self._start_build_tracking()
        
        try:
            # Load configuration
            config = self._load_config()
            if not config:
                return BuildResult(
                    success=False,
                    error="No configuration found. Run 'conan openssl configure' first."
                )
            
            # Check if OpenSSL source exists
            if not self.openssl_dir.exists():
                return BuildResult(
                    success=False,
                    error=f"OpenSSL source directory not found: {self.openssl_dir}"
                )
            
            # Clean if requested
            if self.clean:
                logger.info("Cleaning previous build...")
                subprocess.run(["make", "clean"], cwd=self.openssl_dir, check=False)
            
            # Build make command
            make_cmd = self._build_make_command()
            
            if self.verbose:
                logger.info(f"Build command: {make_cmd}")
            
            # Execute build
            logger.info("Starting OpenSSL build...")
            result = subprocess.run(
                make_cmd,
                cwd=self.openssl_dir,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode != 0:
                error_msg = f"Build failed: {result.stderr}"
                if self.track_db and self.db_id:
                    self._update_build_tracking(self.db_id, "failed", error_msg)
                return BuildResult(
                    success=False,
                    error=error_msg
                )
            
            # Run tests if requested
            test_results = self._run_tests()
            
            # Install if requested
            if self.install:
                logger.info("Installing OpenSSL...")
                install_result = subprocess.run(
                    ["make", "install"],
                    cwd=self.openssl_dir,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if install_result.returncode != 0:
                    logger.warning(f"Installation failed: {install_result.stderr}")
            
            build_time = time.time() - start_time
            
            # Update build tracking
            if self.track_db and self.db_id:
                self._update_build_tracking(self.db_id, "success")
            
            return BuildResult(
                success=True,
                build_dir=str(self.openssl_dir),
                build_time=build_time,
                test_results=test_results,
                db_id=self.db_id
            )
            
        except subprocess.TimeoutExpired:
            error_msg = "Build timed out after 1 hour"
            if self.track_db and self.db_id:
                self._update_build_tracking(self.db_id, "failed", error_msg)
            return BuildResult(
                success=False,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Unexpected error during build: {str(e)}"
            if self.track_db and self.db_id:
                self._update_build_tracking(self.db_id, "failed", error_msg)
            return BuildResult(
                success=False,
                error=error_msg
            )
        finally:
            if self.db_conn:
                self.db_conn.close()


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenSSL Builder Tool")
    parser.add_argument("--profile", "-p", help="Conan profile to use")
    parser.add_argument("--config-dir", help="Configuration directory")
    parser.add_argument("--openssl-dir", help="OpenSSL source directory")
    parser.add_argument("--jobs", "-j", type=int, help="Number of parallel jobs")
    parser.add_argument("--clean", action="store_true", help="Clean before building")
    parser.add_argument("--install", action="store_true", help="Install after building")
    parser.add_argument("--test", action="store_true", help="Run tests after building")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--no-db", action="store_true", help="Disable database tracking")
    
    args = parser.parse_args()
    
    # Create builder
    builder = OpenSSLBuilder(
        conan_api=None,  # Not needed for standalone
        profile=args.profile,
        config_dir=args.config_dir,
        openssl_dir=args.openssl_dir,
        jobs=args.jobs,
        clean=args.clean,
        install=args.install,
        test=args.test,
        verbose=args.verbose,
        track_db=not args.no_db
    )
    
    # Execute build
    result = builder.build()
    
    if result.success:
        print("✅ OpenSSL build completed successfully")
        print(f"Build directory: {result.build_dir}")
        print(f"Build time: {result.build_time:.2f} seconds")
        if result.test_results and result.test_results.total > 0:
            print(f"Tests: {result.test_results.passed}/{result.test_results.total} passed")
        if result.db_id:
            print(f"Database tracking ID: {result.db_id}")
    else:
        print(f"❌ OpenSSL build failed: {result.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
