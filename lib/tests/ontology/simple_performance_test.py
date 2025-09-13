#!/usr/bin/env python3
"""
Simple performance test for the ontology package that works without optional dependencies.

This is a minimal version that only requires the core a1facts dependencies.
"""

import time
import os
import sys
import statistics
from typing import List, Callable

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from a1facts.ontology.knowledge_ontology import KnowledgeOntology
    from a1facts.ontology.entity_class import EntityClass
    from a1facts.ontology.relationship_class import RelationshipClass
    from a1facts.ontology.property import Property
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"Error importing a1facts modules: {e}")
    print("Make sure you have installed the required dependencies:")
    print("pip install PyYAML")
    IMPORTS_SUCCESSFUL = False


def run_simple_performance_test(test_func: Callable, test_name: str, iterations: int = 10) -> dict:
    """Run a simple performance test without memory monitoring."""
    durations = []
    
    try:
        # Warmup
        for _ in range(2):
            try:
                test_func()
            except Exception:
                pass
        
        # Actual test
        for _ in range(iterations):
            start_time = time.perf_counter()
            test_func()
            end_time = time.perf_counter()
            durations.append(end_time - start_time)
        
        return {
            'test_name': test_name,
            'success': True,
            'iterations': len(durations),
            'avg_duration': statistics.mean(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'std_deviation': statistics.stdev(durations) if len(durations) > 1 else 0.0,
            'error_message': None
        }
    except Exception as e:
        return {
            'test_name': test_name,
            'success': False,
            'iterations': 0,
            'avg_duration': 0.0,
            'min_duration': 0.0,
            'max_duration': 0.0,
            'std_deviation': 0.0,
            'error_message': str(e)
        }


def test_ontology_loading():
    """Test ontology loading performance."""
    ontology_file = os.path.join(os.path.dirname(__file__), 'company.yaml')
    if not os.path.exists(ontology_file):
        raise FileNotFoundError(f"Ontology file not found: {ontology_file}")
    
    ontology = KnowledgeOntology(ontology_file)
    return ontology


def test_entity_operations():
    """Test entity class operations."""
    ontology_file = os.path.join(os.path.dirname(__file__), 'company.yaml')
    ontology = KnowledgeOntology(ontology_file)
    
    # Test entity finding
    for entity_class in ontology.entity_classes:
        found = ontology.find_entity_class(entity_class.entity_class_name)
        assert found is not None
    
    # Test property access
    for entity_class in ontology.entity_classes:
        for prop in entity_class.properties:
            _ = prop.property_name
            _ = prop.type
            _ = prop.description
            _ = prop.primary_key


def test_relationship_operations():
    """Test relationship class operations."""
    ontology_file = os.path.join(os.path.dirname(__file__), 'company.yaml')
    ontology = KnowledgeOntology(ontology_file)
    
    # Test relationship property access
    for rel_class in ontology.relationship_classes:
        _ = rel_class.relationship_name
        _ = rel_class.domain_entity_class
        _ = rel_class.range_entity_class
        _ = rel_class.description
        _ = rel_class.symmetric


def test_tool_generation():
    """Test tool generation performance."""
    ontology_file = os.path.join(os.path.dirname(__file__), 'company.yaml')
    ontology = KnowledgeOntology(ontology_file)
    
    # Dummy functions
    def dummy_func(*args, **kwargs):
        return "dummy_result"
    
    # Generate tools
    entity_tools = ontology.get_tools_add_or_update_entity(dummy_func)
    rel_tools = ontology.get_tools_add_or_update_relationship(dummy_func)
    
    return entity_tools + rel_tools


def run_all_simple_tests():
    """Run all simple performance tests."""
    if not IMPORTS_SUCCESSFUL:
        print("Cannot run tests due to import errors.")
        return []
    
    print("Running simple ontology performance tests...")
    print("=" * 50)
    
    tests = [
        (test_ontology_loading, "Ontology Loading", 20),
        (test_entity_operations, "Entity Operations", 50),
        (test_relationship_operations, "Relationship Operations", 30),
        (test_tool_generation, "Tool Generation", 20),
    ]
    
    results = []
    
    for test_func, test_name, iterations in tests:
        print(f"Running {test_name}...")
        result = run_simple_performance_test(test_func, test_name, iterations)
        results.append(result)
        
        if result['success']:
            print(f"✓ {test_name}: {result['avg_duration']:.4f}s (±{result['std_deviation']:.4f}s)")
        else:
            print(f"✗ {test_name}: {result['error_message']}")
    
    return results


def print_summary(results: List[dict]):
    """Print a summary of test results."""
    print("\n" + "=" * 50)
    print("PERFORMANCE TEST SUMMARY")
    print("=" * 50)
    
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"Total tests: {len(results)}")
    print(f"Successful: {len(successful_tests)}")
    print(f"Failed: {len(failed_tests)}")
    
    if successful_tests:
        avg_durations = [r['avg_duration'] for r in successful_tests]
        print(f"\nAverage duration: {statistics.mean(avg_durations):.4f}s")
        print(f"Fastest test: {min(avg_durations):.4f}s")
        print(f"Slowest test: {max(avg_durations):.4f}s")
        
        print("\nDetailed Results:")
        print("-" * 30)
        for result in successful_tests:
            print(f"{result['test_name']}: {result['avg_duration']:.4f}s")
    
    if failed_tests:
        print("\nFailed Tests:")
        print("-" * 30)
        for result in failed_tests:
            print(f"{result['test_name']}: {result['error_message']}")


def main():
    """Main function."""
    print("Simple Ontology Performance Test")
    print("================================")
    
    # Check if ontology file exists
    ontology_file = os.path.join(os.path.dirname(__file__), 'company.yaml')
    if not os.path.exists(ontology_file):
        print(f"Error: Ontology file not found: {ontology_file}")
        print("Make sure you're running this from the tests/ontology directory")
        sys.exit(1)
    
    # Run tests
    results = run_all_simple_tests()
    
    # Print summary
    print_summary(results)
    
    # Exit with error code if any tests failed
    failed_tests = [r for r in results if not r['success']]
    if failed_tests:
        print(f"\n⚠️  {len(failed_tests)} test(s) failed!")
        sys.exit(1)
    else:
        print("\n✓ All tests passed!")


if __name__ == "__main__":
    main()
