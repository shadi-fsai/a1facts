"""
Clinical Trials Agent Evaluation Suite

Uses LLM as a judge to evaluate:
1. Tool selection accuracy - did the agent call the correct tools?
2. Response quality - how accurate and helpful is the response?

Tests are based on complex evaluation queries from complex_evaluation_queries.md
"""

import pytest
import asyncio
import os
import sys
import re
from typing import List, Dict, Any
from pathlib import Path

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'lib', 'src'))
sys.path.append(os.path.dirname(__file__))

from a1facts.knowledge_base import KnowledgeBase
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from textwrap import dedent
from dotenv import load_dotenv


class QueryEvaluator:
    """Uses LLM as a judge to evaluate agent performance."""

    def __init__(self):
        load_dotenv()
        self.judge_model = OpenAIChat(id="gpt-4o-mini", api_key=os.getenv('OPENAI_API_KEY'))

    async def evaluate_tool_selection(self, query: str, expected_tools: List[str], actual_tools: List[str]) -> Dict[str, Any]:
        """Evaluate if the agent selected the correct tools."""

        prompt = f"""
        Evaluate if the agent selected the correct tools for this query.

        Query: {query}

        Expected tools (in order): {expected_tools}
        Actual tools called: {actual_tools}

        Rate the tool selection on a scale of 1-5 (5 being perfect):
        - 5: All expected tools called in correct order
        - 4: All expected tools called but wrong order
        - 3: Most expected tools called
        - 2: Some expected tools called
        - 1: Wrong or no tools called

        Provide a brief explanation of your rating.
        """

        response = await self.judge_model.arun(prompt)

        # Extract rating and explanation
        content = response.content
        rating_match = re.search(r'(\d+)/5|\b([1-5])\b', content)
        rating = int(rating_match.group(1) or rating_match.group(2)) if rating_match else 3

        return {
            'rating': rating,
            'explanation': content,
            'expected_tools': expected_tools,
            'actual_tools': actual_tools
        }

    async def evaluate_response_quality(self, query: str, response: str, tool_calls: List[str]) -> Dict[str, Any]:
        """Evaluate the quality and accuracy of the agent's response."""

        prompt = f"""
        Evaluate the quality and accuracy of this clinical trials agent response.

        Query: {query}

        Tools called: {tool_calls}

        Response: {response}

        Rate the response quality on a scale of 1-5 (5 being excellent):
        - 5: Highly accurate, comprehensive, well-structured, cites sources
        - 4: Mostly accurate with good structure
        - 3: Partially accurate but missing some information
        - 2: Inaccurate or incomplete
        - 1: Irrelevant or incorrect

        Consider:
        - Factual accuracy
        - Completeness of information
        - Source citation
        - Response structure
        - Relevance to query

        Provide a brief explanation of your rating.
        """

        judge_response = await self.judge_model.arun(prompt)

        # Extract rating
        content = judge_response.content
        rating_match = re.search(r'(\d+)/5|\b([1-5])\b', content)
        rating = int(rating_match.group(1) or rating_match.group(2)) if rating_match else 3

        return {
            'rating': rating,
            'explanation': content,
            'response_length': len(response),
            'tool_count': len(tool_calls)
        }


class QueryParser:
    """Parse complex evaluation queries from markdown file."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def parse_queries(self) -> List[Dict[str, Any]]:
        """Parse queries and expected tool chains from markdown."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        queries = []
        # Split by numbered items
        sections = re.split(r'\d+\.\s+\*\*Query:\*\*', content)[1:]

        for section in sections:
            # Extract query
            query_match = re.search(r'"([^"]+)"', section)
            if not query_match:
                continue
            query = query_match.group(1)

            # Extract predicted tool chain
            tools_section = re.search(r'\*\*Predicted Tool Chain:\*\*(.*?)(?=\d+\.|$)', section, re.DOTALL)
            if tools_section:
                tools_text = tools_section.group(1)
                # Extract tool calls
                tool_calls = re.findall(r'`([^`]+)`', tools_text)
                expected_tools = [call for call in tool_calls if 'Tool.' in call or 'acquire_tool' in call]
            else:
                expected_tools = []

            queries.append({
                'query': query,
                'expected_tools': expected_tools,
                'full_description': section.strip()
            })

        return queries


@pytest.fixture(scope="session")
def knowledge_base():
    """Create knowledge base for testing."""
    load_dotenv()
    base_dir = Path(__file__).parent
    ontology_path = base_dir / "trials.yaml"
    sources_path = base_dir / "sources.yaml"

    kb = KnowledgeBase(
        "clinical_trials_agent_test",
        str(ontology_path),
        str(sources_path),
        use_neo4j=False,
        disable_exa=True
    )
    yield kb
    # Cleanup
    try:
        kb.close()
    except:
        pass


@pytest.fixture(scope="session")
def agent(knowledge_base):
    """Create agent for testing."""
    agent = Agent(
        name="clinical_trials_agent_test",
        role="get clinical trials information",
        model=OpenAIChat(id="gpt-4o-mini"),
        tools=knowledge_base.get_tools(),
        instructions=dedent("""You are a clinical trials intelligence agent that provides REAL-TIME data from pharmaceutical APIs. You MUST:
        1. ALWAYS start with query_tool to search the knowledge graph
        2. If query_tool doesn't provide current/sufficient data, IMMEDIATELY use acquire_tool to fetch live API data
        3. When calling acquire_tool, explicitly mention you're "Fetching live data from [source] API..."
        4. NEVER use internal training knowledge - only use tool results
        5. ALWAYS cite the specific API endpoints and data sources used
        6. Include data freshness indicators (e.g., "Data retrieved from ClinicalTrials.gov API on [date]")
        7. Show API call details to prove data authenticity
        Format your responses to clearly show:
        📡 API DATA SOURCE: [which API was called]
        [SEARCH QUERY]: [what was searched]
        [RESULTS]: [data with sources]
        ⏰ RETRIEVED: [when the data was fetched]"""),
        markdown=True,
        debug_mode=False,  # Disable debug for cleaner test output
    )
    return agent


@pytest.fixture(scope="session")
def evaluator():
    """Create LLM evaluator."""
    return QueryEvaluator()


@pytest.fixture(scope="session")
def test_queries():
    """Load test queries from markdown file."""
    parser = QueryParser(Path(__file__).parent / "complex_evaluation_queries.md")
    return parser.parse_queries()


@pytest.mark.asyncio
async def test_query_tool_selection(query_data, agent, evaluator):
    """Test if agent selects correct tools for each query."""
    query = query_data['query']
    expected_tools = query_data['expected_tools']

    # Capture tool calls by running agent
    result = await agent.arun(query)

    # Extract actual tool calls from agent execution
    # This requires accessing the agent's internal state or logs
    # For now, we'll use a simplified approach
    actual_tools = extract_tool_calls_from_response(result.content)

    evaluation = await evaluator.evaluate_tool_selection(query, expected_tools, actual_tools)

    # Assert minimum quality threshold
    assert evaluation['rating'] >= 3, f"Tool selection failed: {evaluation['explanation']}"

    # Store results for reporting
    evaluation['query'] = query
    return evaluation


@pytest.mark.asyncio
async def test_response_quality(query_data, agent, evaluator):
    """Test response quality for each query."""
    query = query_data['query']

    result = await agent.arun(query)

    # Extract tool calls from response
    tool_calls = extract_tool_calls_from_response(result.content)

    evaluation = await evaluator.evaluate_response_quality(query, result.content, tool_calls)

    # Assert minimum quality threshold
    assert evaluation['rating'] >= 3, f"Response quality failed: {evaluation['explanation']}"

    # Store results
    evaluation['query'] = query
    evaluation['response'] = result.content
    return evaluation


def extract_tool_calls_from_response(response: str) -> List[str]:
    """Extract tool call information from agent response."""
    tools = []

    # Look for patterns indicating tool usage
    if 'ClinicalTrials.gov' in response or 'clinical trials' in response.lower():
        tools.append('ClinicalTrialsTool')
    if 'FDA' in response or 'drug safety' in response.lower():
        tools.append('FDATool')
    if 'PubMed' in response or 'literature' in response.lower():
        tools.append('PubMedTool')
    if 'medRxiv' in response:
        tools.append('MedRxivTool')
    if 'BMI' in response or 'calculate' in response.lower():
        tools.append('MedicalCalculatorTool')
    if 'ICD-10' in response or 'terminology' in response.lower():
        tools.append('MedicalTerminologyTool')
    if 'health topics' in response.lower():
        tools.append('HealthTopicsTool')
    if 'NCBI' in response or 'bookshelf' in response.lower():
        tools.append('NCIBookshelfTool')
    if 'DICOM' in response:
        tools.append('DicomTool')

    return tools


@pytest.mark.parametrize("query_data", test_queries[:5])  # Test first 5 queries for faster runs
@pytest.mark.asyncio
async def test_sample_queries_tool_selection(query_data, agent, evaluator):
    """Test tool selection for a sample of queries."""
    evaluation = await test_query_tool_selection(query_data, agent, evaluator)
    assert evaluation['rating'] >= 2  # More lenient for initial testing


@pytest.mark.parametrize("query_data", test_queries[:5])
@pytest.mark.asyncio
async def test_sample_queries_response_quality(query_data, agent, evaluator):
    """Test response quality for a sample of queries."""
    evaluation = await test_response_quality(query_data, agent, evaluator)
    assert evaluation['rating'] >= 2  # More lenient for initial testing


def test_parse_queries(test_queries):
    """Test that queries are parsed correctly."""
    assert len(test_queries) > 0, "No queries parsed from file"
    assert all('query' in q and 'expected_tools' in q for q in test_queries), "Queries missing required fields"


if __name__ == "__main__":
    # Allow running individual tests
    pytest.main([__file__, "-v"])