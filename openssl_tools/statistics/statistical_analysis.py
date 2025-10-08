#!/usr/bin/env python3
"""
OpenSSL Statistical Analysis Tool - Python Implementation
Statistical analysis tools for OpenSSL
"""

import os
import sys
import argparse
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import numpy as np
    import scipy.stats as stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("scipy not available, using fallback calculations")


class StatisticalAnalysisTool:
    """Statistical analysis tools for OpenSSL"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Statistical Analysis tool"""
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or environment"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            'tools': {
                'statistical_analysis': {
                    'alpha': 0.05,
                    'confidence_level': 0.95
                }
            }
        }
    
    def parse_arguments(self, args: List[str]) -> argparse.Namespace:
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description='Statistical analysis tools for OpenSSL',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  statistical-analysis --help
  statistical-analysis --analyze-file data.txt
  statistical-analysis --chi-square-test data.txt
            """
        )
        
        parser.add_argument('--analyze-file', help='File to analyze')
        parser.add_argument('--chi-square-test', help='Perform chi-square test on file')
        parser.add_argument('--t-test', help='Perform t-test on file')
        parser.add_argument('--alpha', type=float, default=0.05, help='Significance level')
        parser.add_argument('--output', help='Output file')
        parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        return parser.parse_args(args)
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a file for statistical properties"""
        try:
            with open(file_path, 'r') as f:
                data = f.read()
            
            # Basic analysis
            lines = data.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            
            analysis = {
                'file_path': file_path,
                'total_lines': len(lines),
                'non_empty_lines': len(non_empty_lines),
                'total_characters': len(data),
                'average_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0
            }
            
            # If scipy is available, do more advanced analysis
            if SCIPY_AVAILABLE:
                # Convert to numeric data if possible
                numeric_data = []
                for line in non_empty_lines:
                    try:
                        numeric_data.append(float(line.strip()))
                    except ValueError:
                        continue
                
                if numeric_data:
                    data_array = np.array(numeric_data)
                    analysis.update({
                        'mean': float(np.mean(data_array)),
                        'median': float(np.median(data_array)),
                        'std': float(np.std(data_array)),
                        'min': float(np.min(data_array)),
                        'max': float(np.max(data_array)),
                        'count': len(numeric_data)
                    })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze file {file_path}: {e}")
            return {}
    
    def chi_square_test(self, file_path: str, alpha: float = 0.05) -> Dict[str, Any]:
        """Perform chi-square test on data"""
        try:
            with open(file_path, 'r') as f:
                data = f.read()
            
            # Parse data (assuming space-separated values)
            lines = data.strip().split('\n')
            observed = []
            expected = []
            
            for line in lines:
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        observed.append(int(parts[0]))
                        expected.append(int(parts[1]))
            
            if not observed or not expected:
                logger.error("No valid data found for chi-square test")
                return {}
            
            if SCIPY_AVAILABLE:
                # Use scipy for chi-square test
                chi2_stat, p_value = stats.chisquare(observed, expected)
                
                result = {
                    'test': 'chi-square',
                    'chi2_statistic': float(chi2_stat),
                    'p_value': float(p_value),
                    'alpha': alpha,
                    'significant': p_value < alpha,
                    'observed': observed,
                    'expected': expected
                }
            else:
                # Fallback calculation
                chi2_stat = sum((o - e) ** 2 / e for o, e in zip(observed, expected))
                df = len(observed) - 1
                
                # Simple approximation for p-value
                p_value = 0.5  # Placeholder
                
                result = {
                    'test': 'chi-square',
                    'chi2_statistic': chi2_stat,
                    'p_value': p_value,
                    'alpha': alpha,
                    'significant': chi2_stat > 3.84,  # Rough approximation
                    'observed': observed,
                    'expected': expected,
                    'degrees_of_freedom': df
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to perform chi-square test: {e}")
            return {}
    
    def t_test(self, file_path: str, alpha: float = 0.05) -> Dict[str, Any]:
        """Perform t-test on data"""
        try:
            with open(file_path, 'r') as f:
                data = f.read()
            
            # Parse data (assuming one value per line)
            lines = data.strip().split('\n')
            values = []
            
            for line in lines:
                if line.strip():
                    try:
                        values.append(float(line.strip()))
                    except ValueError:
                        continue
            
            if len(values) < 2:
                logger.error("Insufficient data for t-test")
                return {}
            
            if SCIPY_AVAILABLE:
                # Use scipy for t-test
                t_stat, p_value = stats.ttest_1samp(values, 0)
                
                result = {
                    'test': 't-test',
                    't_statistic': float(t_stat),
                    'p_value': float(p_value),
                    'alpha': alpha,
                    'significant': p_value < alpha,
                    'sample_size': len(values),
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values))
                }
            else:
                # Fallback calculation
                mean = sum(values) / len(values)
                std = math.sqrt(sum((x - mean) ** 2 for x in values) / (len(values) - 1))
                t_stat = mean / (std / math.sqrt(len(values)))
                
                # Simple approximation for p-value
                p_value = 0.5  # Placeholder
                
                result = {
                    'test': 't-test',
                    't_statistic': t_stat,
                    'p_value': p_value,
                    'alpha': alpha,
                    'significant': abs(t_stat) > 1.96,  # Rough approximation
                    'sample_size': len(values),
                    'mean': mean,
                    'std': std
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to perform t-test: {e}")
            return {}
    
    def run(self, args: List[str]) -> int:
        """Main entry point"""
        try:
            parsed_args = self.parse_arguments(args)
            
            if parsed_args.analyze_file:
                analysis = self.analyze_file(parsed_args.analyze_file)
                if analysis:
                    logger.info(f"Analysis of {parsed_args.analyze_file}:")
                    for key, value in analysis.items():
                        logger.info(f"  {key}: {value}")
                    
                    if parsed_args.output:
                        with open(parsed_args.output, 'w') as f:
                            json.dump(analysis, f, indent=2)
                        logger.info(f"Results saved to {parsed_args.output}")
                    
                    return 0
                else:
                    return 1
            
            if parsed_args.chi_square_test:
                result = self.chi_square_test(parsed_args.chi_square_test, parsed_args.alpha)
                if result:
                    logger.info(f"Chi-square test results:")
                    for key, value in result.items():
                        logger.info(f"  {key}: {value}")
                    
                    if parsed_args.output:
                        with open(parsed_args.output, 'w') as f:
                            json.dump(result, f, indent=2)
                        logger.info(f"Results saved to {parsed_args.output}")
                    
                    return 0
                else:
                    return 1
            
            if parsed_args.t_test:
                result = self.t_test(parsed_args.t_test, parsed_args.alpha)
                if result:
                    logger.info(f"T-test results:")
                    for key, value in result.items():
                        logger.info(f"  {key}: {value}")
                    
                    if parsed_args.output:
                        with open(parsed_args.output, 'w') as f:
                            json.dump(result, f, indent=2)
                        logger.info(f"Results saved to {parsed_args.output}")
                    
                    return 0
                else:
                    return 1
            
            # Show help if no action specified
            parsed_args.help = True
            return 0
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return 1


def main():
    """Main entry point for command line usage"""
    tool = StatisticalAnalysisTool()
    sys.exit(tool.run(sys.argv[1:]))


if __name__ == '__main__':
    main()