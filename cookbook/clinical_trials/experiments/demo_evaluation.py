#!/usr/bin/env python3
"""
Quick evaluation demo for the clinical trials agent.
Shows how LLM-as-judge evaluates tool selection and response quality.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent / 'lib' / 'src'))

from experiments.test_agent_evaluation import QueryEvaluator, extract_tool_calls_from_response
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from textwrap import dedent

load_dotenv()

async def demo_evaluation():
    """Demonstrate LLM-as-judge evaluation."""

    # Sample query and expected tools
    query = "Find recruiting clinical trials for metastatic melanoma"
    expected_tools = ["ClinicalTrialsTool.searchTrials"]
    mock_response = """
    📡 API DATA SOURCE: ClinicalTrials.gov API
    [SEARCH QUERY]: metastatic melanoma recruiting
    [RESULTS]: Found 15 recruiting trials for metastatic melanoma including NCT04500002, NCT03470922, etc.
    ⏰ RETRIEVED: October 1, 2024
    """

    # Extract actual tools from response
    actual_tools = extract_tool_calls_from_response(mock_response)

    print("🔍 CLINICAL TRIALS AGENT EVALUATION DEMO")
    print("=" * 60)
    print(f"Query: {query}")
    print(f"Expected tools: {expected_tools}")
    print(f"Detected tools: {actual_tools}")
    print()

    # Create evaluator
    evaluator = QueryEvaluator()

    # Evaluate tool selection
    print("📊 TOOL SELECTION EVALUATION:")
    tool_eval = await evaluator.evaluate_tool_selection(query, expected_tools, actual_tools)
    print(f"Rating: {tool_eval['rating']}/5")
    print(f"Explanation: {tool_eval['explanation']}")
    print()

    # Evaluate response quality
    print("📈 RESPONSE QUALITY EVALUATION:")
    response_eval = await evaluator.evaluate_response_quality(query, mock_response, actual_tools)
    print(f"Rating: {response_eval['rating']}/5")
    print(f"Explanation: {response_eval['explanation']}")
    print()

    print("✅ Demo completed! The LLM judge provides detailed feedback on agent performance.")

if __name__ == "__main__":
    asyncio.run(demo_evaluation())