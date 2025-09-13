#!/usr/bin/env python3
"""
Simple runner script for ontology performance tests.

This script provides an easy way to run the performance tests with different configurations.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Run ontology performance tests')
    parser.add_argument('--install-deps', action='store_true', 
                       help='Install performance testing dependencies')
    parser.add_argument('--ontology-file', 
                       help='Path to ontology YAML file (default: company.yaml)')
    parser.add_argument('--output', 
                       help='Output file for the report')
    parser.add_argument('--iterations', type=int, default=10,
                       help='Number of iterations per test (default: 10)')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick tests with fewer iterations')
    parser.add_argument('--pytest', action='store_true',
                       help='Run tests using pytest instead of standalone')
    
    args = parser.parse_args()
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    test_file = script_dir / 'test_ontology_performance.py'
    
    if not test_file.exists():
        print(f"Error: Test file not found at {test_file}")
        sys.exit(1)
    
    # Install dependencies if requested
    if args.install_deps:
        print("Installing performance testing dependencies...")
        requirements_file = script_dir / 'requirements_performance.txt'
        if requirements_file.exists():
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)])
        else:
            print("Warning: requirements_performance.txt not found")
    
    # Adjust iterations for quick mode
    iterations = 3 if args.quick else args.iterations
    
    # Prepare command arguments
    cmd_args = []
    
    if args.pytest:
        # Run with pytest
        cmd = [sys.executable, '-m', 'pytest', str(test_file), '-v']
        if args.output:
            cmd.extend(['--benchmark-save', args.output.replace('.txt', '')])
    else:
        # Run standalone
        cmd = [sys.executable, str(test_file)]
        if args.ontology_file:
            cmd.extend(['--ontology-file', args.ontology_file])
        if args.output:
            cmd.extend(['--output', args.output])
        cmd.extend(['--iterations', str(iterations)])
    
    print(f"Running command: {' '.join(cmd)}")
    print(f"Test iterations: {iterations}")
    if args.ontology_file:
        print(f"Ontology file: {args.ontology_file}")
    if args.output:
        print(f"Output file: {args.output}")
    print()
    
    # Run the tests
    try:
        result = subprocess.run(cmd, cwd=script_dir)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
