# TimeCraft API Server Dockerfile
# Builds a container for the demo API server

FROM python:3.8-slim

WORKDIR /app

# Install required Python packages
RUN pip install --no-cache-dir \
    fastapi==0.68.0 \
    uvicorn==0.15.0 \
    numpy==1.19.2 \
    pydantic==1.10.5

# Copy API server code
COPY api_server.py .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/checkpoints

# Copy requirements first for better caching
COPY BRIDGE/requirements.txt ./bridge_requirements.txt

# Create a basic requirements file for REST API functionality
RUN echo "fastapi" > requirements.txt && \
    echo "uvicorn[standard]" >> requirements.txt && \
    echo "python-multipart" >> requirements.txt && \
    echo "pydantic>=1.10.5" >> requirements.txt && \
    echo "requests>=2.28.2" >> requirements.txt && \
    echo "pandas" >> requirements.txt && \
    echo "numpy" >> requirements.txt && \
    echo "scikit-learn" >> requirements.txt && \
    echo "aiofiles" >> requirements.txt

# Install Python dependencies for REST API and BRIDGE components
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt && \
    pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r bridge_requirements.txt

# Copy application files (including HTML UI)
# Note: To include latest UI changes, ensure you rebuild the image after making changes
COPY --chown=root:root . .

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Start the API server with uvicorn for concurrency
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
