from __future__ import annotations

import pytest
import yaml

from src.config import (
    AlertsConfig,
    CameraConfig,
    LoggingConfig,
    ModelConfig,
    PrivacyConfig,
    RecognitionConfig,
    TemporalConfirmationConfig,
    _parse_config,
    load_config,
)


def test_camera_defaults() -> None:
    cfg = CameraConfig()
    assert cfg.source == 0
    assert cfg.width == 640
    assert cfg.height == 480
    assert cfg.target_fps == 15
    assert cfg.process_every_n_frames == 2
    assert cfg.mirror_preview is True


def test_model_defaults() -> None:
    cfg = ModelConfig()
    assert cfg.provider == "CPUExecutionProvider"
    assert cfg.detection_size == [640, 640]
    assert cfg.minimum_detection_confidence == 0.60
    assert cfg.minimum_face_width == 70
    assert cfg.minimum_face_height == 70


def test_recognition_defaults() -> None:
    cfg = RecognitionConfig()
    assert cfg.similarity_threshold == 0.45
    assert cfg.identity_margin == 0.05
    assert cfg.top_k_average == 1
    assert cfg.unknown_label == "Unknown"


def test_temporal_defaults() -> None:
    cfg = TemporalConfirmationConfig()
    assert cfg.history_size == 6
    assert cfg.required_matches == 4
    assert cfg.maximum_gap_seconds == 2.0


def test_alerts_defaults() -> None:
    cfg = AlertsConfig()
    assert cfg.enabled is True
    assert cfg.cooldown_seconds == 60
    assert cfg.popup_title == "Person Alert"
    assert cfg.save_snapshot is False


def test_logging_defaults() -> None:
    cfg = LoggingConfig()
    assert cfg.enabled is True
    assert cfg.event_file == "data/logs/events.csv"
    assert cfg.log_unknown_people is False


def test_privacy_defaults() -> None:
    cfg = PrivacyConfig()
    assert cfg.store_live_frames is False
    assert cfg.store_unknown_faces is False


def test_parse_valid_full_config() -> None:
    raw = {
        "camera": {"source": 0, "width": 800, "height": 600},
        "model": {"provider": "CPUExecutionProvider"},
        "recognition": {"similarity_threshold": 0.5},
        "temporal_confirmation": {"history_size": 8, "required_matches": 5},
        "alerts": {"cooldown_seconds": 30},
        "logging": {"enabled": False},
        "privacy": {"store_live_frames": True},
    }
    cfg = _parse_config(raw)
    assert cfg.camera.width == 800
    assert cfg.camera.height == 600
    assert cfg.model.provider == "CPUExecutionProvider"
    assert cfg.recognition.similarity_threshold == 0.5
    assert cfg.temporal_confirmation.history_size == 8
    assert cfg.temporal_confirmation.required_matches == 5
    assert cfg.alerts.cooldown_seconds == 30
    assert cfg.logging.enabled is False
    assert cfg.privacy.store_live_frames is True


def test_parse_empty_sections_use_defaults() -> None:
    raw = {}
    cfg = _parse_config(raw)
    assert cfg.camera.width == 640
    assert cfg.model.provider == "CPUExecutionProvider"
    assert cfg.recognition.similarity_threshold == 0.45
    assert cfg.temporal_confirmation.history_size == 6
    assert cfg.alerts.cooldown_seconds == 60


def test_load_config_file_not_found() -> None:
    try:
        load_config("/nonexistent/config.yaml")
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_load_invalid_yaml(tmp_path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text(": invalid yaml")
    try:
        load_config(str(p))
        assert False, "Expected exception"
    except Exception:
        pass


def test_parse_non_dict_raises(tmp_path) -> None:
    p = tmp_path / "list.yaml"
    yaml.dump(["a", "b"], p.open("w"))
    try:
        load_config(str(p))
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_camera_width_out_of_range() -> None:
    try:
        CameraConfig(width=100)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_camera_height_out_of_range() -> None:
    try:
        CameraConfig(height=5000)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_camera_target_fps_out_of_range() -> None:
    try:
        CameraConfig(target_fps=200)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_camera_process_every_n_frames_zero() -> None:
    try:
        CameraConfig(process_every_n_frames=0)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_model_confidence_out_of_range() -> None:
    try:
        ModelConfig(minimum_detection_confidence=1.5)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_model_face_width_too_small() -> None:
    try:
        ModelConfig(minimum_face_width=5)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_recognition_threshold_out_of_range() -> None:
    try:
        RecognitionConfig(similarity_threshold=-0.1)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_recognition_margin_out_of_range() -> None:
    try:
        RecognitionConfig(identity_margin=3.0)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_temporal_required_exceeds_history() -> None:
    try:
        TemporalConfirmationConfig(history_size=4, required_matches=5)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_alerts_cooldown_negative() -> None:
    try:
        AlertsConfig(cooldown_seconds=-1)
        assert False, "Expected ValueError"
    except ValueError:
        pass


# --- New regression tests for review fixes ---

def test_model_detection_size_wrong_type() -> None:
    try:
        ModelConfig(detection_size="640,640")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_model_detection_size_wrong_length() -> None:
    try:
        ModelConfig(detection_size=[640])
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_model_detection_size_too_small() -> None:
    try:
        ModelConfig(detection_size=[32, 32])
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_parse_unknown_camera_key_raises() -> None:
    raw = {"camera": {"wifth": 800}}
    try:
        _parse_config(raw)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "wifth" in str(exc)


def test_parse_unknown_recognition_key_raises() -> None:
    raw = {"recognition": {"similiarity_threshold": 0.5}}
    try:
        _parse_config(raw)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "similiarity_threshold" in str(exc)


def test_parse_unknown_top_level_key_raises() -> None:
    raw = {"camera": {}, "database": {}}
    try:
        _parse_config(raw)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "database" in str(exc)



