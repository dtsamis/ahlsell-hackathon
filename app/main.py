import os
from io import BytesIO
from typing import List, Optional

from fastapi import FastAPI, File, UploadFile, Query, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image

from app.model import FloorCADModelManager
from app.schemas import PredictionResponse, ModelInfoResponse

app = FastAPI(
    title="FloorCAD YOLOv8n Detection API",
    description="CAD Floor Plan Symbol & Architectural Element Detection using Ultralytics YOLOv8n",
    version="1.0.0",
)

# Enable CORS for cross-origin frontend support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(SAMPLES_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

model_manager = FloorCADModelManager.get_instance()


@app.get("/api/health")
def health_check():
    """Health check endpoint indicating server and model status."""
    return {
        "status": "healthy",
        "model_loaded": model_manager.is_loaded,
        "device": model_manager.device,
        "repo_id": model_manager.repo_id,
    }


@app.get("/api/info", response_model=ModelInfoResponse)
def get_model_info():
    """Returns model metadata, target domain, and supported 35 classes."""
    try:
        return model_manager.get_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model info: {str(e)}")


@app.get("/api/classes")
def get_classes():
    """Returns dictionary of supported architectural classes."""
    info = model_manager.get_info()
    return {"total": info.num_classes, "classes": info.classes}


@app.get("/api/samples")
def list_samples():
    """Lists available sample floor plans for 1-click testing."""
    samples = []
    if os.path.exists(SAMPLES_DIR):
        for f in sorted(os.listdir(SAMPLES_DIR)):
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                samples.append({
                    "id": f,
                    "filename": f,
                    "name": os.path.splitext(f)[0].replace("_", " ").title(),
                    "url": f"/api/samples/{f}",
                })
    return {"samples": samples}


@app.get("/api/samples/{filename}")
def get_sample_image(filename: str):
    """Retrieves a specific sample image."""
    filepath = os.path.join(SAMPLES_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Sample image not found")
    media_type = "image/png" if filename.lower().endswith(".png") else "image/jpeg"
    return StreamingResponse(open(filepath, "rb"), media_type=media_type)


def _parse_allowed_classes(classes_input: Optional[str]) -> Optional[List[int]]:
    if not classes_input:
        return None
    res = []
    for item in classes_input.split(","):
        item = item.strip()
        if not item:
            continue
        if item.isdigit():
            res.append(int(item))
        else:
            # Try to match class name
            info = model_manager.get_info()
            for cid, cname in info.classes.items():
                if cname.lower() == item.lower():
                    res.append(cid)
                    break
    return res if res else None


@app.post("/api/predict", response_model=PredictionResponse)
async def predict_floorplan(
    file: UploadFile = File(..., description="CAD floor plan image file (PNG, JPG, BMP)"),
    conf: float = Form(0.25, ge=0.01, le=1.0, description="Confidence threshold"),
    iou: float = Form(0.45, ge=0.01, le=1.0, description="IoU threshold for NMS"),
    imgsz: int = Form(640, ge=320, le=2048, description="Inference image resolution"),
    classes: Optional[str] = Form(None, description="Comma-separated class IDs or names to filter"),
    return_annotated: bool = Form(True, description="Whether to include base64 annotated image"),
):
    """
    Run YOLOv8n object detection on an uploaded CAD floor plan image.
    Returns detected symbols, bounding boxes (pixel and normalized), and confidence scores.
    """
    try:
        if hasattr(file, "file"):
            if hasattr(file.file, "seek"):
                file.file.seek(0)
            contents = file.file.read()
        else:
            contents = await file.read()
        if not contents:
            raise ValueError("Uploaded image file is empty.")
        image = Image.open(BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    allowed_classes_list = _parse_allowed_classes(classes)

    try:
        response = model_manager.predict(
            image=image,
            conf=conf,
            iou=iou,
            imgsz=imgsz,
            allowed_classes=allowed_classes_list,
            return_annotated=return_annotated,
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@app.post("/api/predict/image")
async def predict_floorplan_visual(
    file: UploadFile = File(...),
    conf: float = Form(0.25),
    iou: float = Form(0.45),
    imgsz: int = Form(640),
    classes: Optional[str] = Form(None),
):
    """Runs inference and streams back the annotated image directly as a PNG."""
    try:
        if hasattr(file, "file"):
            if hasattr(file.file, "seek"):
                file.file.seek(0)
            contents = file.file.read()
        else:
            contents = await file.read()
        if not contents:
            raise ValueError("Uploaded image file is empty.")
        image = Image.open(BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    allowed_classes_list = _parse_allowed_classes(classes)

    try:
        response = model_manager.predict(
            image=image,
            conf=conf,
            iou=iou,
            imgsz=imgsz,
            allowed_classes=allowed_classes_list,
            return_annotated=True,
        )
        if not response.annotated_image_base64:
            raise HTTPException(status_code=500, detail="Failed to generate annotated image")

        # Decode base64 to bytes
        import base64
        b64_data = response.annotated_image_base64.split(",", 1)[1]
        img_bytes = base64.b64decode(b64_data)
        return StreamingResponse(BytesIO(img_bytes), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    """Serves the interactive single-page CAD floor plan inspection UI."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>FloorCAD YOLOv8n API is running. <a href='/docs'>View Docs</a></h1>")
