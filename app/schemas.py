from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x1: float = Field(..., description="Top-left X coordinate in pixels")
    y1: float = Field(..., description="Top-left Y coordinate in pixels")
    x2: float = Field(..., description="Bottom-right X coordinate in pixels")
    y2: float = Field(..., description="Bottom-right Y coordinate in pixels")
    width: float = Field(..., description="Width in pixels")
    height: float = Field(..., description="Height in pixels")


class NormalizedBoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    width: float
    height: float


class DetectionItem(BaseModel):
    id: int = Field(..., description="Unique detection index")
    class_id: int = Field(..., description="Class ID")
    class_name: str = Field(..., description="Class name of the detected symbol")
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0")
    bbox: BoundingBox = Field(..., description="Bounding box in pixel coordinates")
    bbox_norm: NormalizedBoundingBox = Field(..., description="Bounding box normalized [0.0 - 1.0]")


class ImageDimensions(BaseModel):
    width: int
    height: int


class DetectionSummary(BaseModel):
    total_detections: int
    class_counts: Dict[str, int]
    inference_time_ms: float


class PredictionResponse(BaseModel):
    success: bool
    image_dimensions: ImageDimensions
    detections: List[DetectionItem]
    summary: DetectionSummary
    annotated_image_base64: Optional[str] = Field(
        None, description="Base64 encoded PNG of the annotated floor plan"
    )


class ModelInfoResponse(BaseModel):
    model_name: str
    repo_id: str
    device: str
    num_classes: int
    classes: Dict[int, str]
    task: str = "detect"
