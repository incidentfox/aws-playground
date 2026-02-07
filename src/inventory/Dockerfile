FROM python:3.12-slim

WORKDIR /app

COPY ./src/inventory/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/inventory/inventory.py ./

EXPOSE 8080

ENTRYPOINT ["opentelemetry-instrument", "python", "inventory.py"]
