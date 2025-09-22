# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# RUN apt-get update && apt-get install -y \
#     gcc \
#     g++ \
#     && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN pip install uv

# Copy UV configuration files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync

# Copy application code in layers for better caching
COPY src/ ./src/
COPY vantrails/ ./vantrails/
COPY data/ ./data/
COPY monitoring/ ./monitoring/
COPY app.py ./
COPY .env ./

# Expose port for Flask API
EXPOSE 8000

# Expose port for Gradio interface  
EXPOSE 7860

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden in docker-compose)
CMD ["uv", "run", "vantrails/answer.py"]