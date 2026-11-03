# FloorCAD YOLOv8n — FastAPI & Interactive Web Visualizer

High-performance REST API and interactive CAD visualizer for detecting architectural symbols and layout elements in floor plan drawings, powered by [`mudasir13cs/floorcad-yolov8n-detect`](https://huggingface.co/mudasir13cs/floorcad-yolov8n-detect).

---

## 🌟 Key Features

### ⚡ FastAPI High-Performance Backend
- **Ultralytics YOLOv8n FloorCAD Engine:** Automatically loaded and optimized via ONNX Runtime for blazing-fast inference (~80ms latency).
- **Full 35-Class Architectural Symbol Detection:** Detects doors, windows, walls, stairs, elevators, furniture, and bathroom fixtures.
- **RESTful Endpoints:**
  - `POST /api/predict`: Returns structured JSON detection coordinates (pixel + normalized), confidence scores, class summaries, and base64 rendered preview.
  - `POST /api/predict/image`: Streams back the annotated floor plan PNG directly.
  - `GET /api/info` & `GET /api/classes`: Model metadata and 35-symbol dictionary.
  - `GET /api/samples`: Built-in demo floor plans for instant 1-click testing.
  - `GET /api/health`: Health status, device backend, and model status.
- **Interactive OpenAPI Documentation:** Available at `/docs` (Swagger UI) and `/redoc`.

### 🖥️ Interactive CAD Web Visualizer
- **Single-Page CAD Interface:** Served directly at `http://127.0.0.1:8000/`.
- **CAD Canvas with Pan & Zoom:** Smooth mouse-wheel zooming (up to 1000%) and drag-to-pan to inspect high-resolution CAD schematics.
- **View Modes:**
  - **Interactive CAD View:** Dynamic vector bounding boxes with hover tooltips and CAD corner brackets.
  - **Split Comparison:** Side-by-side view comparing original floor plan with the YOLO detection output.
  - **Annotated Render:** Raw high-res rendered image from the backend.
- **Symbol Schedule & Detection Inspector:** Scrollable inspector table; clicking or hovering any row immediately spotlights and flashes that element on the floor plan.
- **Class Filtering & Search:** Search and toggle individual symbols or categories (Doors, Windows, Furniture, Sanitary, Vertical circulation, Structural).
- **Exporting Options:**
  - Download Annotated PNG
  - Export Detections (JSON)
  - Export Symbol Schedule (CSV)

---

## 📐 Supported 35 Architectural Symbols

| Category | Classes |
| :--- | :--- |
| **Openings & Doors** | `single_door`, `double_door`, `sliding_door`, `opening_symbol` |
| **Windows** | `window`, `bay_window`, `blind_window` |
| **Circulation & Transport** | `elevator`, `escalator`, `stair`, `parking`, `railing` |
| **Furniture** | `bed`, `bedside_cupboard`, `chair`, `sofa`, `table`, `wardrobe`, `tv_cabinet`, `half_height_cabinet`, `high_cabinet` |
| **Sanitary & Wet Area** | `bath`, `bath_tub`, `toilet`, `squat_toilet`, `urinal`, `sink`, `washing_machine` |
| **Kitchen & Appliances** | `gas_stove`, `refrigerator` |
| **Structure & Boundary** | `wall`, `class_31`, `class_32`, `class_34`, `class_35` |

---

## 🚀 Quick Start

### 1. Activate Environment & Install Dependencies

```bash
# Activate the existing virtual environment (Python 3.11)
.\.venv\Scripts\activate

# Or install dependencies from requirements.txt
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python run.py --port 8000 --reload
```

Open your browser at:
- **Interactive Web UI:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Swagger API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📡 API Usage Examples

### 1. JSON Detections (`POST /api/predict`)

```bash
curl -X POST "http://127.0.0.1:8000/api/predict" \
  -F "file=@app/samples/demo_cad_floorplan.png" \
  -F "conf=0.25" \
  -F "iou=0.45" \
  -F "imgsz=640"
```

**Sample Response:**
```json
{
  "success": true,
  "image_dimensions": { "width": 1600, "height": 1100 },
  "summary": {
    "total_detections": 8,
    "class_counts": {
      "double_door": 4,
      "escalator": 1,
      "bath": 1,
      "parking": 1,
      "wall": 1
    },
    "inference_time_ms": 81.89
  },
  "detections": [
    {
      "id": 1,
      "class_id": 11,
      "class_name": "double_door",
      "confidence": 0.9654,
      "bbox": {
        "x1": 520.12,
        "y1": 310.45,
        "x2": 600.48,
        "y2": 393.56,
        "width": 80.36,
        "height": 83.11
      },
      "bbox_norm": {
        "x1": 0.3251,
        "y1": 0.2822,
        "x2": 0.3753,
        "y2": 0.3578,
        "width": 0.0502,
        "height": 0.0756
      }
    }
  ],
  "annotated_image_base64": "data:image/png;base64,..."
}
```

### 2. Stream Annotated Image Directly (`POST /api/predict/image`)

```bash
curl -X POST "http://127.0.0.1:8000/api/predict/image" \
  -F "file=@app/samples/demo_cad_floorplan.png" \
  --output annotated_output.png
```

---

## 🧪 Automated Tests

Run the test suite with pytest:

```bash
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

All 6 test cases verify endpoints, model loading, class mappings, demo samples, and detection accuracy.
