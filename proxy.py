from fastmcp import FastMCP, Client
import os

# Get backend server command from environment or default
BACKEND_CMD = os.environ.get("NEWS_API_MCP_BACKEND_CMD", "python -m src.news_api_mcp.server")

# Create a client that talks to the backend server via stdio
backend_client = Client(transport="stdio", command=BACKEND_CMD)

# Create the proxy server
proxy = FastMCP.from_client(
    backend_client,
    name="News API MCP Proxy"
)

if __name__ == "__main__":
    # Run the proxy server (default: stdio, but can be changed via env/args)
    proxy.run(transport='sse')