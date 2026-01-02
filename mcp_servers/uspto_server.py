"""
USPTO Patent Database MCP Server
Provides tools for patent search and innovation trend analysis
"""

from mcp.server import Server
from mcp.types import Tool, TextContent
import httpx
import json
from typing import Optional, List
import asyncio
import sys

# Add debug logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("uspto-patent-search")

USPTO_BASE_URL = "https://developer.uspto.gov/ibd-api/v1"

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Define available USPTO tools"""
    logger.info("list_tools called")
    return [
        Tool(
            name="search_patents",
            description="Search USPTO patent database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search keywords"
                    },
                    "assignees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Company names"
                    },
                    "date_range": {
                        "type": "string",
                        "description": "Date range YYYY-YYYY"
                    },
                    "max_results": {
                        "type": "integer",
                        "default": 50
                    }
                },
                "required": ["query"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    logger.info(f"call_tool called with name={name}, arguments={arguments}")
    
    try:
        if name == "search_patents":
            return await search_patents(
                query=arguments["query"],
                assignees=arguments.get("assignees"),
                date_range=arguments.get("date_range"),
                max_results=arguments.get("max_results", 50)
            )
        else:
            error_response = {"error": f"Unknown tool: {name}"}
            return [TextContent(
                type="text",
                text=json.dumps(error_response, indent=2)
            )]
    
    except Exception as e:
        logger.error(f"Error in call_tool: {str(e)}", exc_info=True)
        error_response = {"error": str(e)}
        return [TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]


async def search_patents(query: str, assignees: Optional[List[str]], 
                        date_range: Optional[str], max_results: int) -> list[TextContent]:
    """Search USPTO patent database"""
    logger.info(f"search_patents called with query={query}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        params = {
            "searchText": query,
            "rows": min(max_results, 1000)
        }
        
        if assignees:
            assignee_query = " OR ".join(assignees)
            params["assignee"] = assignee_query
        
        if date_range:
            params["dateRange"] = date_range
        
        try:
            logger.info(f"Calling USPTO API with params: {params}")
            response = await client.get(
                f"{USPTO_BASE_URL}/patent/application",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"USPTO API returned {data.get('numFound', 0)} results")
            
            # Format results
            results = {
                "query": query,
                "total_found": data.get("numFound", 0),
                "returned": len(data.get("docs", [])),
                "patents": []
            }
            
            for patent in data.get("docs", [])[:max_results]:
                results["patents"].append({
                    "patent_number": patent.get("patentApplicationNumber"),
                    "title": patent.get("inventionTitle"),
                    "assignee": patent.get("assigneeEntityName"),
                    "filing_date": patent.get("filingDate"),
                    "abstract": patent.get("inventionAbstract", "")[:300],
                    "inventors": patent.get("inventorNameArrayText", [])[:3]
                })
            
            result_json = json.dumps(results, indent=2)
            logger.info(f"Returning result: {result_json[:200]}...")
            
            return [TextContent(
                type="text",
                text=result_json
            )]
        
        except httpx.HTTPError as e:
            logger.error(f"USPTO API error: {str(e)}")
            error_response = {"error": f"USPTO API error: {str(e)}"}
            return [TextContent(
                type="text",
                text=json.dumps(error_response, indent=2)
            )]
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            error_response = {"error": f"Unexpected error: {str(e)}"}
            return [TextContent(
                type="text",
                text=json.dumps(error_response, indent=2)
            )]


async def main():
    """Entry point for MCP server"""
    logger.info("Starting USPTO MCP Server")
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server initialized, waiting for requests")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    logger.info("USPTO MCP Server script started")
    asyncio.run(main())