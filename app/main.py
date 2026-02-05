from __future__ import annotations

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from .analyzer import analyze_prescription

app = FastAPI(title="Prescription analyzer", version="0.2.0")

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/analyzer")
async def api_analyser(
    file: UploadFile | None = File(default=None),
    raw_text: str | None = Form(default=None),
) -> JSONResponse:
    raw_text = raw_text.strip() if raw_text else None

    image_bytes = None
    filename = None
    content_type = None

    if file is not None:
        if not file.content_type or not file.content_type.startswith("image/"):
            return JSONResponse(status_code=400, content={"error": "Please upload an image file."})
        image_bytes = await file.read()
        filename = file.filename
        content_type = file.content_type

    if raw_text:
        image_bytes = None

    if not image_bytes and not raw_text:
        return JSONResponse(status_code=400, content={"error": "Upload an image or paste text."})

    try:
        data = analyze_prescription(image_bytes, raw_text, filename, content_type)
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except RuntimeError as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})
    except Exception as exc:  # pylint: disable=broad-except
        return JSONResponse(status_code=500, content={"error": f"AI extraction failed: {exc}"})

    summary = data.get("summary", "")
    raw_text_out = data.get("transcription", raw_text or "")
    extracted = {key: value for key, value in data.items() if key != "summary"}

    return JSONResponse(
        content={
            "raw_text": raw_text_out,
            "extracted": extracted,
            "summary": summary,
        }
    )
