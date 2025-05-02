# Start with a base Python image
FROM python:3.12-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the pyproject.toml for dependencies
COPY pyproject.toml /app/

# Install build backend and project dependencies
RUN pip install --upgrade pip && \
    pip install hatchling && \
    pip install .

# Copy the rest of the application code
COPY src/ /app/src/

# Set environment variables
ENV NEWS_API_KEY=${NEWS_API_KEY}

# Expose the port that the app runs on
EXPOSE 8000

ENTRYPOINT ["fastmcp", "run", "src/news_api_mcp/server.py:mcp", "-t", "sse", "--host", "0.0.0.0", "--port", "8000"]
