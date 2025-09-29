#!/usr/bin/env python3
"""
BioRxiv MCP Server
BioRxiv preprint server for early pharmaceutical research intelligence
"""

import asyncio
from mcp.server import NotificationOptions, Server, InitializationOptions
from mcp.types import InitializeResult
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import logging
import requests
from typing import Any, Sequence
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("biorxiv-mcp")

class BioRxivMCPServer:
    def __init__(self):
        self.server = Server("biorxiv-mcp")
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available BioRxiv tools."""
            return [
                Tool(
                    name="search_preprints",
                    description="Search bioRxiv preprints for pharmaceutical research",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for preprints"
                            },
                            "category": {
                                "type": "string", 
                                "description": "Subject category (e.g., pharmacology, drug-discovery)"
                            },
                            "date_from": {
                                "type": "string",
                                "description": "Start date for search (YYYY-MM-DD)"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_preprint_details",
                    description="Get detailed information about a specific preprint",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "doi": {
                                "type": "string",
                                "description": "DOI of the preprint to retrieve"
                            }
                        },
                        "required": ["doi"]
                    }
                ),
                Tool(
                    name="track_research_trends",
                    description="Track research trends in pharmaceutical topics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Research topic to track trends for"
                            },
                            "time_period": {
                                "type": "string",
                                "description": "Time period for trend analysis (e.g., '6months', '1year')"
                            }
                        },
                        "required": ["topic"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
            """Handle tool calls."""
            if name == "search_preprints":
                return await self.search_preprints(arguments or {})
            elif name == "get_preprint_details":
                return await self.get_preprint_details(arguments or {})
            elif name == "track_research_trends":
                return await self.track_research_trends(arguments or {})
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def search_preprints(self, args: dict) -> list[TextContent]:
        """Search bioRxiv for preprints."""
        query = args.get("query", "")
        category = args.get("category", "")
        date_from = args.get("date_from", "")
        max_results = args.get("max_results", 10)
        
        try:
            # bioRxiv API search
            base_url = "https://api.biorxiv.org/details/biorxiv"
            
            # Build search parameters
            params = {
                "server": "biorxiv",
                "format": "json"
            }
            
            # For date range search
            if date_from:
                # Use date range endpoint
                end_date = datetime.now().strftime("%Y-%m-%d")
                url = f"{base_url}/{date_from}/{end_date}"
            else:
                # Use recent preprints
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
                end_date = datetime.now().strftime("%Y-%m-%d") 
                url = f"{base_url}/{start_date}/{end_date}"
            
            # Run synchronous HTTP request in thread pool to avoid blocking event loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: requests.get(url, params=params, timeout=15))
            response.raise_for_status()
            data = response.json()
            
            preprints = []
            if "collection" in data:
                for paper in data["collection"][:max_results]:
                    # Filter by query if provided
                    title = paper.get("title", "").lower()
                    abstract = paper.get("abstract", "").lower()
                    
                    if not query or query.lower() in title or query.lower() in abstract:
                        preprints.append({
                            "doi": paper.get("doi", ""),
                            "title": paper.get("title", ""),
                            "authors": paper.get("authors", ""),
                            "date": paper.get("date", ""),
                            "category": paper.get("category", ""),
                            "abstract": paper.get("abstract", "")[:500] + "..." if len(paper.get("abstract", "")) > 500 else paper.get("abstract", ""),
                            "url": f"https://www.biorxiv.org/content/{paper.get('doi', '')}v1"
                        })
            
            result = {
                "query": query,
                "category": category,
                "preprints_found": len(preprints),
                "preprints": preprints,
                "source": "bioRxiv API",
                "timestamp": datetime.now().isoformat()
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "source": "bioRxiv MCP Server",
                    "query": query
                })
            )]

    async def get_preprint_details(self, args: dict) -> list[TextContent]:
        """Get detailed preprint information."""
        doi = args.get("doi", "")
        
        try:
            # bioRxiv details API
            url = f"https://api.biorxiv.org/details/biorxiv/{doi}"
            
            # Run synchronous HTTP request in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: requests.get(url, timeout=10))
            response.raise_for_status()
            data = response.json()
            
            if "collection" in data and len(data["collection"]) > 0:
                paper = data["collection"][0]
                
                result = {
                    "doi": paper.get("doi", ""),
                    "title": paper.get("title", ""),
                    "authors": paper.get("authors", ""),
                    "date": paper.get("date", ""),
                    "category": paper.get("category", ""),
                    "abstract": paper.get("abstract", ""),
                    "server": paper.get("server", ""),
                    "version": paper.get("version", ""),
                    "url": f"https://www.biorxiv.org/content/{doi}v{paper.get('version', '1')}",
                    "source": "bioRxiv API"
                }
            else:
                result = {
                    "error": "Preprint not found",
                    "doi": doi,
                    "source": "bioRxiv API"
                }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "source": "bioRxiv MCP Server",
                    "doi": doi
                })
            )]

    async def track_research_trends(self, args: dict) -> list[TextContent]:
        """Track research trends for a topic."""
        topic = args.get("topic", "")
        time_period = args.get("time_period", "6months")
        
        try:
            # Calculate date range based on time period
            end_date = datetime.now()
            if time_period == "1year":
                start_date = end_date - timedelta(days=365)
            elif time_period == "6months":
                start_date = end_date - timedelta(days=180)
            elif time_period == "3months":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=180)  # Default 6 months
            
            # Search for papers in time range
            search_result = await self.search_preprints({
                "query": topic,
                "date_from": start_date.strftime("%Y-%m-%d"),
                "max_results": 100
            })
            
            # Parse search results for trend analysis
            search_data = json.loads(search_result[0].text)
            preprints = search_data.get("preprints", [])
            
            # Analyze trends
            monthly_counts = {}
            categories = {}
            recent_papers = []
            
            for paper in preprints:
                # Count by month
                paper_date = paper.get("date", "")
                if paper_date:
                    month_key = paper_date[:7]  # YYYY-MM
                    monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
                
                # Count by category
                category = paper.get("category", "Unknown")
                categories[category] = categories.get(category, 0) + 1
                
                # Recent papers (last 30 days)
                if paper_date and paper_date >= (end_date - timedelta(days=30)).strftime("%Y-%m-%d"):
                    recent_papers.append(paper)
            
            trend_analysis = {
                "topic": topic,
                "time_period": time_period,
                "total_papers": len(preprints),
                "monthly_distribution": monthly_counts,
                "category_distribution": categories,
                "recent_papers_count": len(recent_papers),
                "recent_papers": recent_papers[:10],  # Top 10 recent
                "trend_summary": f"Found {len(preprints)} papers on '{topic}' in the last {time_period}",
                "source": "bioRxiv Trend Analysis"
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(trend_analysis, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Trend analysis failed: {str(e)}",
                    "topic": topic,
                    "time_period": time_period
                })
            )]

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="biorxiv-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

if __name__ == "__main__":
    server = BioRxivMCPServer()
    asyncio.run(server.run())
