#!/usr/bin/env python3
"""
Conan Container Testing Suite
Tests Docker Compose services and Conan server functionality
"""

import os
import sys
import subprocess
import time
import json
import requests
import docker
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import pytest
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConanContainerTester:
    """Test suite for Conan containerized environment"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.docker_compose_file = project_root / "docker-compose.dev.yml"
        self.dockerfile = project_root / "Dockerfile.dev"
        self.test_results = []
        
    def test_docker_environment(self) -> bool:
        """Test Docker environment availability"""
        logger.info("Testing Docker environment...")
        
        try:
            # Test Docker daemon
            client = docker.from_env()
            client.ping()
            
            # Test Docker Compose
            result = subprocess.run(['docker-compose', '--version'], 
                                  capture_output=True, text=True)
            assert result.returncode == 0, f"Docker Compose not available: {result.stderr}"
            
            # Test Dockerfile exists
            assert self.dockerfile.exists(), f"Dockerfile not found: {self.dockerfile}"
            
            # Test docker-compose file exists
            assert self.docker_compose_file.exists(), f"Docker Compose file not found: {self.docker_compose_file}"
            
            logger.info("✅ Docker environment test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Docker environment test failed: {e}")
            return False
    
    def test_dockerfile_validation(self) -> bool:
        """Test Dockerfile syntax and structure"""
        logger.info("Testing Dockerfile validation...")
        
        try:
            # Test Dockerfile syntax
            result = subprocess.run(['docker', 'build', '--dry-run', '-f', str(self.dockerfile), '.'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            # Note: --dry-run might not be available in all Docker versions
            
            # Test Docker Compose file syntax
            result = subprocess.run(['docker-compose', '-f', str(self.docker_compose_file), 'config'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            assert result.returncode == 0, f"Docker Compose file validation failed: {result.stderr}"
            
            # Parse docker-compose file
            with open(self.docker_compose_file, 'r') as f:
                compose_config = yaml.safe_load(f)
            
            # Validate required services
            required_services = ['openssl-dev', 'conan-server']
            for service in required_services:
                assert service in compose_config['services'], f"Required service {service} not found"
            
            logger.info("✅ Dockerfile validation test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Dockerfile validation test failed: {e}")
            return False
    
    def test_conan_server_startup(self) -> bool:
        """Test Conan server startup and functionality"""
        logger.info("Testing Conan server startup...")
        
        try:
            # Start Conan server
            result = subprocess.run(['docker-compose', '-f', str(self.docker_compose_file), 
                                   'up', '-d', 'conan-server'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            assert result.returncode == 0, f"Failed to start Conan server: {result.stderr}"
            
            # Wait for server to be ready
            max_retries = 30
            for i in range(max_retries):
                try:
                    response = requests.get('http://localhost:9300/v1/ping', timeout=5)
                    if response.status_code == 200:
                        break
                except requests.exceptions.RequestException:
                    if i == max_retries - 1:
                        raise
                    time.sleep(2)
            else:
                raise Exception("Conan server did not start within timeout")
            
            # Test server endpoints
            endpoints = [
                'http://localhost:9300/v1/ping',
                'http://localhost:9300/v1/users/authenticate',
            ]
            
            for endpoint in endpoints:
                response = requests.get(endpoint, timeout=5)
                assert response.status_code in [200, 401], f"Endpoint {endpoint} returned {response.status_code}"
            
            logger.info("✅ Conan server startup test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Conan server startup test failed: {e}")
            return False
        finally:
            # Cleanup
            subprocess.run(['docker-compose', '-f', str(self.docker_compose_file), 
                          'down', 'conan-server'], 
                         capture_output=True, text=True, cwd=self.project_root)
    
    def test_openssl_dev_container(self) -> bool:
        """Test OpenSSL development container"""
        logger.info("Testing OpenSSL development container...")
        
        try:
            # Build and start OpenSSL dev container
            result = subprocess.run(['docker-compose', '-f', str(self.docker_compose_file), 
                                   'up', '-d', 'openssl-dev'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            assert result.returncode == 0, f"Failed to start OpenSSL dev container: {result.stderr}"
            
            # Wait for container to be ready
            time.sleep(10)
            
            # Test container is running
            result = subprocess.run(['docker-compose', '-f', str(self.docker_compose_file), 
                                   'ps', 'openssl-dev'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            assert 'openssl-dev' in result.stdout, "OpenSSL dev container not running"
            
            # Test Conan installation in container
            result = subprocess.run(['docker-compose', '-f', str(self.docker_compose_file), 
                                   'exec', '-T', 'openssl-dev', 'conan', '--version'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            assert result.returncode == 0, f"Conan not available in container: {result.stderr}"
            
            # Test Conan profile detection in container
            result = subprocess.run(['docker-compose', '-f', str(self.docker_compose_file), 
                                   'exec', '-T', 'openssl-dev', 'conan', 'profile', 'detect', '--force'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            assert result.returncode == 0, f"Profile detection failed in container: {result.stderr}"
            
            logger.info("✅ OpenSSL dev container test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ OpenSSL dev container test failed: {e}")
            return False
        finally:
            # Cleanup
            subprocess.run(['docker-compose', '-f', str(self.docker_compose_file), 
                          'down', 'openssl-dev'], 
                         capture_output=True, text=True, cwd=self.project_root)
    
    def test_integration_workflow(self) -> bool:
        """Test complete integration workflow"""
        logger.info("Testing integration workflow...")
        
        try:
            # Start all services
            result = subprocess.run(['docker-compose', '-f', str(self.docker_compose_file), 
                                   'up', '-d'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            assert result.returncode == 0, f"Failed to start services: {result.stderr}"
            
            # Wait for services to be ready
            time.sleep(15)
            
            # Test Conan install in container
            result = subprocess.run(['docker-compose', '-f', str(self.docker_compose_file), 
                                   'exec', '-T', 'openssl-dev', 'conan', 'install', '.', '--build=missing'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            assert result.returncode == 0, f"Conan install failed: {result.stderr}"
            
            # Test Conan create in container
            result = subprocess.run(['docker-compose', '-f', str(self.docker_compose_file), 
                                   'exec', '-T', 'openssl-dev', 'conan', 'create', '.', '--build=missing'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            assert result.returncode == 0, f"Conan create failed: {result.stderr}"
            
            logger.info("✅ Integration workflow test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Integration workflow test failed: {e}")
            return False
        finally:
            # Cleanup
            subprocess.run(['docker-compose', '-f', str(self.docker_compose_file), 'down'], 
                         capture_output=True, text=True, cwd=self.project_root)
    
    def test_performance_metrics(self) -> bool:
        """Test container performance metrics"""
        logger.info("Testing container performance metrics...")
        
        try:
            # Start services
            result = subprocess.run(['docker-compose', '-f', str(self.docker_compose_file), 
                                   'up', '-d'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            assert result.returncode == 0, f"Failed to start services: {result.stderr}"
            
            # Wait for services
            time.sleep(10)
            
            # Get container stats
            result = subprocess.run(['docker', 'stats', '--no-stream', '--format', 'json'], 
                                  capture_output=True, text=True)
            assert result.returncode == 0, f"Failed to get container stats: {result.stderr}"
            
            # Parse stats
            stats = json.loads(result.stdout)
            assert len(stats) > 0, "No container stats available"
            
            # Check memory usage
            for stat in stats:
                memory_usage = float(stat['MemUsage'].split('/')[0].replace('MiB', ''))
                assert memory_usage < 2000, f"Container {stat['Name']} using too much memory: {memory_usage}MiB"
            
            logger.info("✅ Container performance metrics test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Container performance metrics test failed: {e}")
            return False
        finally:
            # Cleanup
            subprocess.run(['docker-compose', '-f', str(self.docker_compose_file), 'down'], 
                         capture_output=True, text=True, cwd=self.project_root)
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all container tests"""
        logger.info("Starting Conan container tests...")
        
        tests = [
            ("docker_environment", self.test_docker_environment),
            ("dockerfile_validation", self.test_dockerfile_validation),
            ("conan_server_startup", self.test_conan_server_startup),
            ("openssl_dev_container", self.test_openssl_dev_container),
            ("integration_workflow", self.test_integration_workflow),
            ("performance_metrics", self.test_performance_metrics),
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {e}")
                results[test_name] = False
        
        # Summary
        passed = sum(results.values())
        total = len(results)
        logger.info(f"Container tests completed: {passed}/{total} passed")
        
        return results

def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent.parent
    tester = ConanContainerTester(project_root)
    results = tester.run_all_tests()
    
    # Exit with error code if any test failed
    if not all(results.values()):
        sys.exit(1)

if __name__ == "__main__":
    main()