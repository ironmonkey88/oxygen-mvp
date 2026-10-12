# Civic Pulse SQL MCP server. Built by wong-way-server's compose.yml straight
# from this folder at a pinned commit; see README.md.
FROM python:3.12-slim
RUN useradd --system --uid 10001 --no-create-home mcp
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py .
USER mcp
ENV CIVIC_PULSE_DB=/data/somerville_ro.duckdb PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["python", "/app/server.py"]
