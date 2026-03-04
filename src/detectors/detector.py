import os
import logging
from ultralytics import YOLO
from configs.config import MODEL_NAME, MODEL_CONF, MODEL_CLASSES

logger = logging.getLogger(__name__)


class Detector:
    """
    YOLOv8 person detector.
    Automatically exports and loads ONNX for faster CPU inference when available.
    """

    def __init__(self):
        base_name = os.path.splitext(MODEL_NAME)[0]
        onnx_path = f"{base_name}.onnx"

        if os.path.exists(onnx_path):
            logger.info(f"Loading ONNX model: {onnx_path}")
            self.model = YOLO(onnx_path, task="detect")
        else:
            logger.info(f"Loading PyTorch model: {MODEL_NAME}")
            self.model = YOLO(MODEL_NAME)

            # Auto-export to ONNX for next startup (significantly faster on CPU)
            try:
                logger.info("Exporting model to ONNX for faster inference...")
                self.model.export(format="onnx", imgsz=640, simplify=True)
                if os.path.exists(onnx_path):
                    logger.info(f"ONNX export successful → {onnx_path}. Will use ONNX on next run.")
            except Exception as e:
                logger.warning(f"ONNX export failed (will continue with PyTorch): {e}")

        logger.info(f"Detector ready. Conf: {MODEL_CONF}, Classes: {MODEL_CLASSES}")

    def detect(self, frame):
        """Run inference on a single frame and return results."""
        return self.model(frame, verbose=False, classes=MODEL_CLASSES, conf=MODEL_CONF, imgsz=640)