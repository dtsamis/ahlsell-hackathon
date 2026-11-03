import os
import time
import base64
import logging
from io import BytesIO
from typing import Dict, List, Optional, Tuple, Any

import cv2
import numpy as np
from PIL import Image, ImageDraw
import yaml
import onnxruntime as ort

from app.schemas import (
    BoundingBox,
    NormalizedBoundingBox,
    DetectionItem,
    DetectionSummary,
    ImageDimensions,
    PredictionResponse,
    ModelInfoResponse,
)

logger = logging.getLogger("floorcad.model")
logger.setLevel(logging.INFO)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEIGHTS_DIR = os.path.join(BASE_DIR, "weights")
ONNX_PATH = os.path.join(WEIGHTS_DIR, "floorcad-yolov8n-detect.onnx")
DATASET_YAML_PATH = os.path.join(BASE_DIR, "dataset.yaml")
REPO_ID = "mudasir13cs/floorcad-yolov8n-detect"

CATEGORY_COLORS = {
    # Doors & Openings: Cyan / Sky
    "single_door": (6, 182, 212),
    "double_door": (6, 182, 212),
    "sliding_door": (14, 165, 233),
    "opening_symbol": (56, 189, 248),
    # Windows: Sky Blue
    "window": (2, 132, 199),
    "bay_window": (12, 74, 110),
    "blind_window": (3, 105, 161),
    # Vertical circulation & transport: Emerald
    "elevator": (16, 185, 129),
    "escalator": (5, 150, 105),
    "stair": (52, 211, 153),
    "railing": (110, 231, 183),
    "parking": (4, 120, 87),
    # Furniture: Violet / Purple
    "bed": (168, 85, 247),
    "bedside_cupboard": (192, 132, 252),
    "chair": (147, 51, 234),
    "sofa": (126, 34, 206),
    "table": (192, 38, 211),
    "wardrobe": (217, 70, 239),
    "tv_cabinet": (162, 28, 175),
    "half_height_cabinet": (134, 25, 143),
    "high_cabinet": (112, 26, 117),
    # Sanitary & Wet Area: Rose
    "bath": (244, 63, 94),
    "bath_tub": (225, 29, 72),
    "toilet": (251, 113, 133),
    "squat_toilet": (244, 63, 94),
    "urinal": (190, 18, 60),
    "sink": (253, 164, 175),
    "washing_machine": (225, 29, 72),
    # Kitchen & Appliances: Amber
    "gas_stove": (245, 158, 11),
    "refrigerator": (217, 119, 6),
    # Structure: Orange
    "wall": (234, 88, 12),
}
DEFAULT_COLOR = (249, 115, 22)


class FloorCADModelManager:
    _instance: Optional["FloorCADModelManager"] = None

    def __init__(self):
        self.repo_id = REPO_ID
        self.session: Optional[ort.InferenceSession] = None
        self.classes: Dict[int, str] = {}
        self.is_loaded = False
        self.device = "CPU"
        self._load_classes()

    @classmethod
    def get_instance(cls) -> "FloorCADModelManager":
        if cls._instance is None:
            cls._instance = FloorCADModelManager()
        return cls._instance

    def _load_classes(self) -> None:
        """Loads class mapping from dataset.yaml."""
        if os.path.exists(DATASET_YAML_PATH):
            try:
                with open(DATASET_YAML_PATH, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    self.classes = {int(k): str(v) for k, v in data.get("names", {}).items()}
                    return
            except Exception as e:
                logger.warning("Could not read dataset.yaml: %s", e)

        # Fallback default 35 FloorCAD classes
        self.classes = {
            0: "bath", 1: "bath_tub", 2: "bay_window", 3: "bed", 4: "bedside_cupboard",
            5: "blind_window", 6: "chair", 7: "class_31", 8: "class_32", 9: "class_34",
            10: "class_35", 11: "double_door", 12: "elevator", 13: "escalator", 14: "gas_stove",
            15: "half_height_cabinet", 16: "high_cabinet", 17: "opening_symbol", 18: "parking",
            19: "railing", 20: "refrigerator", 21: "single_door", 22: "sink", 23: "sliding_door",
            24: "sofa", 25: "squat_toilet", 26: "stair", 27: "table", 28: "toilet",
            29: "tv_cabinet", 30: "urinal", 31: "wall", 32: "wardrobe", 33: "washing_machine",
            34: "window",
        }

    def load_model(self) -> None:
        """Loads the ONNX Runtime session."""
        if self.is_loaded and self.session is not None:
            return

        if not os.path.exists(ONNX_PATH):
            from scripts.convert_pt_to_onnx import convert
            convert()

        available_providers = ort.get_available_providers()
        logger.info("Available ONNX Runtime providers: %s", available_providers)

        providers = []
        if "CUDAExecutionProvider" in available_providers:
            providers.append("CUDAExecutionProvider")
            self.device = "CUDA (RTX 4050 GPU)"
        else:
            self.device = "CPU (Optimized SIMD)"
        providers.append("CPUExecutionProvider")

        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        self.session = ort.InferenceSession(ONNX_PATH, sess_options=sess_options, providers=providers)
        self.is_loaded = True
        logger.info("FloorCAD YOLOv8n ONNX model loaded successfully on %s", self.device)

    def get_info(self) -> ModelInfoResponse:
        if not self.is_loaded:
            self.load_model()
        return ModelInfoResponse(
            model_name="FloorCAD YOLOv8n Detect",
            repo_id=self.repo_id,
            device=self.device,
            num_classes=len(self.classes),
            classes=self.classes,
            task="detect",
        )

    @staticmethod
    def _letterbox(img: np.ndarray, target_size: int = 640) -> Tuple[np.ndarray, float, Tuple[float, float]]:
        """Resize and pad image while meeting target_size stride constraints."""
        h, w = img.shape[:2]
        r = min(target_size / h, target_size / w)
        new_unpad_w, new_unpad_h = int(round(w * r)), int(round(h * r))
        dw, dh = (target_size - new_unpad_w) / 2, (target_size - new_unpad_h) / 2

        if (w, h) != (new_unpad_w, new_unpad_h):
            img_resized = cv2.resize(img, (new_unpad_w, new_unpad_h), interpolation=cv2.INTER_LINEAR)
        else:
            img_resized = img

        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        img_padded = cv2.copyMakeBorder(
            img_resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114)
        )
        return img_padded, r, (dw, dh)

    def predict(
        self,
        image: Image.Image,
        conf: float = 0.25,
        iou: float = 0.45,
        imgsz: int = 640,
        allowed_classes: Optional[List[int]] = None,
        return_annotated: bool = True,
    ) -> PredictionResponse:
        if not self.is_loaded:
            self.load_model()

        start_time = time.perf_counter()

        if image.mode != "RGB":
            image = image.convert("RGB")
        img_np = np.array(image)
        orig_h, orig_w = img_np.shape[:2]

        # Letterbox preprocessing to 640x640
        img_letterboxed, ratio, (dw, dh) = self._letterbox(img_np, target_size=640)

        # Transpose to (1, 3, H, W) and normalize [0, 1]
        input_tensor = (img_letterboxed.transpose(2, 0, 1) / 255.0).astype(np.float32)[None, ...]

        # Run ONNX inference
        outputs = self.session.run(None, {"images": input_tensor})[0]  # shape: (1, 39, 8400)
        preds = outputs[0].T  # shape: (8400, 39)

        raw_boxes = preds[:, :4]  # cx, cy, w, h
        raw_scores = preds[:, 4:]  # (8400, 35)

        max_scores = np.max(raw_scores, axis=1)
        max_classes = np.argmax(raw_scores, axis=1)

        conf_mask = max_scores >= conf
        if allowed_classes is not None and len(allowed_classes) > 0:
            class_mask = np.isin(max_classes, allowed_classes)
            valid_mask = conf_mask & class_mask
        else:
            valid_mask = conf_mask

        cand_boxes = raw_boxes[valid_mask]
        cand_scores = max_scores[valid_mask]
        cand_classes = max_classes[valid_mask]

        detections: List[DetectionItem] = []
        class_counts: Dict[str, int] = {}

        if len(cand_boxes) > 0:
            cx = (cand_boxes[:, 0] - dw) / ratio
            cy = (cand_boxes[:, 1] - dh) / ratio
            w_box = cand_boxes[:, 2] / ratio
            h_box = cand_boxes[:, 3] / ratio

            x1 = np.clip(cx - w_box / 2, 0, orig_w)
            y1 = np.clip(cy - h_box / 2, 0, orig_h)
            x2 = np.clip(cx + w_box / 2, 0, orig_w)
            y2 = np.clip(cy + h_box / 2, 0, orig_h)

            w_clean = np.maximum(0.0, x2 - x1)
            h_clean = np.maximum(0.0, y2 - y1)

            cv_boxes = [[int(a), int(b), int(c), int(d)] for a, b, c, d in zip(x1, y1, w_clean, h_clean)]
            indices = cv2.dnn.NMSBoxes(
                cv_boxes,
                cand_scores.tolist(),
                score_threshold=float(conf),
                nms_threshold=float(iou),
            )

            det_id = 1
            if len(indices) > 0:
                for item in indices:
                    idx = int(item[0]) if isinstance(item, (list, tuple, np.ndarray)) else int(item)
                    class_idx = int(cand_classes[idx])
                    score_val = round(float(cand_scores[idx]), 4)
                    class_name = self.classes.get(class_idx, f"symbol_{class_idx}")

                    bx1 = round(float(x1[idx]), 2)
                    by1 = round(float(y1[idx]), 2)
                    bx2 = round(float(x2[idx]), 2)
                    by2 = round(float(y2[idx]), 2)
                    bw = round(float(w_clean[idx]), 2)
                    bh = round(float(h_clean[idx]), 2)

                    class_counts[class_name] = class_counts.get(class_name, 0) + 1

                    detections.append(
                        DetectionItem(
                            id=det_id,
                            class_id=class_idx,
                            class_name=class_name,
                            confidence=score_val,
                            bbox=BoundingBox(
                                x1=bx1, y1=by1, x2=bx2, y2=by2, width=bw, height=bh
                            ),
                            bbox_norm=NormalizedBoundingBox(
                                x1=round(bx1 / orig_w, 4),
                                y1=round(by1 / orig_h, 4),
                                x2=round(bx2 / orig_w, 4),
                                y2=round(by2 / orig_h, 4),
                                width=round(bw / orig_w, 4),
                                height=round(bh / orig_h, 4),
                            ),
                        )
                    )
                    det_id += 1

        inference_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        annotated_b64: Optional[str] = None
        if return_annotated:
            annotated_img = image.copy()
            draw = ImageDraw.Draw(annotated_img)

            for det in detections:
                color = CATEGORY_COLORS.get(det.class_name, DEFAULT_COLOR)
                box = [det.bbox.x1, det.bbox.y1, det.bbox.x2, det.bbox.y2]
                draw.rectangle(box, outline=color, width=3)

                label_text = f"{det.class_name} {int(det.confidence * 100)}%"
                text_bbox = draw.textbbox((det.bbox.x1, det.bbox.y1), label_text)
                text_w = text_bbox[2] - text_bbox[0]
                text_h = text_bbox[3] - text_bbox[1]

                label_bg = [
                    det.bbox.x1,
                    max(0, det.bbox.y1 - text_h - 4),
                    det.bbox.x1 + text_w + 6,
                    det.bbox.y1,
                ]
                draw.rectangle(label_bg, fill=color)
                draw.text(
                    (det.bbox.x1 + 3, max(0, det.bbox.y1 - text_h - 2)),
                    label_text,
                    fill=(255, 255, 255),
                )

            buffered = BytesIO()
            annotated_img.save(buffered, format="PNG", optimize=True)
            annotated_b64 = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")

        summary = DetectionSummary(
            total_detections=len(detections),
            class_counts=class_counts,
            inference_time_ms=inference_time_ms,
        )

        return PredictionResponse(
            success=True,
            image_dimensions=ImageDimensions(width=orig_w, height=orig_h),
            detections=detections,
            summary=summary,
            annotated_image_base64=annotated_b64,
        )
