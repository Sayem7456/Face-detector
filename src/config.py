from __future__ import annotations

from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any

import yaml


@dataclass
class CameraConfig:
    source: int | str = 0
    width: int = 640
    height: int = 480
    target_fps: int = 15
    process_every_n_frames: int = 2
    mirror_preview: bool = True

    def __post_init__(self) -> None:
        if self.width < 160 or self.width > 4096:
            raise ValueError(
                f"camera.width must be between 160 and 4096, got {self.width}"
            )
        if self.height < 120 or self.height > 4096:
            raise ValueError(
                f"camera.height must be between 120 and 4096, got {self.height}"
            )
        if self.target_fps < 1 or self.target_fps > 120:
            raise ValueError(
                f"camera.target_fps must be between 1 and 120, got {self.target_fps}"
            )
        if self.process_every_n_frames < 1:
            raise ValueError(
                f"camera.process_every_n_frames must be >= 1, got "
                f"{self.process_every_n_frames}"
            )


@dataclass
class ModelConfig:
    provider: str = "CPUExecutionProvider"
    detection_size: list[int] = field(default_factory=lambda: [640, 640])
    minimum_detection_confidence: float = 0.60
    minimum_face_width: int = 70
    minimum_face_height: int = 70

    def __post_init__(self) -> None:
        if not isinstance(self.provider, str) or not self.provider.strip():
            raise ValueError(
                f"model.provider must be a non-empty string, got {self.provider!r}"
            )
        if (
            self.minimum_detection_confidence < 0.0
            or self.minimum_detection_confidence > 1.0
        ):
            raise ValueError(
                f"model.minimum_detection_confidence must be between 0.0 and 1.0, "
                f"got {self.minimum_detection_confidence}"
            )
        if self.minimum_face_width < 20:
            raise ValueError(
                f"model.minimum_face_width must be >= 20, got {self.minimum_face_width}"
            )
        if self.minimum_face_height < 20:
            raise ValueError(
                f"model.minimum_face_height must be >= 20, got "
                f"{self.minimum_face_height}"
            )
        if not isinstance(self.detection_size, list) or len(self.detection_size) != 2:
            raise ValueError(
                f"model.detection_size must be a list of two ints, got "
                f"{self.detection_size!r}"
            )
        if not all(isinstance(v, int) and v >= 64 for v in self.detection_size):
            raise ValueError(
                f"model.detection_size values must be ints >= 64, got "
                f"{self.detection_size}"
            )


@dataclass
class RecognitionConfig:
    similarity_threshold: float = 0.45
    identity_margin: float = 0.05
    top_k_average: int = 1
    unknown_label: str = "Unknown"

    def __post_init__(self) -> None:
        if self.similarity_threshold < 0.0 or self.similarity_threshold > 2.0:
            raise ValueError(
                f"recognition.similarity_threshold must be between 0.0 and 2.0, "
                f"got {self.similarity_threshold}"
            )
        if self.identity_margin < 0.0 or self.identity_margin > 2.0:
            raise ValueError(
                f"recognition.identity_margin must be between 0.0 and 2.0, "
                f"got {self.identity_margin}"
            )
        if self.top_k_average < 1:
            raise ValueError(
                f"recognition.top_k_average must be >= 1, got {self.top_k_average}"
            )


@dataclass
class TemporalConfirmationConfig:
    history_size: int = 6
    required_matches: int = 4
    maximum_gap_seconds: float = 2.0

    def __post_init__(self) -> None:
        if self.history_size < 1:
            raise ValueError(
                f"temporal_confirmation.history_size must be >= 1, got "
                f"{self.history_size}"
            )
        if self.required_matches < 1:
            raise ValueError(
                f"temporal_confirmation.required_matches must be >= 1, got "
                f"{self.required_matches}"
            )
        if self.required_matches > self.history_size:
            raise ValueError(
                f"temporal_confirmation.required_matches ({self.required_matches}) "
                f"cannot exceed history_size ({self.history_size})"
            )
        if self.maximum_gap_seconds < 0.0:
            raise ValueError(
                f"temporal_confirmation.maximum_gap_seconds must be >= 0, got "
                f"{self.maximum_gap_seconds}"
            )


@dataclass
class AlertsConfig:
    enabled: bool = True
    cooldown_seconds: int = 60
    popup_title: str = "Person Alert"
    save_snapshot: bool = False
    snapshot_directory: str = "data/logs/snapshots"

    def __post_init__(self) -> None:
        if self.cooldown_seconds < 0:
            raise ValueError(
                f"alerts.cooldown_seconds must be >= 0, got {self.cooldown_seconds}"
            )


@dataclass
class LoggingConfig:
    enabled: bool = True
    event_file: str = "data/logs/events.csv"
    log_unknown_people: bool = False


@dataclass
class PrivacyConfig:
    store_live_frames: bool = False
    store_unknown_faces: bool = False


@dataclass
class AppConfig:
    camera: CameraConfig = field(default_factory=CameraConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    recognition: RecognitionConfig = field(default_factory=RecognitionConfig)
    temporal_confirmation: TemporalConfirmationConfig = field(
        default_factory=TemporalConfirmationConfig
    )
    alerts: AlertsConfig = field(default_factory=AlertsConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    privacy: PrivacyConfig = field(default_factory=PrivacyConfig)


_TOP_LEVEL_SECTIONS = {
    "camera", "model", "recognition", "temporal_confirmation",
    "alerts", "logging", "privacy",
}


def _field_names(cls: type) -> set[str]:
    return {f.name for f in fields(cls)}


def _check_unknown_keys(
    section: str, raw: dict[str, Any], known: set[str]
) -> None:
    extra = set(raw.keys()) - known
    if extra:
        raise ValueError(
            f"Unknown key(s) in '{section}': {', '.join(sorted(extra))}. "
            f"Valid keys: {', '.join(sorted(known))}"
        )


def _validate_paths(config: AppConfig) -> None:
    if config.logging.enabled:
        log_path = Path(config.logging.event_file)
        if log_path.suffix.lower() != ".csv":
            raise ValueError(
                f"logging.event_file must have a .csv extension, got "
                f"{config.logging.event_file}"
            )


def load_config(path: str | Path = "config.yaml") -> AppConfig:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    raw: dict[str, Any]
    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError(
            f"Configuration file must contain a top-level mapping, "
            f"got {type(raw).__name__}"
        )

    return _parse_config(raw)


def _parse_config(raw: dict[str, Any]) -> AppConfig:
    _check_unknown_keys("top-level", raw, _TOP_LEVEL_SECTIONS)

    camera_raw = raw.get("camera", {})
    if not isinstance(camera_raw, dict):
        raise ValueError("'camera' section must be a mapping")
    _check_unknown_keys("camera", camera_raw, _field_names(CameraConfig))
    camera = CameraConfig(**camera_raw)

    model_raw = raw.get("model", {})
    if not isinstance(model_raw, dict):
        raise ValueError("'model' section must be a mapping")
    _check_unknown_keys("model", model_raw, _field_names(ModelConfig))
    model = ModelConfig(**model_raw)

    recognition_raw = raw.get("recognition", {})
    if not isinstance(recognition_raw, dict):
        raise ValueError("'recognition' section must be a mapping")
    _check_unknown_keys(
        "recognition", recognition_raw, _field_names(RecognitionConfig)
    )
    recognition = RecognitionConfig(**recognition_raw)

    temporal_raw = raw.get("temporal_confirmation", {})
    if not isinstance(temporal_raw, dict):
        raise ValueError("'temporal_confirmation' section must be a mapping")
    _check_unknown_keys(
        "temporal_confirmation", temporal_raw, _field_names(TemporalConfirmationConfig)
    )
    temporal = TemporalConfirmationConfig(**temporal_raw)

    alerts_raw = raw.get("alerts", {})
    if not isinstance(alerts_raw, dict):
        raise ValueError("'alerts' section must be a mapping")
    _check_unknown_keys("alerts", alerts_raw, _field_names(AlertsConfig))
    alerts = AlertsConfig(**alerts_raw)

    logging_raw = raw.get("logging", {})
    if not isinstance(logging_raw, dict):
        raise ValueError("'logging' section must be a mapping")
    _check_unknown_keys("logging", logging_raw, _field_names(LoggingConfig))
    logging_cfg = LoggingConfig(**logging_raw)

    privacy_raw = raw.get("privacy", {})
    if not isinstance(privacy_raw, dict):
        raise ValueError("'privacy' section must be a mapping")
    _check_unknown_keys("privacy", privacy_raw, _field_names(PrivacyConfig))
    privacy = PrivacyConfig(**privacy_raw)

    cfg = AppConfig(
        camera=camera,
        model=model,
        recognition=recognition,
        temporal_confirmation=temporal,
        alerts=alerts,
        logging=logging_cfg,
        privacy=privacy,
    )
    _validate_paths(cfg)
    return cfg
