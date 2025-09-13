#!/usr/bin/env python3
"""
Example script demonstrating how to use the ontology performance testing framework.

This script shows different ways to run performance tests and interpret results.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from test_ontology_performance import OntologyPerformanceTester


def example_basic_usage():
    """Example of basic performance testing usage."""
    print("=== Basic Performance Testing Example ===")
    
    # Initialize the tester with default ontology file
    tester = OntologyPerformanceTester()
    
    # Run just the ontology loading tests
    print("Running ontology loading performance tests...")
    results = tester.test_ontology_loading_performance()
    
    # Print results
    for result in results:
        if result.success:
            print(f"✓ {result.test_name}: {result.avg_duration:.4f}s")
        else:
            print(f"✗ {result.test_name}: {result.error_message}")
    
    tester.cleanup()


def example_custom_ontology():
    """Example of testing with a custom ontology file."""
    print("\n=== Custom Ontology Testing Example ===")
    
    # Create a custom ontology file path
    custom_ontology = os.path.join(os.path.dirname(__file__), 'company.yaml')
    
    if not os.path.exists(custom_ontology):
        print(f"Custom ontology file not found: {custom_ontology}")
        return
    
    # Initialize tester with custom ontology
    tester = OntologyPerformanceTester(custom_ontology)
    
    # Run entity operations tests
    print("Running entity operations performance tests...")
    results = tester.test_entity_operations_performance()
    
    # Print detailed results
    for result in results:
        print(f"\n{result.test_name}:")
        if result.success:
            print(f"  Average duration: {result.avg_duration:.4f}s")
            print(f"  Memory usage: {result.memory_usage:.2f} MB")
            print(f"  Iterations: {result.iterations}")
            print(f"  Min/Max: {result.min_duration:.4f}s / {result.max_duration:.4f}s")
        else:
            print(f"  Error: {result.error_message}")
    
    tester.cleanup()


def example_comprehensive_testing():
    """Example of running comprehensive performance tests."""
    print("\n=== Comprehensive Testing Example ===")
    
    # Initialize tester
    tester = OntologyPerformanceTester()
    
    # Run all tests
    print("Running comprehensive performance test suite...")
    results = tester.run_all_tests()
    
    # Generate and display report
    report = tester.generate_report()
    print("\n" + report)
    
    # Save report to file
    report_file = "example_performance_report.txt"
    tester.generate_report(report_file)
    print(f"\nReport saved to: {report_file}")
    
    tester.cleanup()


def example_large_ontology_testing():
    """Example of testing with large ontologies."""
    print("\n=== Large Ontology Testing Example ===")
    
    # Initialize tester
    tester = OntologyPerformanceTester()
    
    # Create a large ontology for testing
    print("Creating large ontology for testing...")
    large_ontology_file = tester.create_large_ontology(num_entities=100, num_relationships=50)
    print(f"Created large ontology: {large_ontology_file}")
    
    # Test with large ontology
    large_tester = OntologyPerformanceTester(large_ontology_file)
    
    # Run loading performance test
    print("Testing large ontology loading performance...")
    results = large_tester.test_ontology_loading_performance()
    
    for result in results:
        if "Large" in result.test_name:
            print(f"{result.test_name}: {result.avg_duration:.4f}s, {result.memory_usage:.2f} MB")
    
    # Cleanup
    large_tester.cleanup()
    tester.cleanup()


def example_performance_comparison():
    """Example of comparing performance between different configurations."""
    print("\n=== Performance Comparison Example ===")
    
    # Test with standard ontology
    print("Testing standard ontology...")
    standard_tester = OntologyPerformanceTester()
    standard_results = standard_tester.test_ontology_loading_performance()
    standard_tester.cleanup()
    
    # Test with large ontology
    print("Testing large ontology...")
    large_tester = OntologyPerformanceTester()
    large_ontology_file = large_tester.create_large_ontology(50, 25)
    large_tester.ontology_file = large_ontology_file
    large_results = large_tester.test_ontology_loading_performance()
    large_tester.cleanup()
    
    # Compare results
    print("\nPerformance Comparison:")
    print("=" * 50)
    
    standard_loading = next((r for r in standard_results if "Standard" in r.test_name), None)
    large_loading = next((r for r in large_results if "Large" in r.test_name), None)
    
    if standard_loading and large_loading:
        print(f"Standard ontology loading: {standard_loading.avg_duration:.4f}s")
        print(f"Large ontology loading: {large_loading.avg_duration:.4f}s")
        print(f"Performance ratio: {large_loading.avg_duration / standard_loading.avg_duration:.2f}x")
        print(f"Memory ratio: {large_loading.memory_usage / standard_loading.memory_usage:.2f}x")


def main():
    """Run all examples."""
    print("Ontology Performance Testing Examples")
    print("=" * 50)
    
    try:
        example_basic_usage()
        example_custom_ontology()
        example_large_ontology_testing()
        example_performance_comparison()
        example_comprehensive_testing()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
