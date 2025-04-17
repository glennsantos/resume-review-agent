from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import json
from datetime import datetime
from nats.aio.client import Client as NATS
import logging
from sqlalchemy import create_engine, Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)

# Initialize NATS client
nats_client = NATS()

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Connect to NATS on startup
    servers = os.getenv("NATS_SERVERS", "nats://127.0.0.1:4222")
    await nats_client.connect(servers)
    logging.info(f"Connected to NATS at {servers}")

@app.on_event("shutdown")
async def shutdown_event():
    # Gracefully close NATS connection
    await nats_client.drain()
    await nats_client.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for now
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory to save uploaded resumes
env_dir = os.getenv("UPLOAD_DIR", "uploads")
UPLOAD_DIR = os.path.join(os.getcwd(), env_dir)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# SQLAlchemy setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jobs.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class JobDescription(Base):
    __tablename__ = "job_descriptions"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic model for job description
class JDCreate(BaseModel):
    title: str
    content: str

@app.post("/resumes/upload")
async def upload_resume(file: UploadFile = File(...), jd_id: int = Form(...)):
    try:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
        # Emit resume.uploaded event to NATS
        event_payload = json.dumps({
            "filename": file.filename,
            "path": file_location,
            "uploaded_at": datetime.utcnow().isoformat(),
            "jd_id": jd_id
        }).encode()
        try:
            await nats_client.publish("resume.uploaded", event_payload)
            await nats_client.flush()
            logging.info(f"Published 'resume.uploaded' event: {event_payload}")
        except Exception as e:
            logging.error(f"Failed to publish to NATS: {e}")
        return JSONResponse(status_code=200, content={
            "filename": file.filename,
            "message": "Upload successful",
            "path": file_location
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/job_descriptions")
async def create_job_description(jd: JDCreate):
    db = SessionLocal()
    db_jd = JobDescription(title=jd.title, content=jd.content)
    db.add(db_jd)
    db.commit()
    db.refresh(db_jd)
    return JSONResponse(status_code=201, content={"id": db_jd.id, "title": db_jd.title, "content": db_jd.content, "created_at": db_jd.created_at.isoformat()})

@app.get("/job_descriptions")
async def get_job_descriptions():
    db = SessionLocal()
    jds = db.query(JobDescription).order_by(JobDescription.id).all()
    return JSONResponse(status_code=200, content=[{"id": jd.id, "title": jd.title} for jd in jds])
