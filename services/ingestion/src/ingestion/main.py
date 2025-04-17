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
import openai
import re
from ingestion.scoring.comparison import get_compare_messages
from PyPDF2 import PdfReader
from io import BytesIO

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
openai.api_key = os.getenv("OPENAI_API_KEY")

# Pydantic model for job description
class JDCreate(BaseModel):
    title: str
    content: str

def clean_resume_text(text: str) -> str:
    patterns = [
        r'\S+@\S+',      # emails
        r'http\S+',        # URLs
        r'\+?\d[\d\s\-]{7,}',  # phone numbers
        r'page\s*\d+\s*of\s*\d+', # page numbers
    ]
    for pat in patterns:
        text = re.sub(pat, ' ', text, flags=re.I)
    # remove generic headers
    text = re.sub(r'\b(curriculum vitae|resume)\b', ' ', text, flags=re.I)
    # collapse extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

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

@app.post("/resumes/compare")
async def compare_resume(file: UploadFile = File(...), jd_id: int = Form(...)):
    # Read resume text
    try:
        raw_bytes = await file.read()
        # Extract text for PDF via pypdf, else decode bytes
        filename_lower = file.filename.lower()
        if filename_lower.endswith('.pdf'):
            reader = PdfReader(BytesIO(raw_bytes))
            raw_text = '\n'.join([page.extract_text() or '' for page in reader.pages])
        else:
            raw_text = raw_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file: {e}")
    # Attempt to load normalized JSON resume from normalizer service
    filename_no_ext = file.filename.rsplit('.', 1)[0]
    json_path = os.path.join(UPLOAD_DIR, 'json', f"{filename_no_ext}.json")
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as jf:
            resume_json = json.load(jf)
        sections = []
        summary = resume_json.get('basics', {}).get('summary', '')
        if summary:
            sections.append(summary)
        skills = resume_json.get('skills')
        if skills:
            sections.append('Skills: ' + ', '.join(skills))
        for work in resume_json.get('work', []):
            title = work.get('position') or work.get('title', '')
            highlights = work.get('highlights') or work.get('description', '')
            if isinstance(highlights, list):
                highlights = '; '.join(highlights)
            sections.append(f"{title}: {highlights}")
        resume_text_for_llm = '\n'.join(sections)
    else:
        # Fallback: clean and truncate raw resume text
        resume_text_for_llm = clean_resume_text(raw_text)
    logging.info(f"Using resume_text_for_llm (first 500 chars): {resume_text_for_llm[:500]}")
    # Fetch job description
    db = SessionLocal()
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    # Build messages payload for LLM
    messages = get_compare_messages(jd.content, resume_text_for_llm)
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0
        )
        llm_output = resp.choices[0].message.content
        logging.info(f"LLM compare raw output: {llm_output[:500]}")  # log a snippet for debugging
        if not llm_output.strip():
            raise HTTPException(status_code=502, detail='Empty response from LLM')
        # Strip markdown code fences
        output_clean = re.sub(r'```(?:json)?|```', '', llm_output).strip()
        logging.info(f"LLM compare cleaned output: {output_clean[:500]}")
        # Parse JSON, extract JSON substring on failure
        try:
            data = json.loads(output_clean)
        except json.JSONDecodeError:
            m = re.search(r'\{.*\}', output_clean, flags=re.S)
            if m:
                data = json.loads(m.group(0))
            else:
                err_snip = output_clean[:200]
                raise HTTPException(status_code=502, detail=f"Invalid JSON from LLM: {err_snip}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error or invalid JSON: {e}")
    return JSONResponse(status_code=200, content=data)
