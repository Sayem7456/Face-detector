from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import numpy.typing as npt

from src.config import AppConfig, load_config


@dataclass
class DetectionResult:
    bbox: tuple[int, int, int, int]
    detection_score: float
    embedding: Any
    face_width: int
    face_height: int


class FaceEngine:
    def __init__(self, config: AppConfig | None = None) -> None:
        if config is None:
            config = load_config()
        self.config = config
        self._model = self._load_model()

    def _load_model(self) -> Any:
        import insightface
        from insightface.app import FaceAnalysis

        app = FaceAnalysis(
            providers=[self.config.model.provider],
            allowed_modules=["detection", "recognition"],
        )
        ctx_id = 0 if self.config.model.provider == "CPUExecutionProvider" else 0
        app.prepare(ctx_id=ctx_id, det_size=self.config.model.detection_size)
        return app

    def detect_and_embed(
        self, frame: npt.NDArray[np.uint8]
    ) -> list[DetectionResult]:
        faces = self._model.get(frame)
        results: list[DetectionResult] = []
        cfg = self.config.model

        for face in faces:
            bbox = face.bbox.astype(int)
            x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
            fw = x2 - x1
            fh = y2 - y1

            if fw < cfg.minimum_face_width or fh < cfg.minimum_face_height:
                continue
            if face.det_score < cfg.minimum_detection_confidence:
                continue

            embedding = face.normed_embedding
            results.append(
                DetectionResult(
                    bbox=(int(x1), int(y1), int(x2), int(y2)),
                    detection_score=float(face.det_score),
                    embedding=embedding,
                    face_width=int(fw),
                    face_height=int(fh),
                )
            )

        return results

    def __repr__(self) -> str:
        return (
            f"FaceEngine(provider={self.config.model.provider}, "
            f"det_size={self.config.model.detection_size})"
        )
