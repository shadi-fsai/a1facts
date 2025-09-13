# Ontology Performance Testing

This directory contains comprehensive performance testing tools for the a1facts ontology package.

## Files

- `test_ontology_performance.py` - Main performance testing script
- `run_performance_tests.py` - Simple runner script with various options
- `requirements_performance.txt` - Dependencies for performance testing
- `README_performance.md` - This documentation file

## Quick Start

### 1. Install Dependencies

```bash
# Install performance testing dependencies
python run_performance_tests.py --install-deps

# Or manually:
pip install -r requirements_performance.txt
```

### 2. Run Performance Tests

```bash
# Run all performance tests (recommended)
python run_performance_tests.py

# Run quick tests (fewer iterations)
python run_performance_tests.py --quick

# Run with custom ontology file
python run_performance_tests.py --ontology-file /path/to/your/ontology.yaml

# Run with pytest integration
python run_performance_tests.py --pytest

# Save report to file
python run_performance_tests.py --output performance_report.txt
```

### 3. Run Tests Directly

```bash
# Run the main test script directly
python test_ontology_performance.py

# With custom options
python test_ontology_performance.py --ontology-file company.yaml --output report.txt --iterations 20
```

## Test Categories

The performance testing suite includes the following test categories:

### 1. Ontology Loading Performance
- Standard ontology loading (company.yaml)
- Large ontology loading (50 entities, 25 relationships)
- Very large ontology loading (200 entities, 100 relationships)

### 2. Entity Operations Performance
- Entity class finding operations
- Property access operations
- String representation generation

### 3. Relationship Operations Performance
- Relationship property access
- Relationship validation
- String representation generation

### 4. Tool Generation Performance
- Entity tool generation
- Relationship tool generation
- Combined tool generation

### 5. Concurrent Operations Performance
- Multi-threaded entity finding
- Multi-threaded tool generation

### 6. Memory Usage Performance
- Memory usage during ontology creation
- Memory usage during large ontology operations

## Performance Metrics

Each test measures:

- **Duration**: Execution time in seconds
- **Memory Usage**: Memory consumption in MB
- **Iterations**: Number of test iterations
- **Statistics**: Min, max, average, and standard deviation
- **Success Rate**: Whether tests pass or fail

## Report Format

The performance test generates a comprehensive report including:

- Summary statistics
- Detailed results for each test
- Performance recommendations
- Slow test identification (>1s)
- High memory usage identification (>50MB)

### Sample Report Output

```
================================================================================
A1FACTS ONTOLOGY PERFORMANCE TEST REPORT
================================================================================
Generated at: 2024-01-15 14:30:25
Total tests: 12

SUMMARY
----------------------------------------
Successful tests: 12
Failed tests: 0

Average test duration: 0.0234s
Fastest test: 0.0012s
Slowest test: 0.1567s

DETAILED RESULTS
----------------------------------------
✓ PASS Standard Ontology Loading
  Duration: 0.0156s (±0.0023s)
  Memory: 2.34 MB
  Iterations: 20
  Min/Max: 0.0123s / 0.0198s

✓ PASS Entity Class Finding
  Duration: 0.0034s (±0.0008s)
  Memory: 0.12 MB
  Iterations: 100
  Min/Max: 0.0021s / 0.0045s

...

PERFORMANCE RECOMMENDATIONS
----------------------------------------
✓ All tests show good performance characteristics
```

## Configuration Options

### Command Line Options

- `--ontology-file`: Specify custom ontology YAML file
- `--output`: Save report to file
- `--iterations`: Number of test iterations (default: 10)
- `--quick`: Run with fewer iterations for quick testing
- `--pytest`: Use pytest integration
- `--install-deps`: Install required dependencies

### Test Parameters

- **Warmup Iterations**: 2 (configurable in code)
- **Default Iterations**: 10 (configurable via command line)
- **Quick Mode Iterations**: 3
- **Concurrent Threads**: 3-4 (depending on test)

## Integration with CI/CD

The performance tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Performance Tests
  run: |
    cd tests/ontology
    python run_performance_tests.py --quick --output performance_report.txt
    
- name: Check Performance Thresholds
  run: |
    # Add custom logic to check if performance meets requirements
    python check_performance_thresholds.py performance_report.txt
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running from the correct directory and dependencies are installed
2. **Memory Issues**: For very large ontologies, consider increasing system memory or reducing test iterations
3. **Slow Tests**: Some tests may be slow on older hardware; use `--quick` mode for faster feedback

### Performance Tips

1. **Warmup**: Tests include warmup iterations to get more accurate measurements
2. **Multiple Iterations**: Tests run multiple iterations to get statistical significance
3. **Memory Profiling**: Memory usage is measured for each test
4. **Concurrent Testing**: Tests include concurrent operations to identify thread safety issues

## Extending the Tests

To add new performance tests:

1. Add a new test method to `OntologyPerformanceTester` class
2. Follow the pattern of existing tests
3. Use `self.run_performance_test()` for consistent measurement
4. Add the new test to `run_all_tests()` method
5. Update this documentation

## Dependencies

- `psutil`: System and process utilities for memory monitoring
- `memory-profiler`: Memory usage profiling
- `pytest`: Testing framework (optional)
- `pytest-benchmark`: Benchmarking plugin for pytest (optional)

## License

This performance testing suite is part of the a1facts project and follows the same license terms.
