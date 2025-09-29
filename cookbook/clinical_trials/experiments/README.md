# Clinical Trials Agent Evaluation Suite

This evaluation suite uses LLM-as-a-judge to assess the accuracy and tool selection capabilities of the clinical trials knowledge agent.

## Overview

The suite evaluates the agent on two key dimensions:

1. **Tool Selection Accuracy**: Does the agent call the correct tools in the right sequence?
2. **Response Quality**: How accurate, complete, and well-structured are the responses?

## Test Data

Tests are based on 30 complex evaluation queries from `complex_evaluation_queries.md`, each with:
- A multi-step clinical trials query
- Expected tool call sequence
- Predicted reasoning chain

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure you have OpenAI API key in `.env`:
```
OPENAI_API_KEY=your_key_here
```

3. Make sure MCP servers are running (if testing MCP tools):
```bash
# In separate terminals
cd ../mcp_knowledge_source/healthcare-mcp-server && node server/index.js
cd ../mcp_knowledge_source/dgidb-mcp && python -m dgidb_mcp
cd ../mcp_knowledge_source/biorxiv-mcp && python -m biorxiv_mcp
```

## Quick Demo

Run the evaluation demo to see how LLM-as-judge works:
```bash
python demo_evaluation.py
```

This shows sample evaluations for tool selection and response quality.

## Running Tests

### Run all evaluation tests:
```bash
pytest test_agent_evaluation.py -v
```

### Run specific test categories:
```bash
# Test only tool selection
pytest test_agent_evaluation.py::test_query_tool_selection -v

# Test only response quality
pytest test_agent_evaluation.py::test_response_quality -v

# Test query parsing
pytest test_agent_evaluation.py::test_parse_queries -v

# Run sample tests (first 5 queries)
pytest test_agent_evaluation.py -k "sample" -v
```

### Generate evaluation report:
```bash
pytest test_agent_evaluation.py --tb=short --junitxml=results.xml
```

## Configuration

The `config.yaml` file controls evaluation settings:
- LLM judge model and thresholds
- Test parameters (sample size, timeouts)
- Quality thresholds for pass/fail criteria

## Evaluation Metrics

### Tool Selection (1-5 scale)
- **5**: All expected tools called in correct order
- **4**: All expected tools called but wrong order
- **3**: Most expected tools called
- **2**: Some expected tools called
- **1**: Wrong or no tools called

### Response Quality (1-5 scale)
- **5**: Highly accurate, comprehensive, well-structured, cites sources
- **4**: Mostly accurate with good structure
- **3**: Partially accurate but missing some information
- **2**: Inaccurate or incomplete
- **1**: Irrelevant or incorrect

## Test Structure

```
experiments/
├── test_agent_evaluation.py    # Main test suite
├── demo_evaluation.py          # Quick evaluation demo
├── config.yaml                 # Evaluation configuration
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## LLM Judge

The evaluation uses GPT-4o-mini as the judge to:
- Assess tool selection accuracy
- Evaluate response completeness and accuracy
- Provide detailed explanations for ratings

## Expected Results

Each test query should achieve:
- Tool selection rating ≥ 3
- Response quality rating ≥ 3

Tests will fail if ratings fall below these thresholds, indicating areas for improvement in the agent's tool selection or response generation.

## Tool Detection

The evaluation automatically detects tool usage from agent responses by looking for:
- API source mentions (ClinicalTrials.gov, FDA, PubMed, etc.)
- Tool-specific keywords (BMI, ICD-10, DICOM, etc.)
- Data source citations

This provides automated evaluation of whether the agent used the correct tools for each query.