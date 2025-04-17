from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import json
from datetime import datetime
from nats.aio.client import Client as NATS

# Initialize NATS client
nats_client = NATS()

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Connect to NATS on startup
    servers = os.getenv("NATS_SERVERS", "nats://127.0.0.1:4222")
    await nats_client.connect(servers)

@app.on_event("shutdown")
async def shutdown_event():
    # Gracefully close NATS connection
    await nats_client.drain()
    await nats_client.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory to save uploaded resumes
env_dir = os.getenv("UPLOAD_DIR", "uploads")
UPLOAD_DIR = os.path.join(os.getcwd(), env_dir)
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/resumes/upload")
async def upload_resume(file: UploadFile = File(...)):
    try:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
        # Emit resume.uploaded event to NATS
        event_payload = json.dumps({
            "filename": file.filename,
            "path": file_location,
            "uploaded_at": datetime.utcnow().isoformat()
        }).encode()
        await nats_client.publish("resume.uploaded", event_payload)
        return JSONResponse(status_code=200, content={
            "filename": file.filename,
            "message": "Upload successful",
            "path": file_location
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
