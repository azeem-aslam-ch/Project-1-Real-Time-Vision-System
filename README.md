# 🚀 VisionOps: Production Real-Time Vision Platform

VisionOps is a scalable, modular, and high-performance object detection and tracking platform designed for production surveillance and industrial analytics.

## 🏗 Architecture

The platform is built with a separate **Data Plane** (Inference) and **Control Plane** (API), using Redis as a high-speed inter-process communication bridge.

```eraser
// Real-Time Vision Platform Architecture

// Define Services
StreamlitUI [icon: monitor, color: blue] {
  label: "Streamlit UI"
  description: "Live Video, Control Panel, Metrics"
}

APIService [icon: server, color: green] {
  label: "FastAPI Control Plane"
  description: "REST API, MJPEG Streaming, Auth"
}

InferenceService [icon: cpu, color: red] {
  label: "GPU Vision Engine"
  description: "YOLOv8, ByteTrack, Event Engine"
}

// Data Layer
Redis [icon: database, color: orange] {
  label: "Redis"
  description: "Live Metrics, Latest Events, MJPEG Buffer"
}

SQLite [icon: database, color: gray] {
  label: "SQLite"
  description: "Event History (Persistent)"
}

// Flow Definitions
StreamlitUI -> APIService: "REST API (Start/Stop/Metrics)"
APIService -> InferenceService: "IPC / State Control"
InferenceService -> Redis: "Push Live Metrics & Events"
InferenceService -> SQLite: "Log Persistent Events"
InferenceService -> Redis: "Write Latest MJPEG Frame"
APIService -> Redis: "Pull Metrics & Frames"
APIService -> StreamlitUI: "MJPEG Video Stream + JSON JSON"
```

## 🛠 Features

- **Detection**: YOLOv8 (Ultralytics) with configurable confidence and device support.
- **Tracking**: Integrated ByteTrack for persistent multi-object tracking.
- **Event Engine**: 
    - **Line Crossing**: Detect when an object crosses a virtual boundary.
    - **ROI Intrusion**: Alert when an object enters a restricted zone.
- **MJPEG Streaming**: High-speed frame sharing via Redis for real-time visualization.
- **Monitoring**: Live FPS, Stage latency (p50/p95), and GPU/RAM utilization.
- **Security**: API-Key based authentication and structured JSON logging.

## 🚀 Quick Start (Docker)

1. **Clone the repository**
2. **Configure rules** in `config/config.yaml`.
3. **Run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```
4. **Access the Dashboard**:
   - Streamlit UI: `http://localhost:8501`
   - API Docs: `http://localhost:8000/docs`

## 📡 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/stream` | GET | MJPEG Video Stream |
| `/metrics` | GET | Real-time performance metrics |
| `/events` | GET | List latest 10 captured events |
| `/status` | GET | Current system state (RUNNING/STOPPED) |

**Example Curl**:
```bash
curl -H "X-API-Key: dev-key-123" http://localhost:8000/metrics
```

## 🏎 Performance Tuning

- **Resize**: Reduce `inference.resize_width` in `config.yaml` to increase FPS.
- **Precision**: Set `inference.half: true` for FP16 inference on compatible GPUs.
- **Frame Drop**: Increase `inference.frame_drop_threshold` to prevent lag in high-traffic scenes.

## 📦 Deployment Note (Cloud/VPS)
For production deployment:
1. Use an NVIDIA-Docker runtime for GPU acceleration.
2. Proxy FastAPI through Nginx with SSL.
3. Replace SQLite with PostgreSQL for large-scale event storage.
4. Scale out `api_service` using a Load Balancer if serving many UI clients.

---
Built with ❤️ for High-Performance AI Systems.
