from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

app = FastAPI()
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
        return JSONResponse(status_code=200, content={
            "filename": file.filename,
            "message": "Upload successful",
            "path": file_location
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
