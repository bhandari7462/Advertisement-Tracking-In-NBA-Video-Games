from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from worker import run_pipeline_task
import os

app = FastAPI()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend")

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.post("/analyze")
async def analyze(request: Request):
    data = await request.json()
    youtube_url = data.get("youtubeUrl")
    email = data.get("email")
    model = data.get("model")
    brands = data.get("brands")
    timestamp = data.get("timestamp")

    if not youtube_url or not email or not brands:
        return JSONResponse(status_code=400, content={"error": "Missing required fields"})

    task = run_pipeline_task.delay(youtube_url, brands, model, email, timestamp)
    return {"message": "Pipeline triggered!", "task_id": task.id}
from fastapi.responses import FileResponse
from celery.result import AsyncResult
import os

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    task = AsyncResult(task_id)

    if not task.ready():
        return {"status": "processing"}
    if task.failed():
        return {"status": "failed"}

    result = task.result
    pdf_path = result.get("report")

    if not pdf_path or not os.path.exists(pdf_path):
        return {"status": "error", "message": "Report not found"}

    return FileResponse(pdf_path, media_type="application/pdf", filename="brand_analysis_report.pdf")
