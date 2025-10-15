# main.py
import os
# Suppress gRPC warnings
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'

from fastapi import FastAPI, UploadFile, File, Depends, Form, HTTPException, Header
from typing import List
import shutil, os, io
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse, HTMLResponse
from models import ReviewReport, SessionLocal
from llm_analyzer import analyze_code_with_llm

app = FastAPI(title="Code Review Assistant API")

# Serve static frontend (only if directory exists)
import os
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Simple API key - for demo only. Put SECRET_API_KEY in your .env if you enable it.
DEMO_API_KEY = os.getenv("DEMO_API_KEY", None)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_api_key(x_api_key: str = Header(None)):
    # If no DEMO_API_KEY set, skip requirement (local dev). Otherwise require match.
    if DEMO_API_KEY:
        if not x_api_key or x_api_key != DEMO_API_KEY:
            raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/review/")
async def review_code(
    files: List[UploadFile] = File(...),
    language: str = Form("python"),
    db: Session = Depends(get_db),
    x_api_key: str = Header(None)
):
    # If you enabled require_api_key, call it:
    if DEMO_API_KEY:
        require_api_key(x_api_key)

    # Validate language (basic)
    allowed = {"python","javascript","java","c","cpp","csharp","go","ruby"}
    if language.lower() not in allowed:
        raise HTTPException(status_code=400, detail=f"Language not supported: {language}")

    results = {}
    for file in files:
        # Validate file type
        if file.filename.split(".")[-1] not in ("py","js","java","cpp","c","cs","go","rb","txt"):
            results[file.filename] = "Unsupported file extension"
            continue

        # Save temporarily
        tmp_path = os.path.join("tmp_uploads", file.filename)
        os.makedirs("tmp_uploads", exist_ok=True)
        with open(tmp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Read (binary -> text)
        try:
            with open(tmp_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            with open(tmp_path, "r", encoding="latin-1") as f:
                content = f.read()

        # Analyze
        analysis_result = analyze_code_with_llm(content, language.lower())

        # Save in DB
        db_report = ReviewReport(filename=file.filename, language=language.lower(), report=analysis_result.get("review_text", ""))
        db.add(db_report)
        db.commit()
        db.refresh(db_report)

        results[file.filename] = analysis_result

        # Optionally remove tmp file
        os.remove(tmp_path)

    return JSONResponse(results)

@app.get("/reports/")
def get_reports(db: Session = Depends(get_db)):
    # return last 50 reports
    rows = db.query(ReviewReport).order_by(ReviewReport.id.desc()).limit(50).all()
    return [{"id": r.id, "filename": r.filename, "language": getattr(r, "language", "unknown"), "report": r.report} for r in rows]

@app.get("/reports/{report_id}/download")
def download_report(report_id: int, db: Session = Depends(get_db)):
    r = db.query(ReviewReport).filter(ReviewReport.id == report_id).first()
    if not r:
        raise HTTPException(404, "report not found")
    # Return plain text file for now
    stream = io.BytesIO(r.report.encode("utf-8"))
    return StreamingResponse(stream, media_type="text/plain", headers={"Content-Disposition": f"attachment; filename={r.filename}.review.txt"})

@app.get("/")
def read_root():
    if os.path.exists(os.path.join("static", "index.html")):
        return FileResponse(os.path.join("static", "index.html"))
    else:
        # Fallback HTML if static files not available
        return HTMLResponse("""
<!DOCTYPE html>
<html><head><title>Code Review Assistant</title></head>
<body>
<h1>🚀 AI Code Review Assistant</h1>
<p>API is running! Use the /review/ endpoint to analyze code.</p>
<p>Static files not found. Please ensure the static directory is uploaded.</p>
</body></html>
        """)
