FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY data ./data
COPY scripts ./scripts
COPY dashboard ./dashboard
RUN pip install --no-cache-dir -e .
ENV PYTHONUNBUFFERED=1
CMD ["eval-miner", "serve", "--host", "0.0.0.0", "--port", "8613"]
