
FROM python:3.13-slim-bullseye
WORKDIR /app
COPY src/ /app/src/
COPY requirements.txt /app/
COPY README.md /app/

RUN python -m pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/app
CMD ["python", "src/main.py"]
