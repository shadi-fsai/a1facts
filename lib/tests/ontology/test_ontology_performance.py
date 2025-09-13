"""
Performance testing script for the a1facts ontology package.

This script provides comprehensive performance testing for:
- Ontology loading and initialization
- Entity class operations
- Relationship class operations
- Tool generation
- Memory usage and scalability
- Concurrent operations

Usage:
    python -m pytest tests/ontology/test_ontology_performance.py -v
    python tests/ontology/test_ontology_performance.py  # Run standalone
"""

import time
import threading
import concurrent.futures
import statistics
import json
import os
import sys
import tempfile
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from contextlib import contextmanager

# Optional imports
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("Warning: PyYAML not available. Some features will be disabled.")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available. Memory monitoring will be disabled.")

try:
    import memory_profiler
    MEMORY_PROFILER_AVAILABLE = True
except ImportError:
    MEMORY_PROFILER_AVAILABLE = False
    print("Warning: memory_profiler not available. Advanced memory profiling will be disabled.")

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from a1facts.ontology.knowledge_ontology import KnowledgeOntology
from a1facts.ontology.entity_class import EntityClass
from a1facts.ontology.relationship_class import RelationshipClass
from a1facts.ontology.property import Property


@dataclass
class PerformanceResult:
    """Data class to store performance test results."""
    test_name: str
    duration: float
    memory_usage: float
    iterations: int
    avg_duration: float
    min_duration: float
    max_duration: float
    std_deviation: float
    success: bool
    error_message: str = ""


class OntologyPerformanceTester:
    """Main class for ontology performance testing."""
    
    def __init__(self, ontology_file: str = None):
        """Initialize the performance tester."""
        self.ontology_file = ontology_file or os.path.join(
            os.path.dirname(__file__), 'company.yaml'
        )
        self.results: List[PerformanceResult] = []
        self.large_ontology_file = None
        
    def create_large_ontology(self, num_entities: int = 100, num_relationships: int = 50) -> str:
        """Create a large ontology file for scalability testing."""
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for creating large ontologies")
        
        ontology_data = {
            'world': {
                'name': f'Large Test Ontology ({num_entities} entities)',
                'description': 'Performance testing ontology with many entities and relationships'
            },
            'entity_classes': {},
            'relationships': {}
        }
        
        # Create entity classes
        for i in range(num_entities):
            entity_name = f'Entity_{i}'
            ontology_data['entity_classes'][entity_name] = {
                'description': f'Test entity class {i}',
                'properties': [
                    {
                        'name': 'id',
                        'type': 'str',
                        'primary_key': True,
                        'description': f'Primary key for {entity_name}'
                    },
                    {
                        'name': 'name',
                        'type': 'str',
                        'description': f'Name of {entity_name}'
                    },
                    {
                        'name': 'value',
                        'type': 'float',
                        'description': f'Numeric value for {entity_name}'
                    }
                ]
            }
        
        # Create relationships
        for i in range(num_relationships):
            rel_name = f'relates_to_{i}'
            domain_idx = i % num_entities
            range_idx = (i + 1) % num_entities
            ontology_data['relationships'][rel_name] = {
                'domain': f'Entity_{domain_idx}',
                'range': f'Entity_{range_idx}',
                'description': f'Test relationship {i}',
                'properties': []
            }
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(ontology_data, f)
            self.large_ontology_file = f.name
        
        return self.large_ontology_file
    
    @contextmanager
    def measure_memory(self):
        """Context manager to measure memory usage."""
        if PSUTIL_AVAILABLE:
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            yield
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            return final_memory - initial_memory
        else:
            # Return 0 if psutil is not available
            yield
            return 0.0
    
    def run_performance_test(self, test_func: Callable, test_name: str, 
                           iterations: int = 10, warmup_iterations: int = 2) -> PerformanceResult:
        """Run a performance test with multiple iterations."""
        durations = []
        memory_usage = 0.0
        success = True
        error_message = ""
        
        try:
            # Warmup iterations
            for _ in range(warmup_iterations):
                try:
                    test_func()
                except Exception as e:
                    print(f"Warning: Warmup iteration failed: {e}")
            
            # Actual test iterations
            for i in range(iterations):
                start_time = time.perf_counter()
                with self.measure_memory() as mem_delta:
                    test_func()
                end_time = time.perf_counter()
                
                duration = end_time - start_time
                durations.append(duration)
                if mem_delta is not None:
                    memory_usage += mem_delta
            
            memory_usage /= iterations  # Average memory usage
            
        except Exception as e:
            success = False
            error_message = str(e)
            durations = [0.0]
        
        return PerformanceResult(
            test_name=test_name,
            duration=sum(durations),
            memory_usage=memory_usage,
            iterations=len(durations),
            avg_duration=statistics.mean(durations),
            min_duration=min(durations),
            max_duration=max(durations),
            std_deviation=statistics.stdev(durations) if len(durations) > 1 else 0.0,
            success=success,
            error_message=error_message
        )
    
    def test_ontology_loading_performance(self) -> List[PerformanceResult]:
        """Test ontology loading performance."""
        results = []
        
        # Test standard ontology loading
        def load_standard_ontology():
            ontology = KnowledgeOntology(self.ontology_file)
            return ontology
        
        result = self.run_performance_test(
            load_standard_ontology, 
            "Standard Ontology Loading", 
            iterations=20
        )
        results.append(result)
        
        # Test large ontology loading
        if not self.large_ontology_file:
            self.create_large_ontology(50, 25)
        
        def load_large_ontology():
            ontology = KnowledgeOntology(self.large_ontology_file)
            return ontology
        
        result = self.run_performance_test(
            load_large_ontology,
            "Large Ontology Loading (50 entities, 25 relationships)",
            iterations=10
        )
        results.append(result)
        
        # Test very large ontology loading
        very_large_file = self.create_large_ontology(200, 100)
        
        def load_very_large_ontology():
            ontology = KnowledgeOntology(very_large_file)
            return ontology
        
        result = self.run_performance_test(
            load_very_large_ontology,
            "Very Large Ontology Loading (200 entities, 100 relationships)",
            iterations=5
        )
        results.append(result)
        
        return results
    
    def test_entity_operations_performance(self) -> List[PerformanceResult]:
        """Test entity class operations performance."""
        results = []
        ontology = KnowledgeOntology(self.ontology_file)
        
        # Test entity class finding
        def find_entity_classes():
            for entity_class in ontology.entity_classes:
                found = ontology.find_entity_class(entity_class.entity_class_name)
                assert found is not None
        
        result = self.run_performance_test(
            find_entity_classes,
            "Entity Class Finding",
            iterations=100
        )
        results.append(result)
        
        # Test property access
        def access_entity_properties():
            for entity_class in ontology.entity_classes:
                for prop in entity_class.properties:
                    _ = prop.property_name
                    _ = prop.type
                    _ = prop.description
                    _ = prop.primary_key
        
        result = self.run_performance_test(
            access_entity_properties,
            "Entity Property Access",
            iterations=50
        )
        results.append(result)
        
        # Test string representation
        def entity_string_representation():
            for entity_class in ontology.entity_classes:
                _ = str(entity_class)
        
        result = self.run_performance_test(
            entity_string_representation,
            "Entity String Representation",
            iterations=20
        )
        results.append(result)
        
        return results
    
    def test_relationship_operations_performance(self) -> List[PerformanceResult]:
        """Test relationship class operations performance."""
        results = []
        ontology = KnowledgeOntology(self.ontology_file)
        
        # Test relationship property access
        def access_relationship_properties():
            for rel_class in ontology.relationship_classes:
                _ = rel_class.relationship_name
                _ = rel_class.domain_entity_class
                _ = rel_class.range_entity_class
                _ = rel_class.description
                _ = rel_class.symmetric
                for prop in rel_class.properties:
                    _ = prop.property_name
                    _ = prop.type
        
        result = self.run_performance_test(
            access_relationship_properties,
            "Relationship Property Access",
            iterations=50
        )
        results.append(result)
        
        # Test relationship validation
        def validate_relationships():
            for rel_class in ontology.relationship_classes:
                try:
                    rel_class._validate_properties({})
                except Exception:
                    pass  # Expected for some relationships
        
        result = self.run_performance_test(
            validate_relationships,
            "Relationship Validation",
            iterations=30
        )
        results.append(result)
        
        # Test string representation
        def relationship_string_representation():
            for rel_class in ontology.relationship_classes:
                _ = str(rel_class)
        
        result = self.run_performance_test(
            relationship_string_representation,
            "Relationship String Representation",
            iterations=20
        )
        results.append(result)
        
        return results
    
    def test_tool_generation_performance(self) -> List[PerformanceResult]:
        """Test tool generation performance."""
        results = []
        ontology = KnowledgeOntology(self.ontology_file)
        
        # Dummy functions for tool creation
        def dummy_add_entity(*args, **kwargs):
            return "dummy_result"
        
        def dummy_get_entity(*args, **kwargs):
            return "dummy_result"
        
        def dummy_add_relationship(*args, **kwargs):
            return "dummy_result"
        
        def dummy_get_relationship(*args, **kwargs):
            return "dummy_result"
        
        # Test entity tool generation
        def generate_entity_tools():
            tools = ontology.get_tools_add_or_update_entity(dummy_add_entity)
            tools.extend(ontology.get_tools_get_entity_properties(dummy_get_entity))
            tools.extend(ontology.get_tools_get_all_entity(dummy_get_entity))
            return tools
        
        result = self.run_performance_test(
            generate_entity_tools,
            "Entity Tool Generation",
            iterations=20
        )
        results.append(result)
        
        # Test relationship tool generation
        def generate_relationship_tools():
            tools = ontology.get_tools_add_or_update_relationship(dummy_add_relationship)
            tools.extend(ontology.get_tools_get_relationship_properties(dummy_get_relationship))
            tools.extend(ontology.get_tools_get_relationship_entities(dummy_get_relationship))
            return tools
        
        result = self.run_performance_test(
            generate_relationship_tools,
            "Relationship Tool Generation",
            iterations=20
        )
        results.append(result)
        
        # Test combined tool generation
        def generate_all_tools():
            entity_tools = ontology.get_tools_add_or_update_entity_and_relationship(
                dummy_add_entity, dummy_add_relationship
            )
            get_tools = ontology.get_tools_get_entity_and_relationship(
                dummy_get_entity, dummy_get_entity, dummy_get_relationship, dummy_get_relationship
            )
            return entity_tools + get_tools
        
        result = self.run_performance_test(
            generate_all_tools,
            "Combined Tool Generation",
            iterations=15
        )
        results.append(result)
        
        return results
    
    def test_concurrent_operations_performance(self) -> List[PerformanceResult]:
        """Test concurrent operations performance."""
        results = []
        ontology = KnowledgeOntology(self.ontology_file)
        
        def concurrent_entity_finding():
            def find_entities():
                for entity_class in ontology.entity_classes:
                    found = ontology.find_entity_class(entity_class.entity_class_name)
                    assert found is not None
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(find_entities) for _ in range(10)]
                concurrent.futures.wait(futures)
        
        result = self.run_performance_test(
            concurrent_entity_finding,
            "Concurrent Entity Finding (4 threads, 10 tasks)",
            iterations=5
        )
        results.append(result)
        
        def concurrent_tool_generation():
            def generate_tools():
                dummy_func = lambda *args, **kwargs: "dummy"
                return ontology.get_tools_add_or_update_entity(dummy_func)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(generate_tools) for _ in range(8)]
                concurrent.futures.wait(futures)
        
        result = self.run_performance_test(
            concurrent_tool_generation,
            "Concurrent Tool Generation (3 threads, 8 tasks)",
            iterations=5
        )
        results.append(result)
        
        return results
    
    def test_memory_usage_performance(self) -> List[PerformanceResult]:
        """Test memory usage patterns."""
        results = []
        
        # Test memory usage during ontology creation
        def create_multiple_ontologies():
            ontologies = []
            for _ in range(10):
                ontology = KnowledgeOntology(self.ontology_file)
                ontologies.append(ontology)
            return ontologies
        
        result = self.run_performance_test(
            create_multiple_ontologies,
            "Multiple Ontology Creation Memory Usage",
            iterations=3
        )
        results.append(result)
        
        # Test memory usage during large ontology operations
        if not self.large_ontology_file:
            self.create_large_ontology(100, 50)
        
        def large_ontology_operations():
            ontology = KnowledgeOntology(self.large_ontology_file)
            # Perform various operations
            for entity_class in ontology.entity_classes:
                _ = str(entity_class)
            for rel_class in ontology.relationship_classes:
                _ = str(rel_class)
            return ontology
        
        result = self.run_performance_test(
            large_ontology_operations,
            "Large Ontology Operations Memory Usage",
            iterations=3
        )
        results.append(result)
        
        return results
    
    def run_all_tests(self) -> List[PerformanceResult]:
        """Run all performance tests."""
        print("Starting comprehensive ontology performance testing...")
        
        all_results = []
        
        # Run all test suites
        test_suites = [
            ("Ontology Loading", self.test_ontology_loading_performance),
            ("Entity Operations", self.test_entity_operations_performance),
            ("Relationship Operations", self.test_relationship_operations_performance),
            ("Tool Generation", self.test_tool_generation_performance),
            ("Concurrent Operations", self.test_concurrent_operations_performance),
            ("Memory Usage", self.test_memory_usage_performance),
        ]
        
        for suite_name, test_func in test_suites:
            print(f"\nRunning {suite_name} tests...")
            try:
                results = test_func()
                all_results.extend(results)
                print(f"✓ {suite_name} tests completed")
            except Exception as e:
                print(f"✗ {suite_name} tests failed: {e}")
        
        self.results = all_results
        return all_results
    
    def generate_report(self, output_file: str = None) -> str:
        """Generate a performance test report."""
        if not self.results:
            return "No test results available."
        
        report = []
        report.append("=" * 80)
        report.append("A1FACTS ONTOLOGY PERFORMANCE TEST REPORT")
        report.append("=" * 80)
        report.append(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total tests: {len(self.results)}")
        report.append("")
        
        # Summary statistics
        successful_tests = [r for r in self.results if r.success]
        failed_tests = [r for r in self.results if not r.success]
        
        report.append("SUMMARY")
        report.append("-" * 40)
        report.append(f"Successful tests: {len(successful_tests)}")
        report.append(f"Failed tests: {len(failed_tests)}")
        report.append("")
        
        if successful_tests:
            avg_durations = [r.avg_duration for r in successful_tests]
            report.append(f"Average test duration: {statistics.mean(avg_durations):.4f}s")
            report.append(f"Fastest test: {min(avg_durations):.4f}s")
            report.append(f"Slowest test: {max(avg_durations):.4f}s")
            report.append("")
        
        # Detailed results
        report.append("DETAILED RESULTS")
        report.append("-" * 40)
        
        for result in self.results:
            status = "✓ PASS" if result.success else "✗ FAIL"
            report.append(f"{status} {result.test_name}")
            if result.success:
                report.append(f"  Duration: {result.avg_duration:.4f}s (±{result.std_deviation:.4f}s)")
                report.append(f"  Memory: {result.memory_usage:.2f} MB")
                report.append(f"  Iterations: {result.iterations}")
                report.append(f"  Min/Max: {result.min_duration:.4f}s / {result.max_duration:.4f}s")
            else:
                report.append(f"  Error: {result.error_message}")
            report.append("")
        
        # Performance recommendations
        report.append("PERFORMANCE RECOMMENDATIONS")
        report.append("-" * 40)
        
        slow_tests = [r for r in successful_tests if r.avg_duration > 1.0]
        if slow_tests:
            report.append("⚠️  Slow tests (>1s):")
            for test in slow_tests:
                report.append(f"  - {test.test_name}: {test.avg_duration:.4f}s")
            report.append("")
        
        high_memory_tests = [r for r in successful_tests if r.memory_usage > 50.0]
        if high_memory_tests:
            report.append("⚠️  High memory usage tests (>50MB):")
            for test in high_memory_tests:
                report.append(f"  - {test.test_name}: {test.memory_usage:.2f} MB")
            report.append("")
        
        if not slow_tests and not high_memory_tests:
            report.append("✓ All tests show good performance characteristics")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            print(f"Report saved to: {output_file}")
        
        return report_text
    
    def cleanup(self):
        """Clean up temporary files."""
        if self.large_ontology_file and os.path.exists(self.large_ontology_file):
            os.unlink(self.large_ontology_file)


def main():
    """Main function to run performance tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run ontology performance tests')
    parser.add_argument('--ontology-file', help='Path to ontology YAML file')
    parser.add_argument('--output', help='Output file for the report')
    parser.add_argument('--iterations', type=int, default=10, help='Number of iterations per test')
    
    args = parser.parse_args()
    
    # Initialize tester
    tester = OntologyPerformanceTester(args.ontology_file)
    
    try:
        # Run all tests
        results = tester.run_all_tests()
        
        # Generate and display report
        report = tester.generate_report(args.output)
        print("\n" + report)
        
        # Exit with error code if any tests failed
        failed_tests = [r for r in results if not r.success]
        if failed_tests:
            print(f"\n⚠️  {len(failed_tests)} test(s) failed!")
            sys.exit(1)
        else:
            print("\n✓ All tests passed!")
            
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()
