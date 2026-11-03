import os
from PIL import Image

from app.main import (
    health_check,
    get_model_info,
    get_classes,
    list_samples,
    serve_frontend,
)
from app.model import FloorCADModelManager

SAMPLE_IMG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "samples", "demo_cad_floorplan.png")


def test_health():
    res = health_check()
    assert res["status"] == "healthy"
    assert "device" in res
    assert "repo_id" in res


def test_info():
    info = get_model_info()
    assert info.model_name == "FloorCAD YOLOv8n Detect"
    assert info.num_classes == 35
    assert len(info.classes) == 35


def test_classes():
    data = get_classes()
    assert data["total"] == 35
    assert "double_door" in data["classes"].values()
    assert "window" in data["classes"].values()


def test_samples_list():
    res = list_samples()
    assert "samples" in res
    assert len(res["samples"]) >= 1


def test_frontend_serve():
    res = serve_frontend()
    assert res.status_code == 200
    assert "FloorCAD" in res.body.decode("utf-8")


def test_model_prediction():
    manager = FloorCADModelManager.get_instance()
    img = Image.open(SAMPLE_IMG_PATH)
    res = manager.predict(img, conf=0.25, iou=0.45)
    assert res.success is True
    assert res.summary.total_detections > 0
    assert len(res.detections) > 0
    assert res.annotated_image_base64.startswith("data:image/png;base64,")
