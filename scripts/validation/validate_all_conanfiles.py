#!/usr/bin/env python3
"""
Comprehensive Conanfile Validation Script
Validates all conanfile.py files across the workspace for syntax, dependencies, and schema compliance
"""

import os
import sys
import ast
import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import importlib.util

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConanfileValidator:
    """Validates conanfile.py files for syntax, dependencies, and schema compliance"""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.validation_results = {
            "validation_timestamp": datetime.now().isoformat(),
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "files": []
        }

        # Required attributes for conanfiles
        self.required_attributes = ["name", "version", "license"]
        self.optional_attributes = ["description", "url", "homepage", "topics"]

        # Valid package types
        self.valid_package_types = [
            "library", "application", "python-require", "data", "build-scripts"
        ]

        # Version format regex (semantic versioning)
        self.version_pattern = re.compile(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)*$')

    def validate_all_conanfiles(self) -> Dict:
        """Validate all conanfile.py files in the workspace"""
        logger.info("🔍 Starting comprehensive conanfile validation...")

        # Find all conanfile.py files
        conanfiles = list(self.workspace_root.rglob("conanfile.py"))
        self.validation_results["total_files"] = len(conanfiles)

        logger.info(f"Found {len(conanfiles)} conanfile.py files to validate")

        for conanfile_path in conanfiles:
            logger.info(f"Validating: {conanfile_path.relative_to(self.workspace_root)}")

            file_result = self._validate_single_conanfile(conanfile_path)
            self.validation_results["files"].append(file_result)

            if file_result["valid"]:
                self.validation_results["valid_files"] += 1
            else:
                self.validation_results["invalid_files"] += 1

        # Generate summary
        self._generate_validation_summary()

        return self.validation_results

    def _validate_single_conanfile(self, conanfile_path: Path) -> Dict:
        """Validate a single conanfile.py file"""
        result = {
            "file_path": str(conanfile_path.relative_to(self.workspace_root)),
            "absolute_path": str(conanfile_path),
            "valid": True,
            "errors": [],
            "warnings": [],
            "info": {}
        }

        try:
            # Read file content
            with open(conanfile_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 1. Syntax validation
            syntax_result = self._validate_syntax(content, conanfile_path)
            if not syntax_result["valid"]:
                result["valid"] = False
                result["errors"].extend(syntax_result["errors"])
                return result

            # 2. AST analysis
            ast_result = self._validate_ast(content, conanfile_path)
            if not ast_result["valid"]:
                result["valid"] = False
                result["errors"].extend(ast_result["errors"])
                return result  # Can't continue without AST analysis
            else:
                result["info"].update(ast_result["info"])

            # Get class info for subsequent validations
            class_info = ast_result.get("info", {}).get("class_info", {})

            # 3. Attribute validation
            attr_result = self._validate_attributes(class_info)
            if not attr_result["valid"]:
                result["valid"] = False
                result["errors"].extend(attr_result["errors"])
            result["warnings"].extend(attr_result["warnings"])
            result["info"].update(attr_result["info"])

            # 4. Dependency validation
            dep_result = self._validate_dependencies(class_info)
            if not dep_result["valid"]:
                result["valid"] = False
                result["errors"].extend(dep_result["errors"])
            result["warnings"].extend(dep_result["warnings"])
            result["info"].update(dep_result["info"])

            # 5. Method validation
            method_result = self._validate_methods(class_info)
            if not method_result["valid"]:
                result["warnings"].extend(method_result["warnings"])
            result["info"].update(method_result["info"])

            # 6. Database schema integration check
            db_result = self._check_database_integration(content)
            result["info"]["database_integration"] = db_result

        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Validation failed: {str(e)}")
            logger.error(f"Failed to validate {conanfile_path}: {e}")

        return result

    def _validate_syntax(self, content: str, file_path: Path) -> Dict:
        """Validate Python syntax"""
        result = {"valid": True, "errors": []}

        try:
            compile(content, str(file_path), 'exec')
        except SyntaxError as e:
            result["valid"] = False
            result["errors"].append(f"Syntax error at line {e.lineno}: {e.msg}")
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Compilation error: {str(e)}")

        return result

    def _validate_ast(self, content: str, file_path: Path) -> Dict:
        """Validate using AST analysis"""
        result = {"valid": True, "errors": [], "info": {}}

        try:
            tree = ast.parse(content, filename=str(file_path))

            # Find ConanFile class
            conanfile_class = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it inherits from ConanFile
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == "ConanFile":
                            conanfile_class = node
                            break
                        elif isinstance(base, ast.Attribute):
                            if base.attr == "ConanFile":
                                conanfile_class = node
                                break

            if not conanfile_class:
                result["valid"] = False
                result["errors"].append("No ConanFile class found")
                return result

            # Extract class information
            class_info = self._extract_class_info(conanfile_class)
            result["info"]["class_info"] = class_info

        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"AST analysis failed: {str(e)}")

        return result

    def _extract_class_info(self, class_node: ast.ClassDef) -> Dict:
        """Extract information from ConanFile class"""
        class_info = {
            "name": class_node.name,
            "attributes": {},
            "methods": [],
            "python_requires": [],
            "requires": [],
            "tool_requires": []
        }

        for node in class_node.body:
            if isinstance(node, ast.Assign):
                # Extract class attributes
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if isinstance(node.value, ast.Constant):
                            class_info["attributes"][target.id] = node.value.value
                        elif isinstance(node.value, ast.Str):  # Python < 3.8
                            class_info["attributes"][target.id] = node.value.s
                        elif isinstance(node.value, ast.List):
                            # Handle lists (like topics)
                            class_info["attributes"][target.id] = "list"

            elif isinstance(node, ast.FunctionDef):
                # Extract methods
                class_info["methods"].append(node.name)

                # Check for specific method patterns
                if node.name == "requirements":
                    class_info["requires"] = self._extract_requirements_from_method(node)
                elif node.name == "build_requirements":
                    class_info["tool_requires"] = self._extract_requirements_from_method(node)
                elif node.name == "init":
                    class_info["python_requires"] = self._extract_python_requires_from_method(node)

        return class_info

    def _extract_requirements_from_method(self, method_node: ast.FunctionDef) -> List[str]:
        """Extract requirements from requirements() or build_requirements() method"""
        requirements = []

        for node in ast.walk(method_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == "requires":
                        for arg in node.args:
                            if isinstance(arg, ast.Constant):
                                requirements.append(str(arg.value))
                            elif isinstance(arg, ast.Str):  # Python < 3.8
                                requirements.append(arg.s)
                    elif node.func.attr == "tool_requires":
                        for arg in node.args:
                            if isinstance(arg, ast.Constant):
                                requirements.append(str(arg.value))
                            elif isinstance(arg, ast.Str):  # Python < 3.8
                                requirements.append(arg.s)

        return requirements

    def _extract_python_requires_from_method(self, method_node: ast.FunctionDef) -> List[str]:
        """Extract python_requires from init() method"""
        python_requires = []

        for node in ast.walk(method_node):
            if isinstance(node, ast.Assign):
                if isinstance(node.targets[0], ast.Name) and node.targets[0].id == "python_requires":
                    if isinstance(node.value, ast.Constant):
                        python_requires.append(str(node.value.value))
                    elif isinstance(node.value, ast.Str):  # Python < 3.8
                        python_requires.append(node.value.s)
                    elif isinstance(node.value, ast.List):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant):
                                python_requires.append(str(elt.value))
                            elif isinstance(elt, ast.Str):  # Python < 3.8
                                python_requires.append(elt.s)

        return python_requires

    def _validate_attributes(self, class_info: Dict) -> Dict:
        """Validate required and optional attributes"""
        result = {"valid": True, "errors": [], "warnings": [], "info": {}}
        attributes = class_info.get("attributes", {})
        methods = class_info.get("methods", [])

        # Check required attributes - be flexible about version (can be set dynamically)
        for attr in self.required_attributes:
            if attr == "version" and "set_version" in methods:
                # Version can be set dynamically via set_version() method
                result["info"][f"has_{attr}"] = True
                result["info"]["version_dynamic"] = True
            elif attr not in attributes:
                result["valid"] = False
                result["errors"].append(f"Missing required attribute: {attr}")
            else:
                result["info"][f"has_{attr}"] = True

        # Check optional attributes
        for attr in self.optional_attributes:
            if attr in attributes:
                result["info"][f"has_{attr}"] = True

        # Validate version format (only if static)
        if "version" in attributes and not result["info"].get("version_dynamic", False):
            version = str(attributes["version"])
            if not self.version_pattern.match(version):
                result["warnings"].append(f"Version '{version}' doesn't follow semantic versioning")
            result["info"]["version"] = version

        # Validate package type
        if "package_type" in attributes:
            package_type = attributes["package_type"]
            if package_type not in self.valid_package_types:
                result["warnings"].append(f"Unknown package type: {package_type}")
            result["info"]["package_type"] = package_type

        return result

    def _validate_dependencies(self, class_info: Dict) -> Dict:
        """Validate dependencies and version constraints"""
        result = {"valid": True, "errors": [], "warnings": [], "info": {}}

        # Check python_requires
        python_requires = class_info.get("python_requires", [])
        if python_requires:
            result["info"]["python_requires"] = python_requires
            for req in python_requires:
                if not self._validate_dependency_format(req):
                    result["warnings"].append(f"Invalid python_requires format: {req}")

        # Check requires
        requires = class_info.get("requires", [])
        if requires:
            result["info"]["requires"] = requires
            for req in requires:
                if not self._validate_dependency_format(req):
                    result["warnings"].append(f"Invalid requires format: {req}")

        # Check tool_requires
        tool_requires = class_info.get("tool_requires", [])
        if tool_requires:
            result["info"]["tool_requires"] = tool_requires
            for req in tool_requires:
                if not self._validate_dependency_format(req):
                    result["warnings"].append(f"Invalid tool_requires format: {req}")

        return result

    def _validate_dependency_format(self, dependency: str) -> bool:
        """Validate dependency format (name/version@user/channel)"""
        # Basic format check
        if "@" in dependency:
            parts = dependency.split("@")
            if len(parts) == 2:
                name_version = parts[0]
                user_channel = parts[1]

                # Check name/version format
                if "/" in name_version:
                    name, version = name_version.split("/", 1)
                    if name and version:
                        return True

        return False

    def _validate_methods(self, class_info: Dict) -> Dict:
        """Validate required and recommended methods"""
        result = {"valid": True, "warnings": [], "info": {}}
        methods = class_info.get("methods", [])

        # Check for required methods
        required_methods = ["package_info"]
        for method in required_methods:
            if method not in methods:
                result["warnings"].append(f"Missing recommended method: {method}")
            else:
                result["info"][f"has_{method}"] = True

        # Check for package method (required for most package types)
        if "package" not in methods:
            result["warnings"].append("Missing package() method - may be required for packaging")
        else:
            result["info"]["has_package"] = True

        result["info"]["methods"] = methods

        return result

    def _check_database_integration(self, content: str) -> Dict:
        """Check for database schema integration hooks"""
        integration_info = {
            "has_database_import": False,
            "has_package_tracking": False,
            "has_config_validation": False,
            "integration_level": "none"
        }

        # Check for database imports
        if "openssl_tools.database" in content or "OpenSSLSchemaValidator" in content:
            integration_info["has_database_import"] = True

        # Check for package tracking
        if "track_package_in_cache" in content:
            integration_info["has_package_tracking"] = True

        # Check for configuration validation
        if "validate_openssl_configuration" in content:
            integration_info["has_config_validation"] = True

        # Determine integration level
        if integration_info["has_database_import"] and integration_info["has_package_tracking"]:
            integration_info["integration_level"] = "full"
        elif integration_info["has_database_import"]:
            integration_info["integration_level"] = "partial"

        return integration_info

    def _generate_validation_summary(self):
        """Generate validation summary"""
        total = self.validation_results["total_files"]
        valid = self.validation_results["valid_files"]
        invalid = self.validation_results["invalid_files"]

        logger.info(f"📊 Validation Summary:")
        logger.info(f"   Total files: {total}")
        logger.info(f"   Valid files: {valid}")
        logger.info(f"   Invalid files: {invalid}")
        logger.info(f"   Success rate: {(valid/total*100):.1f}%" if total > 0 else "   Success rate: 0%")

        # Count database integration
        db_integrated = sum(1 for f in self.validation_results["files"]
                          if f["info"].get("database_integration", {}).get("integration_level") == "full")
        logger.info(f"   Database integrated: {db_integrated}")

    def save_results(self, output_path: Path):
        """Save validation results to file"""
        with open(output_path, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        logger.info(f"📄 Validation results saved to: {output_path}")

def main():
    """Main validation function"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate all conanfile.py files")
    parser.add_argument("--workspace-root", type=Path, default=Path.cwd().parent,
                       help="Workspace root directory")
    parser.add_argument("--output", type=Path,
                       default=Path("conanfile-validation-results.json"),
                       help="Output file for results")

    args = parser.parse_args()

    # Initialize validator
    validator = ConanfileValidator(args.workspace_root)

    # Run validation
    results = validator.validate_all_conanfiles()

    # Save results
    validator.save_results(args.output)

    # Exit with error code if any files are invalid
    if results["invalid_files"] > 0:
        logger.error(f"❌ Validation failed: {results['invalid_files']} files have errors")
        return 1
    else:
        logger.info("✅ All conanfiles validated successfully")
        return 0

if __name__ == "__main__":
    exit(main())
