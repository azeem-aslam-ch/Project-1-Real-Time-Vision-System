FROM python:3.11-slim
ENV PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY inference_service/requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Download model early for caching
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

COPY . .

CMD ["python", "inference_service/main.py"]
