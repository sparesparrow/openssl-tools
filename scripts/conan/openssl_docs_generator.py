#!/usr/bin/env python3
"""
OpenSSL Documentation Generator Module
Extract and format OpenSSL documentation from sources
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import json
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DocsResult:
    """Result of documentation generation"""
    success: bool
    output_dir: Optional[str] = None
    generated_files: List[str] = None
    error: Optional[str] = None


class OpenSSLDocsGenerator:
    """OpenSSL documentation generator"""
    
    def __init__(self, conan_api, openssl_dir=None, output_dir=None, format="html",
                 sections=None, language="en", template=None, verbose=False):
        self.conan_api = conan_api
        self.openssl_dir = Path(openssl_dir or "openssl-source")
        self.output_dir = Path(output_dir or "docs")
        self.format = format
        self.sections = sections or ["all"]
        self.language = language
        self.template = Path(template) if template else None
        self.verbose = verbose
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _extract_man_pages(self) -> List[Path]:
        """Extract POD man pages from OpenSSL source"""
        man_pages = []
        doc_dir = self.openssl_dir / "doc"
        
        if not doc_dir.exists():
            logger.warning("OpenSSL doc directory not found")
            return man_pages
        
        # Find POD files
        for pod_file in doc_dir.rglob("*.pod"):
            man_pages.append(pod_file)
        
        return man_pages
    
    def _convert_pod_to_html(self, pod_file: Path) -> Optional[Path]:
        """Convert POD file to HTML"""
        try:
            output_file = self.output_dir / f"{pod_file.stem}.html"
            
            result = subprocess.run(
                ["pod2html", "--infile", str(pod_file), "--outfile", str(output_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return output_file
            else:
                logger.error(f"Failed to convert {pod_file}: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout converting {pod_file}")
            return None
        except FileNotFoundError:
            logger.warning("pod2html not found, skipping POD conversion")
            return None
    
    def _extract_api_docs(self) -> List[Path]:
        """Extract API documentation from header files"""
        api_docs = []
        include_dir = self.openssl_dir / "include"
        
        if not include_dir.exists():
            logger.warning("OpenSSL include directory not found")
            return api_docs
        
        # Find header files with documentation
        for header_file in include_dir.rglob("*.h"):
            if self._has_documentation(header_file):
                api_docs.append(header_file)
        
        return api_docs
    
    def _has_documentation(self, header_file: Path) -> bool:
        """Check if header file contains documentation"""
        try:
            with open(header_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Look for common documentation patterns
                return any(pattern in content for pattern in [
                    "/**", "/*!", "///", "//!", "/* @", "/*!"
                ])
        except Exception:
            return False
    
    def _extract_header_docs(self, header_file: Path) -> Optional[Path]:
        """Extract documentation from header file"""
        try:
            with open(header_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Simple extraction of function documentation
            doc_content = self._parse_c_docs(content)
            
            if doc_content:
                output_file = self.output_dir / f"{header_file.stem}_api.html"
                
                html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{header_file.name} API Documentation</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .function {{ margin: 20px 0; padding: 10px; border: 1px solid #ccc; }}
        .function-name {{ font-weight: bold; color: #0066cc; }}
        .function-desc {{ margin-top: 5px; }}
    </style>
</head>
<body>
    <h1>{header_file.name} API Documentation</h1>
    {doc_content}
</body>
</html>
"""
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                return output_file
            
        except Exception as e:
            logger.error(f"Failed to extract docs from {header_file}: {e}")
            return None
    
    def _parse_c_docs(self, content: str) -> str:
        """Parse C documentation comments"""
        html_docs = []
        
        # Simple regex to find function documentation
        # This is a basic implementation - could be enhanced
        pattern = r'/\*\*\s*(.*?)\s*\*/\s*\w+\s+\w+\s*\([^)]*\);'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            # Clean up the documentation
            doc = match.strip().replace('*', '').strip()
            if doc:
                html_docs.append(f'<div class="function"><div class="function-desc">{doc}</div></div>')
        
        return '\n'.join(html_docs)
    
    def _generate_index(self, generated_files: List[str]) -> Path:
        """Generate index page for documentation"""
        index_file = self.output_dir / "index.html"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>OpenSSL Documentation</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .file-list {{ list-style-type: none; padding: 0; }}
        .file-list li {{ margin: 10px 0; }}
        .file-list a {{ text-decoration: none; color: #0066cc; }}
        .file-list a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>OpenSSL Documentation</h1>
    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>Available Documentation</h2>
    <ul class="file-list">
"""
        
        for file_path in generated_files:
            file_name = Path(file_path).name
            html_content += f'        <li><a href="{file_name}">{file_name}</a></li>\n'
        
        html_content += """
    </ul>
</body>
</html>
"""
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return index_file
    
    def generate(self) -> DocsResult:
        """Execute documentation generation"""
        generated_files = []
        
        try:
            if not self.openssl_dir.exists():
                return DocsResult(
                    success=False,
                    error=f"OpenSSL source directory not found: {self.openssl_dir}"
                )
            
            # Generate man pages if requested
            if "man" in self.sections or "all" in self.sections:
                man_pages = self._extract_man_pages()
                for pod_file in man_pages:
                    if self.verbose:
                        logger.info(f"Converting {pod_file}")
                    
                    html_file = self._convert_pod_to_html(pod_file)
                    if html_file:
                        generated_files.append(str(html_file))
            
            # Generate API documentation if requested
            if "api" in self.sections or "all" in self.sections:
                api_docs = self._extract_api_docs()
                for header_file in api_docs:
                    if self.verbose:
                        logger.info(f"Extracting API docs from {header_file}")
                    
                    html_file = self._extract_header_docs(header_file)
                    if html_file:
                        generated_files.append(str(html_file))
            
            # Generate index page
            if generated_files:
                index_file = self._generate_index(generated_files)
                generated_files.append(str(index_file))
            
            return DocsResult(
                success=True,
                output_dir=str(self.output_dir),
                generated_files=generated_files
            )
            
        except Exception as e:
            return DocsResult(
                success=False,
                error=f"Documentation generation failed: {str(e)}"
            )


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenSSL Documentation Generator")
    parser.add_argument("--openssl-dir", help="OpenSSL source directory")
    parser.add_argument("--output-dir", help="Documentation output directory")
    parser.add_argument("--format", choices=["html", "pdf", "man", "markdown"], 
                       default="html", help="Output format")
    parser.add_argument("--sections", nargs="+", 
                       choices=["man", "api", "guide", "faq", "all"], 
                       default=["all"], help="Documentation sections to generate")
    parser.add_argument("--language", default="en", help="Documentation language")
    parser.add_argument("--template", help="Custom template directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Create generator
    generator = OpenSSLDocsGenerator(
        conan_api=None,  # Not needed for standalone
        openssl_dir=args.openssl_dir,
        output_dir=args.output_dir,
        format=args.format,
        sections=args.sections,
        language=args.language,
        template=args.template,
        verbose=args.verbose
    )
    
    # Execute documentation generation
    result = generator.generate()
    
    if result.success:
        print("✅ OpenSSL documentation generation completed successfully")
        print(f"Output directory: {result.output_dir}")
        print(f"Generated files: {len(result.generated_files)}")
        if args.verbose:
            for file in result.generated_files:
                print(f"  - {file}")
    else:
        print(f"❌ OpenSSL documentation generation failed: {result.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
