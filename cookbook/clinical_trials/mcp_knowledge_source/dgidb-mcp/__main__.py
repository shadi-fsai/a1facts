#!/usr/bin/env python3
"""
DGIdb MCP Server
Drug-Gene Interaction Database MCP server for A1Facts clinical trials intelligence
"""

import asyncio
import json
import sys
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dgidb-mcp")

class DGIdbMCPServer:
    def __init__(self):
        self.server = Server("dgidb-mcp")
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available DGIdb tools."""
            return [
                Tool(
                    name="search_drug_interactions",
                    description="Search for drug-gene interactions in DGIdb database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "drug_name": {
                                "type": "string",
                                "description": "Name of the drug to search for interactions"
                            },
                            "interaction_types": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Types of interactions to filter (e.g., inhibitor, activator)"
                            }
                        },
                        "required": ["drug_name"]
                    }
                ),
                Tool(
                    name="get_gene_info",
                    description="Get detailed information about a specific gene",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "gene_name": {
                                "type": "string",
                                "description": "Gene symbol or name to query"
                            }
                        },
                        "required": ["gene_name"]
                    }
                ),
                Tool(
                    name="analyze_mechanism",
                    description="Analyze drug mechanism of action through gene interactions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "drug_name": {
                                "type": "string", 
                                "description": "Drug name for mechanism analysis"
                            },
                            "include_pathways": {
                                "type": "boolean",
                                "description": "Include pathway analysis in results"
                            }
                        },
                        "required": ["drug_name"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
            """Handle tool calls."""
            if name == "search_drug_interactions":
                return await self.search_drug_interactions(arguments or {})
            elif name == "get_gene_info":
                return await self.get_gene_info(arguments or {})
            elif name == "analyze_mechanism":
                return await self.analyze_mechanism(arguments or {})
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def search_drug_interactions(self, args: dict) -> list[TextContent]:
        """Search DGIdb for drug-gene interactions."""
        drug_name = args.get("drug_name", "")
        
        try:
            # DGIdb API call
            url = f"https://www.dgidb.org/api/v2/interactions.json"
            params = {"drugs": drug_name}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            interactions = []
            if "matchedTerms" in data:
                for match in data["matchedTerms"]:
                    if "interactions" in match:
                        for interaction in match["interactions"]:
                            interactions.append({
                                "drug": match.get("searchTerm", ""),
                                "gene": interaction.get("geneName", ""),
                                "interaction_type": interaction.get("interactionType", ""),
                                "source": interaction.get("source", ""),
                                "score": interaction.get("score", "")
                            })
            
            result = {
                "drug_searched": drug_name,
                "interactions_found": len(interactions),
                "interactions": interactions[:20],  # Limit to first 20
                "source": "DGIdb API",
                "timestamp": "2025-09-24"
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
                    "source": "DGIdb MCP Server",
                    "drug_searched": drug_name
                })
            )]

    async def get_gene_info(self, args: dict) -> list[TextContent]:
        """Get gene information from DGIdb."""
        gene_name = args.get("gene_name", "")
        
        try:
            url = f"https://www.dgidb.org/api/v2/genes/{gene_name}.json"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "gene_searched": gene_name,
                    "gene_info": data,
                    "source": "DGIdb API"
                }, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "source": "DGIdb MCP Server",
                    "gene_searched": gene_name
                })
            )]

    async def analyze_mechanism(self, args: dict) -> list[TextContent]:
        """Analyze drug mechanism through gene interactions."""
        drug_name = args.get("drug_name", "")
        include_pathways = args.get("include_pathways", False)
        
        # This is a simplified mechanism analysis
        # In a real implementation, this would integrate multiple data sources
        interactions_result = await self.search_drug_interactions({"drug_name": drug_name})
        
        try:
            interactions_data = json.loads(interactions_result[0].text)
            
            # Analyze interaction types
            interaction_types = {}
            target_genes = []
            
            for interaction in interactions_data.get("interactions", []):
                int_type = interaction.get("interaction_type", "unknown")
                interaction_types[int_type] = interaction_types.get(int_type, 0) + 1
                target_genes.append(interaction.get("gene", ""))
            
            mechanism_analysis = {
                "drug": drug_name,
                "primary_targets": target_genes[:10],  # Top 10 targets
                "interaction_type_distribution": interaction_types,
                "mechanism_summary": f"Drug targets {len(set(target_genes))} genes through {len(interaction_types)} interaction types",
                "source": "DGIdb Mechanism Analysis"
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(mechanism_analysis, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Mechanism analysis failed: {str(e)}",
                    "drug": drug_name
                })
            )]

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="dgidb-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

if __name__ == "__main__":
    server = DGIdbMCPServer()
    asyncio.run(server.run())
