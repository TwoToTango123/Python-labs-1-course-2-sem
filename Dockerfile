FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src/ src/
COPY tests/ tests/
COPY demo.py ./

RUN pip install --no-cache-dir pytest pytest-cov

CMD ["sh", "-c", "python demo.py && echo && python -m pytest"]
