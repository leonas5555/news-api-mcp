# Start with a base Python image
FROM python:3.12-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the entire project
COPY . /app/

# Install dependencies and the package in development mode
RUN pip install --upgrade pip && \
    pip install -e .

# Set environment variables
# This will be overridden by the docker-compose environment setting
ENV NEWS_API_KEY=""

# Expose the port that the app runs on
EXPOSE 8000

# Add a healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/messages/ || exit 1

# Run the server with SSE transport on port 8000
ENTRYPOINT ["fastmcp", "run", "src/news_api_mcp/server.py:mcp", "-t", "sse", "--host", "0.0.0.0", "--port", "8000"]
