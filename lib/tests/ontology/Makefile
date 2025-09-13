# Makefile for ontology performance testing

.PHONY: help install test test-quick test-full test-examples clean

# Default target
help:
	@echo "Ontology Performance Testing Makefile"
	@echo "====================================="
	@echo ""
	@echo "Available targets:"
	@echo "  install      - Install performance testing dependencies"
	@echo "  test         - Run standard performance tests"
	@echo "  test-quick   - Run quick performance tests (fewer iterations)"
	@echo "  test-full    - Run comprehensive performance tests"
	@echo "  test-examples- Run example usage scripts"
	@echo "  clean        - Clean up temporary files and reports"
	@echo ""
	@echo "Usage examples:"
	@echo "  make install && make test"
	@echo "  make test-quick"
	@echo "  make test-full > performance_report.txt"

# Install dependencies
install:
	@echo "Installing performance testing dependencies..."
	pip install -r requirements_performance.txt

# Run standard performance tests
test:
	@echo "Running standard performance tests..."
	python run_performance_tests.py

# Run quick performance tests
test-quick:
	@echo "Running quick performance tests..."
	python run_performance_tests.py --quick

# Run comprehensive performance tests
test-full:
	@echo "Running comprehensive performance tests..."
	python run_performance_tests.py --iterations 20 --output full_performance_report.txt

# Run example usage scripts
test-examples:
	@echo "Running performance testing examples..."
	python example_performance_usage.py

# Clean up temporary files
clean:
	@echo "Cleaning up temporary files..."
	rm -f *.txt
	rm -f *.yaml
	rm -f *.pickle
	@echo "Cleanup complete"

# Run tests with pytest
test-pytest:
	@echo "Running performance tests with pytest..."
	python run_performance_tests.py --pytest

# Run tests with custom ontology file
test-custom:
	@echo "Running tests with custom ontology file..."
	python run_performance_tests.py --ontology-file company.yaml --output custom_report.txt
