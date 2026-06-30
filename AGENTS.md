# Face Detector — Repository Rules

## First action in every session

Read `docs/plan.md` — it is the authoritative project specification. The `docs/` directory is gitignored (`.gitignore` pattern: `\docs`), so git will not report changes inside it. You **must** read it explicitly.

## Implementation workflow

- Use the phase prompts in `docs/opencode-prompts.md` sequentially (read `docs/plan.md` first).
- Start a fresh session per phase. Never run multiple phases at once.
- Commit after each completed phase. Do not commit between phases.
- The repo has **zero commits** — no source code exists yet. Treat every file you create as new.

## Technology stack

- Python 3.11+ (latest in `3.11` series)
- **CPU only** — no CUDA, no GPU. Use `CPUExecutionProvider` explicitly everywhere.
- **No model training** — pretrained InsightFace embedding model only.
- Core deps: `opencv-python`, `insightface`, `onnxruntime`, `numpy`, `pyyaml`, `pillow`
- Desktop notifications: `notify-send` (Ubuntu `libnotify-bin`)

## Privacy & data (do NOT commit)

- `data/reference_images/` — face images
- `data/embeddings/` — `.npz` embedding files
- `data/logs/`, `data/snapshots/` — events and snapshots
- `data/calibration/` — calibration images
- Model cache files (`.insightface/` models)

None of these paths have `.gitignore` entries yet. Add them as needed.

## Testing rules

- Mock hardware: camera, desktop notifications (`subprocess`), time (`monotonic` clocks)
- Hardware-dependent tests must be marked manual/skip — never fail unit suites
- No test may require real biometric images, a webcam, or a downloaded model
- Use synthetic normalized vectors for matcher tests
- Prefer deterministic, time-independent assertions

## Code conventions

- Type hints on all public functions and classes (not required on trivial `__init__` or private helpers)
- `pathlib.Path` over string concatenation for paths
- Core data models: `dataclasses` or `TypedDict`
- `shell=False` for all `subprocess` calls (always pass argument lists)
- Recognize-only, no classifier training
- Never log or print raw embedding vectors
