from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
import logging
from typing import Optional
from config.config import config
from api_service.core.deps import get_api_key, RedisReader

# Configure Logging
logging.basicConfig(level=config.logging.get("level", "INFO"))
logger = logging.getLogger(__name__)

app = FastAPI(title="Vision Control Plane")
reader = RedisReader(redis_url=config.storage.get("redis_url"))

@app.get("/status", dependencies=[Depends(get_api_key)])
async def get_status():
    return {
        "status": reader.get_status(),
        "source": config.inference.get("input_source")
    }

@app.get("/metrics", dependencies=[Depends(get_api_key)])
async def get_metrics():
    return reader.get_metrics()

@app.get("/events", dependencies=[Depends(get_api_key)])
async def get_events():
    return reader.get_latest_events()

# MJPEG Stream generator
async def frame_generator():
    while True:
        frame = reader.get_latest_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        await asyncio.sleep(0.01) # Approx 100 FPS max polling

@app.get("/stream")
async def video_stream():
    """MJPEG stream endpoint for UI consumption"""
    return StreamingResponse(
        frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/latest_frame", dependencies=[Depends(get_api_key)])
async def get_latest_frame():
    """Returns the latest single frame as a JPEG"""
    frame = reader.get_latest_frame()
    if not frame:
        raise HTTPException(status_code=404, detail="No frame available")
    from fastapi import Response
    return Response(content=frame, media_type="image/jpeg")

@app.post("/reload_config", dependencies=[Depends(get_api_key)])
async def reload_config():
    # In a real system, this might signal the inference service via Redis
    # or restart the process
    return {"message": "Config reload triggered"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.api.get("host"), port=config.api.get("port"))
