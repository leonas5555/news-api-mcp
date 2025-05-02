import logging
from fastmcp import FastMCP
import os
import httpx
from news_api_mcp.tools import (
    make_news_api_request,
    format_articles,
    format_sources,
    API_KEY
)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger("news_api_mcp")

# Check for API key 
if not API_KEY:
    logger.error("Missing NEWS_API_KEY environment variable")
    raise ValueError("Missing NEWS_API_KEY environment variable")
else:
    logger.info("NEWS_API_KEY is set")

MCP_SERVER_NAME = "News API MCP"
logger.info(f"Starting {MCP_SERVER_NAME} server...")

# Initialize FastMCP with dependencies
mcp = FastMCP(MCP_SERVER_NAME, dependencies=["httpx>=0.28.1"])
logger.info(f"FastMCP server initialized. Ready to accept requests.")

@mcp.tool()
async def search_news(
    query: str,
    from_date: str = None,
    to_date: str = None,
    sources: str = None,
    language: str = "en",
    sort_by: str = "publishedAt",
    page_size: int = 20,
    page: int = 1
):
    logger.info(f"search_news called with query='{query}', from_date='{from_date}', to_date='{to_date}', sources='{sources}', language='{language}', sort_by='{sort_by}', page_size={page_size}, page={page}")
    params = {
        "q": query,
        "pageSize": page_size,
        "page": page,
        "language": language,
        "sortBy": sort_by
    }
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    if sources:
        params["sources"] = sources
    try:
        async with httpx.AsyncClient() as client:
            news_data = await make_news_api_request(client, "everything", params)
            logger.debug(f"News API response (truncated): {str(news_data)[:500]}")
            if isinstance(news_data, str):
                logger.error(f"News API error: {news_data}")
                return f"Error: {news_data}"
            articles = news_data.get("articles", [])
            total_results = news_data.get("totalResults", 0)
            if not articles:
                logger.info(f"No articles found for query: '{query}'")
                return f"No articles found for query: '{query}'"
            formatted_articles = format_articles(articles)
            logger.info(f"Returning {len(articles)} articles for query '{query}'")
            return f"Search results for '{query}' (Found {total_results} articles):\n\n{formatted_articles}"
    except Exception as e:
        logger.exception(f"Exception in search_news: {e}")
        return f"Internal server error: {e}"

@mcp.tool()
async def get_top_headlines(
    country: str = None,
    category: str = None,
    sources: str = None,
    query: str = None,
    page_size: int = 20,
    page: int = 1
):
    logger.info(f"get_top_headlines called with country='{country}', category='{category}', sources='{sources}', query='{query}', page_size={page_size}, page={page}")
    params = {
        "pageSize": page_size,
        "page": page
    }
    if country:
        params["country"] = country
    if category:
        params["category"] = category
    if sources:
        params["sources"] = sources
    if query:
        params["q"] = query
    try:
        async with httpx.AsyncClient() as client:
            news_data = await make_news_api_request(client, "top-headlines", params)
            logger.debug(f"News API response (truncated): {str(news_data)[:500]}")
            if isinstance(news_data, str):
                logger.error(f"News API error: {news_data}")
                return f"Error: {news_data}"
            articles = news_data.get("articles", [])
            total_results = news_data.get("totalResults", 0)
            if not articles:
                logger.info("No headlines found matching criteria")
                return "No headlines found matching your criteria"
            formatted_articles = format_articles(articles)
            title_parts = []
            if country:
                title_parts.append(f"country: {country.upper()}")
            if category:
                title_parts.append(f"category: {category}")
            if sources:
                title_parts.append(f"sources: {sources}")
            if query:
                title_parts.append(f"query: '{query}'")
            title = "Top headlines"
            if title_parts:
                title += " for " + ", ".join(title_parts)
            logger.info(f"Returning {len(articles)} headlines for {title}")
            return f"{title} (Found {total_results} articles):\n\n{formatted_articles}"
    except Exception as e:
        logger.exception(f"Exception in get_top_headlines: {e}")
        return f"Internal server error: {e}"

@mcp.tool()
async def get_news_sources(
    category: str = None,
    language: str = None,
    country: str = None
):
    logger.info(f"get_news_sources called with category='{category}', language='{language}', country='{country}'")
    params = {}
    if category:
        params["category"] = category
    if language:
        params["language"] = language
    if country:
        params["country"] = country
    try:
        async with httpx.AsyncClient() as client:
            news_data = await make_news_api_request(client, "top-headlines/sources", params)
            logger.debug(f"News API response (truncated): {str(news_data)[:500]}")
            if isinstance(news_data, str):
                logger.error(f"News API error: {news_data}")
                return f"Error: {news_data}"
            sources = news_data.get("sources", [])
            if not sources:
                logger.info("No news sources found matching criteria")
                return "No news sources found matching your criteria"
            formatted_sources = format_sources(sources)
            title_parts = []
            if category:
                title_parts.append(f"category: {category}")
            if language:
                title_parts.append(f"language: {language}")
            if country:
                title_parts.append(f"country: {country.upper()}")
            title = "Available news sources"
            if title_parts:
                title += " for " + ", ".join(title_parts)
            logger.info(f"Returning {len(sources)} sources for {title}")
            return f"{title} (Found {len(sources)} sources):\n\n{formatted_sources}"
    except Exception as e:
        logger.exception(f"Exception in get_news_sources: {e}")
        return f"Internal server error: {e}"
