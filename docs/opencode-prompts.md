# OpenCode Implementation Prompts

This file contains phase-by-phase prompts for implementing the project defined in `docs/plan.md`.

Use the prompts sequentially. Start a fresh OpenCode session for each major phase when possible so the model focuses on the current scope. Do not run all phase prompts at once.

---

## How to Use This Prompt Pack

1. Place this file at:

```text
docs/opencode-prompts.md
```

2. Confirm that the main project plan exists at:

```text
docs/plan.md
```

3. Open OpenCode from the repository root.

4. Paste the **Repository Preflight Prompt** first.

5. Paste one phase prompt at a time.

6. Review the diff and test output before proceeding to the next phase.

7. Commit a completed phase before starting the next phase.

Recommended workflow:

```bash
opencode
```

Then paste:

```text
Repository Preflight Prompt
Phase 1 Prompt
Phase 2 Prompt
...
Final Integration Prompt
```

---

# Global Implementation Contract

The following rules are already repeated inside the phase prompts, but they can also be saved in an OpenCode project instruction file if desired.

```text
You are implementing a production-quality, local, CPU-friendly Python project.

Repository source of truth:
- Read docs/plan.md before making changes.
- Inspect the existing repository before writing code.
- Existing working behavior takes priority over assumptions.
- Do not invent files, functions, APIs, command results, model outputs, camera results, metrics, or test results.
- Verify third-party APIs against the installed package, package source, or official documentation available to you.
- If an API differs from an assumption, adapt the implementation to the installed version.

Engineering rules:
- Implement functional code, not pseudocode.
- Do not leave TODO, FIXME, pass, NotImplementedError, fake implementations, placeholder return values, or commented-out alternative implementations.
- Do not create dummy biometric images or fabricated calibration results.
- Do not silently weaken error handling to make tests pass.
- Use type hints for public functions and classes.
- Use pathlib instead of hard-coded path strings where practical.
- Use structured dataclasses or typed dictionaries for core data.
- Keep modules focused and avoid unnecessary abstractions.
- Preserve unrelated repository code.
- Never delete user files or reference images.
- Never commit secrets, models, biometric images, embeddings, logs, or snapshots.
- Avoid shell=True for subprocess execution.
- Keep all recognition processing local.
- Use CPUExecutionProvider explicitly unless configuration says otherwise.
- Prefer deterministic tests.
- Mock hardware, time, and desktop notifications in unit tests.
- Hardware-dependent tests must be reported as manual or skipped when the hardware is unavailable.
- Never report a test or command as successful unless it was actually run and succeeded.

Quality gates:
- Run relevant unit tests after each change.
- Run the complete test suite before finishing a phase when practical.
- Run Python compilation or import checks.
- Report exact commands executed and their exit status.
- Report files created or modified.
- Report unresolved limitations honestly.
- Do not begin the next phase automatically.
```

---

# Repository Preflight Prompt

Paste this before Phase 1.

```text
Act as the lead engineer for this repository.

The project specification is in docs/plan.md. This task is repository preflight only. Do not implement the full application yet.

Perform these steps:

1. Read docs/plan.md completely.
2. Inspect the repository structure, including hidden files that affect Python, Git, testing, formatting, or environment configuration.
3. Run git status and identify uncommitted changes without modifying or discarding them.
4. Identify:
   - Existing Python version requirements
   - Existing dependency files
   - Existing source and test layout
   - Existing configuration
   - Existing scripts
   - Existing CI or lint configuration
   - Conflicts between the repository and docs/plan.md
5. Determine whether the repository is empty, partially implemented, or already contains overlapping modules.
6. Produce a phase-by-phase implementation map that preserves existing work.
7. Identify risky assumptions, especially:
   - Camera availability
   - Ubuntu notify-send availability
   - InsightFace model availability
   - Internet-dependent model downloads
   - ONNX Runtime provider availability
   - Biometric data paths
8. Do not claim that hardware or model tests passed unless you actually ran them.
9. Do not modify code unless a minimal non-destructive fix is required to inspect the project. Prefer no changes during preflight.

Return:
- Current repository summary
- Relevant files found
- Conflicts with docs/plan.md
- Recommended implementation order
- Exact Phase 1 scope
- Commands inspected or executed
- Current git status

Stop after the preflight report. Do not implement Phase 1.
```

---

# Phase 1 Prompt: Environment and Camera Verification

```text
Implement Phase 1 from docs/plan.md: Environment and Camera Verification.

First:
1. Read docs/plan.md, especially Sections 1-8 and Phase 1.
2. Inspect the current repository and git status.
3. Reuse existing files and conventions where sound.
4. Do not overwrite unrelated user work.

Required implementation:

A. Project bootstrap
- Establish a clean Python package layout consistent with docs/plan.md.
- Add or update requirements.txt with the minimum runtime and development dependencies needed for this phase.
- Do not pin arbitrary versions without evidence. If versions are pinned, explain why and verify compatibility.
- Add a safe .gitignore covering:
  - .venv
  - Python caches
  - test caches
  - model caches where appropriate
  - data/reference_images contents
  - data/embeddings contents
  - data/logs contents
  - snapshots
  Preserve directory placeholders where useful.
- Add src/__init__.py and scripts/__init__.py only when appropriate.

B. Configuration foundation
- Add config.yaml containing the initial camera, model, recognition, temporal confirmation, alerts, logging, and privacy sections from the plan.
- Implement src/config.py with:
  - Typed configuration models using dataclasses or another lightweight validated approach already present in the project
  - YAML loading
  - Clear defaults
  - Validation of dimensions, frame interval, thresholds, provider name, cooldown, and paths
  - Helpful errors for missing or malformed configuration
- Do not introduce a heavy settings framework unless the repository already uses it.

C. Camera verification
- Implement scripts/test_camera.py.
- It must:
  - Accept camera source from CLI, defaulting to config
  - Open the camera safely
  - Set requested width and height where supported
  - Read frames
  - Display a preview when a desktop is available
  - Support a --no-preview mode
  - Print actual frame dimensions and measured frames received
  - Exit cleanly on q, Ctrl+C, camera failure, or timeout
  - Release the camera and destroy windows in finally blocks
- Do not claim the camera works if it is unavailable.

D. Desktop notification verification
- Implement a small notification adapter or scripts/test_notification.py.
- Detect whether notify-send exists.
- Invoke notify-send with subprocess using an argument list and shell=False.
- Return a useful nonzero exit code or message when unavailable.
- Do not make notification failure crash unrelated tests.

E. Face-model smoke test
- Implement scripts/test_face_model.py.
- Load the configured InsightFace face-analysis pipeline using CPUExecutionProvider.
- Centralize model initialization so later phases can reuse it.
- Handle the possibility that required model assets are not already available.
- Do not silently download large assets without clearly reporting it.
- Support an optional input image path.
- When an image is provided, report the number of detected faces and basic bounding-box metadata.
- When no image is provided, only verify model initialization.
- Never generate or add a fake face image.

F. Tests
- Add tests for configuration parsing and validation.
- Add tests for notification command construction using mocks.
- Add tests for camera cleanup behavior using mocks where practical.
- Hardware tests must be optional/manual and must not make the ordinary unit suite fail.

G. Documentation
- Add or update README.md with Phase 1 setup instructions:
  - Supported Python version chosen for the repo
  - Virtual environment creation
  - Dependency installation
  - Ubuntu libnotify-bin installation
  - Camera test command
  - Notification test command
  - Face-model smoke-test command
  - Clear note about possible model-asset download requirements

Verification:
- Install dependencies if the environment permits.
- Run the relevant unit tests.
- Run Python compile/import checks.
- Run CLI --help commands.
- Run hardware smoke tests only when the environment supports them.
- If hardware or model assets are unavailable, report the exact limitation instead of faking success.

Before finishing:
- Review the diff for secrets, biometric data, generated models, and unnecessary files.
- Confirm that no reference images or embeddings were committed.

Return:
- Files changed
- Architecture decisions
- Exact commands run and outcomes
- Tests passed/failed/skipped
- Manual checks still required
- Any deviation from docs/plan.md and justification

Stop after Phase 1. Do not implement Phase 2.
```

---

# Phase 2 Prompt: Reference Image Preparation and Validation

```text
Implement Phase 2 from docs/plan.md: Reference Image Preparation.

Read docs/plan.md and inspect the repository before making changes. Preserve completed Phase 1 behavior.

Important constraints:
- Do not create, download, synthesize, or commit face images.
- Do not invent the names of the three people.
- The user will manually create one directory per identity under data/reference_images.
- Biometric images must remain ignored by Git.

Required implementation:

A. Directory preparation
- Ensure these directories can exist without committing biometric contents:
  - data/reference_images
  - data/embeddings
  - data/calibration/known
  - data/calibration/unknown
  - data/logs
- Use .gitkeep only where it does not undermine privacy or .gitignore behavior.
- Verify git check-ignore behavior for sample paths.

B. Reference-image scanner
- Implement a reusable module for scanning identity directories.
- An identity is represented by a direct child directory of data/reference_images.
- Ignore hidden files and unsupported extensions.
- Support common safe image extensions such as jpg, jpeg, png, and webp.
- Sort identities and paths deterministically.
- Reject identity directories with unsafe or empty names.
- Do not infer identity from EXIF or file content.

C. Validation script
- Implement scripts/validate_reference_images.py.
- It must:
  - Load configuration
  - Scan identity directories
  - Decode each image safely
  - Detect unreadable or unsupported files
  - Use the existing face engine from Phase 1 to detect faces
  - Reject images with zero faces
  - Reject ambiguous images with multiple substantial faces
  - Check configured minimum face dimensions
  - Record detection confidence
  - Print a per-identity summary
  - Exit nonzero when any identity has no valid images
  - Support --json-report with an output path
  - Never modify or delete source images
- Make model-dependent validation explicit. If model assets are unavailable, return a clear error.

D. Documentation
- Add docs/reference-image-guide.md explaining:
  - Folder layout
  - Recommended image quality
  - Pose and lighting variation
  - Why two or three images can start the prototype
  - Why five to ten camera-specific images are better
  - Consent and privacy requirements
  - How to run validation
  - That images must not be committed
- Use generic examples such as person_1, person_2, person_3. Do not invent real identities.

E. Tests
- Unit-test directory scanning using temporary directories.
- Test supported and unsupported extensions.
- Test empty identities.
- Test deterministic ordering.
- Mock face detection for validator decision tests.
- Do not require real biometric images in automated tests.

Verification:
- Run tests.
- Run compile/import checks.
- Run the validator --help command.
- If no real reference images are available, do not report an actual successful enrollment-ready validation. Report that the script is ready for manual use.

Return:
- Files changed
- Validation rules implemented
- Commands and outcomes
- Manual action required from the user
- Privacy protections confirmed

Stop after Phase 2. Do not implement enrollment.
```

---

# Phase 3 Prompt: Enrollment Pipeline

```text
Implement Phase 3 from docs/plan.md: Enrollment Pipeline.

Read docs/plan.md and inspect all existing Phase 1-2 code. Do not rewrite working modules without a concrete reason.

Objective:
Convert valid reference images into a safe, deterministic local embedding database.

Required implementation:

A. Core data models
- Add typed models for:
  - Face detection result
  - Enrollment record
  - Enrollment rejection
  - Enrollment summary
- Reuse face-engine output rather than coupling enrollment directly to third-party face objects.

B. Face engine
- Complete or refine src/face_engine.py so it:
  - Loads the configured InsightFace pipeline once
  - Uses CPUExecutionProvider explicitly by default
  - Converts third-party outputs into project-owned typed structures
  - Returns bounding boxes, detection confidence, optional landmarks if available, and normalized embeddings
  - Validates embedding shape and finite values
  - Does not leak model-specific objects beyond the adapter
  - Produces clear errors for missing model assets or unavailable providers
- Verify the API against the actually installed InsightFace version.

C. Enrollment service
- Implement src/enrollment.py.
- It must:
  - Scan identity folders through the Phase 2 scanner
  - Decode images
  - Detect faces
  - Reject images with no valid face
  - Reject ambiguous images with multiple substantial faces
  - Enforce minimum face dimensions and detection confidence
  - Normalize each embedding using L2 normalization
  - Keep every valid reference embedding separately
  - Produce deterministic ordering
  - Never alter source images
  - Require at least one valid embedding per identity
  - Return a detailed summary

D. Embedding file format
- Save to data/embeddings/known_faces.npz by default.
- Use numpy savez_compressed or an equally transparent local format.
- Store, at minimum:
  - schema_version
  - names
  - embeddings
  - source_paths
  - detection_scores
  - bounding_boxes
  - created_at
  - model identifier or model configuration fingerprint
- Avoid Python pickle.
- Ensure the file can be loaded with allow_pickle=False.
- Save atomically using a temporary file followed by replace.
- Set restrictive file permissions on POSIX when possible.
- Never log full embedding vectors.

E. Embedding loader
- Implement a strict loader that verifies:
  - Required fields
  - Schema version
  - Consistent row counts
  - Two-dimensional embedding array
  - Finite numeric values
  - Expected normalization tolerance
  - Nonempty identity names
  - At least one identity
- Return project-owned typed data.

F. CLI
- Implement scripts/enroll_faces.py with:
  - Config path option
  - Reference root option
  - Output option
  - --dry-run
  - --json-report
  - --force to replace an existing database intentionally
  - Useful exit codes
- Without --force, do not overwrite an existing embedding database.
- Print a concise enrollment summary without exposing embeddings.

G. Tests
- Test normalization.
- Test deterministic records.
- Test atomic save and strict load using temporary data.
- Test corrupted or mismatched NPZ fields.
- Test overwrite protection.
- Mock face-engine outputs; real images and model assets must not be required by unit tests.
- Include a test proving allow_pickle=False loading works.

H. Documentation
- Update README with enrollment commands and expected layout.
- Document that changing reference images requires reenrollment.
- Document how to delete the generated database.

Verification:
- Run tests and compile checks.
- Run CLI --help.
- If real reference images and model assets are available, perform enrollment and report the actual result.
- Otherwise, do not fabricate an embedding file or enrollment count.

Return:
- Files changed
- NPZ schema
- Commands and outcomes
- Actual versus mocked verification
- Manual steps remaining

Stop after Phase 3. Do not implement matching.
```

---

# Phase 4 Prompt: Face Matcher and Unknown Rejection

```text
Implement Phase 4 from docs/plan.md: Face Matcher.

Read docs/plan.md and inspect the embedding schema and configuration already implemented.

Objective:
Match one normalized live-face embedding against enrolled references while safely rejecting unknown people.

Required implementation:

A. Recognition data model
- Implement or finalize RecognitionResult with:
  - label
  - accepted
  - best_score
  - second_best_score
  - margin
  - matched_reference_path when appropriate
  - rejection_reason
- Do not expose raw embeddings in results or logs.

B. Matcher
- Implement src/matcher.py with a FaceMatcher class.
- Load the embedding database through the strict Phase 3 loader.
- Normalize live embeddings defensively.
- Compute cosine similarity using vectorized NumPy.
- Group scores by identity.
- Support configured identity scoring modes:
  1. maximum reference similarity
  2. mean of top K references
- Default to maximum reference similarity for the initial project.
- Calculate the second-best score from a different identity.
- Apply both:
  - minimum similarity threshold
  - minimum identity margin
- Return Unknown when either condition fails.
- Handle a database containing only one identity without inventing a second identity score.
- Reject malformed, nonfinite, zero-norm, or wrong-dimensional live embeddings with clear errors.
- Ensure stable deterministic tie behavior.

C. Configuration
- Validate:
  - threshold range
  - nonnegative margin
  - top_k_average >= 1
  - supported scoring mode
  - unknown label cannot collide with an enrolled identity

D. Optional batch interface
- Add a small batch-matching method only if it remains simple and is used by calibration or evaluation.
- Do not overengineer approximate-nearest-neighbor search; there are only a few references.

E. Tests
Use synthetic normalized vectors and test:
- Correct identity acceptance
- Unknown below threshold
- Rejection when margin is too small
- Second-best identity excludes references from the winning identity
- Multiple references per identity
- Top-K averaging
- Single-identity database
- Zero vector
- NaN or infinity
- Dimension mismatch
- Deterministic ties
- Unknown-label collision
- Input embedding is not mutated

F. CLI utility
- Implement or update scripts/evaluate_images.py only for a minimal static-image recognition smoke test if it fits the existing plan.
- It must use the face engine and matcher, accept explicit image paths, and print decisions.
- It must not claim ground-truth accuracy.

Verification:
- Run matcher unit tests.
- Run full tests.
- Run compile/import checks.
- If a real embedding database exists, run a safe static smoke test and report the actual score.
- Otherwise, state that only synthetic tests were run.

Return:
- Files changed
- Matching algorithm
- Rejection rules
- Commands and exact outcomes
- Known limitations

Stop after Phase 4. Do not implement the real-time loop.
```

---

# Phase 5 Prompt: Real-Time Video Pipeline

```text
Implement Phase 5 from docs/plan.md: Real-Time Video Pipeline.

Read docs/plan.md and preserve all completed enrollment and matching behavior.

Objective:
Capture webcam frames, detect faces, generate embeddings, classify them as one of the enrolled identities or Unknown, and display a stable preview. Do not add desktop alerts yet.

Required implementation:

A. Camera abstraction
- Implement src/camera.py.
- It must:
  - Accept integer webcam indexes and supported stream paths/URLs without unsafe evaluation
  - Open and validate the source
  - Apply requested width, height, and target FPS where supported
  - Report actual capture properties
  - Return clear read failures
  - Release resources idempotently
  - Support context-manager usage
  - Avoid infinite tight retry loops

B. Real-time application
- Implement src/main.py as the main entry point.
- Add a CLI with:
  - --config
  - --camera-source
  - --no-preview
  - --max-frames for deterministic smoke testing
  - --debug
  - --save-frame only when explicitly requested
- Load configuration, face engine, embedding database, and matcher once.
- Process every configured Nth frame.
- Do not recreate the model or reload embeddings per frame.
- Resize or configure input according to the plan while preserving correct bounding-box coordinates.
- Detect and match every valid face.
- Filter faces below configured minimum dimensions or confidence.
- Draw bounding boxes and labels for preview mode.
- Display:
  - accepted identity and score
  - Unknown and best score
  - optional debug details when --debug is enabled
- Mirror only the preview when configured; keep inference coordinate logic correct.
- Provide q to quit and handle Ctrl+C.
- Always release camera and destroy OpenCV windows.

C. Headless behavior
- --no-preview must run without calling OpenCV GUI functions.
- It must still process frames and print concise recognition events.
- max-frames must allow automated or bounded tests.

D. Error handling
- Handle:
  - unavailable camera
  - missing embedding database
  - model initialization failure
  - frame read failure
  - malformed configuration
- Use nonzero exit codes.
- Avoid broad exception swallowing.

E. Performance
- Track and optionally display:
  - processed-frame count
  - detection/recognition latency
  - approximate processed FPS
- Do not fabricate performance.
- Keep metrics lightweight.

F. Tests
- Mock camera capture, face engine, matcher, and GUI calls.
- Test:
  - processing every Nth frame
  - no-preview does not call imshow/waitKey
  - cleanup on normal exit
  - cleanup on exception
  - max-frames
  - multiple faces
  - known and unknown overlays or event formatting
- Do not require a real camera in unit tests.

G. Documentation
- Update README with run commands, keyboard controls, no-preview mode, and troubleshooting.

Verification:
- Run tests and compile checks.
- Run CLI --help.
- When a camera and model are available, run a bounded live smoke test using max-frames.
- If no hardware is available, explicitly state that real-time hardware verification remains manual.

Return:
- Files changed
- Runtime flow
- Commands and outcomes
- Measured performance only if actually measured
- Manual validation remaining

Stop after Phase 5. Do not implement temporal confirmation or notifications.
```

---

# Phase 6 Prompt: Temporal Confirmation and Lightweight Tracking

```text
Implement Phase 6 from docs/plan.md: Temporal Confirmation.

Read docs/plan.md and inspect the current real-time loop.

Objective:
Prevent single-frame identity decisions from being treated as confirmed detections. Associate nearby detections across frames and require repeated accepted matches.

Required implementation:

A. Tracking data models
- Define project-owned types for:
  - tracked detection
  - track state
  - temporal decision
- Store only necessary recent metadata, not full video frames.

B. Lightweight association
- Implement a simple CPU-friendly track association mechanism suitable for a fixed camera and a small number of faces.
- Use bounding-box IoU and/or normalized center distance.
- Make thresholds configurable.
- Assign stable integer track IDs.
- Expire tracks after the configured gap.
- Do not merge two simultaneous nearby faces into one track.
- Do not carry an identity history into a newly appearing face after track expiry.
- Keep the implementation replaceable by a more advanced tracker later.

C. Temporal filter
- Implement src/temporal_filter.py.
- Maintain a fixed recent history per track.
- Confirm a person only when:
  - the same accepted identity occurs at least required_matches times
  - within history_size recent processed observations
  - observations are within maximum_gap_seconds
- Unknown or rejected predictions must not count as positive matches.
- Conflicting known identities must not be silently combined.
- Return:
  - provisional label
  - confirmed label or None
  - match count
  - history size
  - track ID
  - state transition, such as newly_confirmed, still_confirmed, lost, or unconfirmed
- Define behavior when the confirmed identity changes. Prefer requiring fresh confirmation rather than immediate switching.

D. Real-time integration
- Integrate tracking and temporal decisions into src/main.py.
- Preview should distinguish:
  - provisional recognition
  - confirmed recognition
  - Unknown
- Do not send desktop notifications yet.
- Print a concise event only on meaningful state changes, not on every frame.

E. Configuration
Add validated tracking/temporal fields if missing:
- history_size
- required_matches
- maximum_gap_seconds
- minimum IoU or maximum center-distance threshold
- track expiration
Ensure required_matches <= history_size.

F. Tests
Test deterministically:
- 4 of 6 confirmation
- insufficient matches
- unknown interruptions
- alternating identities
- confirmed identity remains stable
- identity switch requires reconfirmation
- track expiration
- reentry receives a new track
- two simultaneous faces
- crossing or nearby boxes as far as practical
- out-of-order or nonmonotonic timestamps rejected or handled explicitly

G. Documentation
- Explain temporal confirmation settings and their trade-offs in README.

Verification:
- Run unit and full tests.
- Run compile checks.
- Run a bounded mocked integration test.
- Run a live manual smoke test only when hardware is available.

Return:
- Files changed
- Association algorithm
- Confirmation state machine
- Commands and outcomes
- Remaining edge cases

Stop after Phase 6. Do not implement alerts.
```

---

# Phase 7 Prompt: Desktop Notification and Cooldown

```text
Implement Phase 7 from docs/plan.md: Desktop Notification System.

Read docs/plan.md and inspect the temporal confirmation state transitions.

Objective:
Send a desktop popup only when an enrolled identity becomes newly confirmed, while preventing duplicate notification spam.

Required implementation:

A. Alert manager
- Implement src/alert_manager.py.
- Support:
  - per-person cooldown
  - enabled/disabled configuration
  - optional dry-run mode
  - notification title template
  - notification body containing identity, local timestamp, and similarity
  - optional icon path only when configured and valid
- Use a monotonic clock for cooldown calculation.
- Use wall-clock time only for display and logging.
- Inject clocks or make them mockable for deterministic tests.
- Store cooldown state in memory for the first version.
- Different people must have independent cooldowns.
- A rejected or Unknown identity must never trigger an alert.

B. Notification backend
- Create a small backend interface.
- Implement Ubuntu notify-send backend:
  - verify executable availability
  - subprocess argument list
  - shell=False
  - bounded timeout
  - capture useful failure details
- Notification failure should be logged or reported but must not crash the camera loop by default.
- Do not claim cross-platform support unless implemented.

C. Integration
- Trigger only on temporal state `newly_confirmed`.
- Check cooldown before sending.
- Record whether the alert was sent, suppressed by cooldown, disabled, dry-run, or failed.
- Do not notify on every still-confirmed frame.
- Allow a different newly confirmed identity to alert immediately.
- Add CLI option such as --dry-run-alerts if consistent with the existing CLI.

D. Optional sound
- Do not add sound unless it can be implemented cleanly and disabled by default.
- Notifications are the required feature.

E. Tests
Mock subprocess and clocks. Test:
- first alert allowed
- repeated alert blocked within cooldown
- alert allowed after cooldown
- different identity allowed
- Unknown never alerts
- disabled mode
- dry-run mode
- missing notify-send
- command timeout
- nonzero command exit
- real-time integration triggers only on newly_confirmed

F. Documentation
- Add notification setup and troubleshooting to README.
- Explain desktop-session limitations, such as a systemd service without access to the graphical user session.
- Do not claim notification delivery in unsupported environments.

Verification:
- Run tests and compile checks.
- Run the notification test utility if notify-send and a desktop session are available.
- Otherwise, report mocked verification only.

Return:
- Files changed
- Alert state flow
- Commands and outcomes
- Actual versus mocked notification verification
- Manual steps remaining

Stop after Phase 7. Do not implement event logging.
```

---

# Phase 8 Prompt: Privacy-Preserving Event Logging

```text
Implement Phase 8 from docs/plan.md: Logging.

Read docs/plan.md and inspect recognition, temporal, and alert result objects.

Objective:
Create structured event logs for evaluation and debugging without storing raw biometric vectors or continuous frames.

Required implementation:

A. Event model
- Define a typed event record containing the fields required by the plan:
  - timestamp
  - person_name
  - accepted
  - best_score
  - second_best_score
  - margin
  - detection_confidence
  - face_width
  - face_height
  - track_id
  - temporal_state
  - alert_status
  - camera_source in a privacy-safe form
- Do not log raw embeddings.
- Do not log authentication secrets from camera URLs.
- Redact credentials or query tokens from stream sources.

B. CSV logger
- Implement src/event_logger.py.
- Requirements:
  - Create parent directories safely
  - Write a header exactly once
  - Append records
  - Use UTF-8
  - Use Python's csv module correctly
  - Flush events promptly enough to survive ordinary shutdown
  - Handle malformed existing headers explicitly
  - Avoid crashing the main loop on a recoverable log write failure
  - Support enabled/disabled configuration
  - Support log_unknown_people configuration
- Make file permissions restrictive where practical.
- Do not add global hidden side effects at import time.

C. Snapshot policy
- Keep snapshot saving disabled by default.
- If the plan's optional snapshot support is already present, implement it only for confirmed known alerts and only when explicitly enabled.
- Never save unknown faces by default.
- Use safe filenames and avoid identity path traversal.
- Do not implement continuous recording.

D. Integration
- Log meaningful processed detections or state changes according to a documented policy.
- Avoid writing duplicate identical rows every frame when not useful.
- Ensure alert outcome is represented.
- Flush and close cleanly during application shutdown.

E. Tests
Use temporary directories. Test:
- header creation
- append behavior
- exact field order
- unknown logging disabled
- source redaction
- malformed existing header
- Unicode identity names
- disabled logger
- failure handling
- no embedding field
- restrictive permission attempt where testable

F. Documentation
- Document log location, schema, retention, and deletion.
- State clearly that logs may still contain identity names and timestamps.

Verification:
- Run tests and compile checks.
- Execute a small synthetic logging smoke test.
- Inspect the generated CSV manually.
- Do not add the smoke-test log to Git.

Return:
- Files changed
- Log schema
- Logging policy
- Commands and outcomes
- Privacy safeguards

Stop after Phase 8. Do not implement calibration.
```

---

# Phase 9 Prompt: Threshold and Margin Calibration

```text
Implement Phase 9 from docs/plan.md: Threshold Calibration.

Read docs/plan.md and inspect the matcher, enrollment database, and calibration directory structure.

Objective:
Build an offline, reproducible calibration tool that recommends a recognition threshold and identity margin from real labeled samples. Never fabricate calibration data or performance.

Required implementation:

A. Calibration dataset conventions
Support this layout or a clearly documented equivalent:

data/calibration/
├── known/
│   ├── person_1/
│   ├── person_2/
│   └── person_3/
└── unknown/
    ├── unknown_001/
    ├── unknown_002/
    └── ...

- Known folder names are ground-truth identities.
- Unknown subfolder names are sample-group identifiers, not enrolled identities.
- Do not require unknown people's real names.
- Do not commit images.

B. Calibration record generation
- Implement a service and scripts/calibrate_threshold.py.
- For each valid calibration image:
  - detect exactly one usable face or report rejection
  - extract normalized embedding
  - compute per-identity scores without applying final acceptance
  - record ground truth
  - record predicted best identity
  - record best score
  - record second-best different-identity score
  - record margin
  - record image path relative to calibration root
  - record rejection reason when unusable
- Ensure calibration images are not also reference enrollment images unless explicitly allowed and clearly warned. Prefer a leakage check based on paths and optional file hashes.

C. Threshold sweep
- Sweep configurable threshold values and margin values.
- Compute, at minimum:
  - known true accept rate
  - known false reject rate
  - wrong-known-identity rate
  - unknown false accept rate
  - unknown rejection rate
  - accepted sample count
- Clearly define metric denominators.
- Handle zero known or zero unknown samples without division errors.

D. Recommendation policy
- Prioritize:
  1. minimum unknown false acceptance
  2. minimum wrong-known identity acceptance
  3. highest known true acceptance among safe candidates
- Allow a configurable maximum false-accept target.
- If no candidate satisfies the target, report that fact and recommend no threshold instead of inventing one.
- Do not automatically rewrite config.yaml unless an explicit --apply flag is provided.
- With --apply:
  - back up or atomically update configuration
  - change only calibrated fields
  - print the exact old and new values

E. Outputs
- Produce:
  - detailed CSV of sample scores
  - JSON calibration summary
  - human-readable Markdown report
- Include dataset counts, rejected samples, sweep configuration, selected values, and limitations.
- Do not include raw embeddings.

F. Tests
Use synthetic scores or mocked embeddings to test:
- metric definitions
- threshold sweep
- margin sweep
- no unknown samples
- no known samples
- no safe candidate
- deterministic recommendation
- config apply modifies only intended fields
- data leakage warning
- unreadable/multiface rejection handling

G. Documentation
- Add calibration collection and execution instructions.
- Explain why default thresholds are only starting points.
- Explain the need to use the final camera and room.

Verification:
- Run tests and compile checks.
- Run --help.
- If no real calibration images exist, run only synthetic tests and explicitly state that no real threshold was recommended.
- Never insert fabricated metrics into config or reports.

Return:
- Files changed
- Metric definitions
- Recommendation policy
- Commands and outcomes
- Whether real calibration was possible
- Manual data collection required

Stop after Phase 9. Do not implement the full evaluation phase.
```

---

# Phase 10 Prompt: Evaluation and Benchmarking

```text
Implement Phase 10 from docs/plan.md: Evaluation.

Read docs/plan.md and inspect calibration outputs, runtime logs, and existing scripts.

Objective:
Provide reproducible offline evaluation, runtime benchmarking, and a manual scenario checklist without fabricating results.

Required implementation:

A. Offline evaluation
- Implement or refine scripts/evaluate_images.py.
- Accept:
  - config path
  - embedding database path
  - labeled evaluation root
  - output directory
- Use a dataset layout clearly documented for known and unknown people.
- Keep evaluation data separate from enrollment and calibration data.
- Detect accidental path or hash overlap and warn about leakage.
- Produce per-sample decisions and aggregate metrics:
  - known recognition accuracy
  - known true accept rate
  - known false reject rate
  - wrong-known identity rate
  - unknown rejection rate
  - unknown false accept rate
  - confusion matrix over enrolled identities plus Unknown where well-defined
- Include rejected/unusable image counts separately.

B. Runtime benchmark
- Implement scripts/benchmark_runtime.py.
- Support a camera source or an explicit local video path.
- Support bounded execution using max frames or duration.
- Measure actual:
  - captured frames
  - processed frames
  - face detections
  - processing latency distribution
  - processed FPS
  - dropped/read-failure count
- CPU and memory measurement may be added only if a suitable dependency already exists or is justified.
- Do not fabricate CPU utilization.
- Do not require preview.
- Keep results machine-readable.

C. Event-log analysis
- Add a script or module to summarize data/logs/events.csv:
  - alerts by person
  - alerts suppressed by cooldown
  - unknown decisions if logged
  - time range
  - score distributions
- Do not infer ground-truth accuracy from runtime logs unless labels exist.

D. Reports
- Produce JSON and Markdown reports.
- Include:
  - configuration fingerprint
  - model identifier
  - embedding database fingerprint
  - timestamp
  - dataset counts
  - metric definitions
  - limitations
- Do not commit generated reports containing sensitive paths or identities unless explicitly intended.

E. Manual test checklist
- Add docs/manual-evaluation-checklist.md covering all scenarios in Phase 10:
  - known frontal
  - known side view
  - unknown person
  - known plus unknown
  - multiple enrolled people
  - low light
  - printed photo or screen replay
  - leave and return
- Provide fields for actual observation, expected behavior, pass/fail, and notes.
- Do not prefill results.

F. Tests
Test:
- metric calculations
- confusion matrix label order
- empty datasets
- rejected samples
- runtime aggregate calculations
- log summary
- report generation
- leakage detection

Verification:
- Run tests and compile checks.
- Run all CLI --help commands.
- Run synthetic evaluation fixtures.
- Run actual hardware/video benchmarks only when a source is available.
- Clearly separate real results from synthetic test results.

Return:
- Files changed
- Metrics and denominator definitions
- Commands and outcomes
- Real results, if any
- Manual scenarios still required

Stop after Phase 10. Do not implement privacy deletion or liveness yet.
```

---

# Phase 11 Prompt: Privacy, Data Removal, and Security Hardening

```text
Implement Phase 11 from docs/plan.md: Privacy and Security.

Read docs/plan.md and audit the repository for biometric data handling.

Objective:
Make privacy protections explicit and provide safe identity removal and data cleanup workflows.

Required implementation:

A. Privacy audit
Inspect:
- .gitignore
- reference image paths
- embedding paths
- calibration and evaluation paths
- logs
- snapshots
- temporary files
- reports
- exception messages
- camera URLs
- model cache behavior

Identify and fix accidental exposure risks without deleting user data.

B. Git protections
- Ensure biometric images, embeddings, logs, snapshots, calibration data, evaluation data, and generated sensitive reports are ignored.
- Add a safe command or documentation for checking tracked sensitive files.
- Do not remove tracked files automatically. Report them and provide explicit user-controlled remediation instructions.
- Never run destructive Git history rewrite.

C. File permissions
- Centralize best-effort restrictive permissions for:
  - embedding database
  - logs
  - snapshots
  - generated reports
- Handle non-POSIX systems gracefully.
- Do not claim encryption when only permissions are used.

D. Identity removal
- Implement scripts/remove_identity.py.
- Requirements:
  - accept exact identity name
  - load and validate the embedding database
  - show how many records would be removed
  - require --confirm or an explicit noninteractive confirmation flag
  - support --dry-run
  - write atomically
  - preserve all other records and schema metadata
  - refuse to leave an invalid empty database unless an explicit delete-all workflow is chosen
  - optionally identify related reference and snapshot paths, but never delete source images by default
- Add a separate safe cleanup command only if necessary.
- No wildcard deletion based on untrusted identity names.

E. Camera-source redaction
- Ensure logs and errors redact credentials, tokens, or password-like URL components.
- Add tests.

F. Privacy documentation
Create docs/privacy-and-data-management.md covering:
- consent
- purpose limitation
- local processing
- data inventory
- storage paths
- retention
- deletion
- backup implications
- logs
- snapshots
- unknown-person policy
- limitations
- incident response for accidental Git commits
- no high-stakes use claim

G. Tests
Test:
- identity removal preserves other embeddings
- dry-run
- nonexistent identity
- exact-name matching
- atomic update
- invalid database
- permission helper
- URL redaction
- no path traversal
- no automatic image deletion

Verification:
- Run tests and compile checks.
- Run git status.
- Run git ls-files checks for sensitive directories.
- Do not display biometric file contents or embeddings in the report.

Return:
- Files changed
- Risks found and fixed
- Sensitive tracked files found, if any
- Commands and outcomes
- Remaining privacy responsibilities

Stop after Phase 11. Do not implement liveness.
```

---

# Phase 12 Prompt: Experimental Anti-Spoofing Upgrade

```text
Implement Phase 12 from docs/plan.md: Anti-Spoofing Upgrade.

This phase is experimental. Read docs/plan.md and preserve the working recognition pipeline.

Objective:
Add an optional, CPU-friendly challenge-based liveness gate that reduces simple printed-photo and static phone-screen attacks. Do not claim that it provides secure or certified anti-spoofing.

Design constraints:
- Disabled by default.
- Modular and removable.
- Recognition continues to work normally when disabled.
- No cloud services.
- No GPU requirement.
- No training of a new model.
- Do not invent support from third-party APIs; verify the installed landmark library API.
- Prefer a maintained CPU-capable face-landmark solution already installed or add one justified dependency.
- If MediaPipe is selected, verify its current Python API and supported Python version before implementation.

Required implementation:

A. Liveness interface
- Add a project-owned liveness interface returning:
  - status: disabled, pending, passed, failed, unavailable
  - challenge type
  - progress
  - reason
  - timestamp
- Do not expose third-party landmark objects outside the adapter.

B. Active challenge state machine
Implement at least one robustly testable challenge workflow, preferably:
- blink followed by head turn, or
- randomized blink / look-left / look-right sequence

Requirements:
- Generate a short challenge from configured supported actions.
- Associate challenge state with a track ID.
- Use a timeout.
- Require ordered completion.
- Reset on track expiration.
- Prevent one person's action from completing another person's track.
- Use configurable thresholds.
- Use temporal smoothing to reduce jitter.
- Do not use identity recognition itself as proof of liveness.

C. Landmark measurements
- Implement measurements through an adapter:
  - blink measurement using eye aspect or an equivalent verified signal
  - left/right head-turn measurement using landmarks or pose estimation
- Isolate numeric measurements from the challenge state machine.
- Validate finite values and missing landmarks.
- Document that thresholds require camera-specific calibration.

D. Recognition integration
- Add config:
  - liveness enabled
  - required for alerts
  - challenge timeout
  - supported actions
  - measurement thresholds
- When liveness is required for alerts:
  - identity must already be temporally confirmed
  - liveness must pass for the same track
  - only then may a newly eligible alert be sent
- Decide and document whether cooldown starts on identity confirmation or successful alert. Prefer successful alert.
- Preview should display challenge instructions and progress.
- In no-preview mode, print challenge instructions only when meaningful.
- Unknown people must not receive named alerts.

E. Safety and limitations
- Clearly label the feature experimental.
- Do not claim resistance to replay, deepfake, 3D mask, or sophisticated screen attacks.
- Do not describe it as authentication-grade.
- If the landmark dependency is unavailable, fail gracefully or keep liveness disabled according to configuration.

F. Tests
Use synthetic measurements and timestamps. Test:
- successful blink challenge
- successful head-turn challenge
- ordered sequence
- timeout
- wrong action
- noisy values
- missing landmarks
- track expiration
- separate simultaneous tracks
- liveness disabled
- liveness required blocks alert
- liveness pass enables alert
- cooldown starts at the documented point
- dependency unavailable behavior

G. Documentation
Add docs/liveness.md with:
- threat model
- supported challenges
- configuration
- calibration
- user flow
- limitations
- manual spoof-testing checklist
- explicit non-security guarantee

Verification:
- Run tests and compile checks.
- Run CLI help.
- Run a mocked end-to-end liveness test.
- Run a real camera challenge only when a compatible camera, GUI session, and landmark dependency are available.
- Never claim spoof resistance based only on unit tests.

Return:
- Files changed
- Liveness state machine
- Dependency and API verification performed
- Commands and outcomes
- Real versus synthetic verification
- Security limitations

Stop after Phase 12.
```

---

# Final Integration Prompt: Complete and Harden the Project

```text
Perform final integration and hardening for the real-time three-person desktop alert detector.

Read docs/plan.md completely and inspect every implemented phase. Do not add unrelated features.

Goals:
- Ensure all phases work together.
- Remove dead code and contradictions.
- Complete documentation.
- Make the project runnable from a clean checkout after the user supplies private images and model assets.
- Never fabricate camera, recognition, calibration, evaluation, or spoof-testing results.

Required work:

1. Repository audit
- Inspect git status and all source, scripts, tests, docs, config, and dependency files.
- Identify duplicate modules, stale APIs, circular imports, inconsistent data models, and mismatched configuration fields.
- Preserve intentional user modifications.

2. End-to-end flow
Verify the intended sequence:
- configuration load
- reference validation
- enrollment
- embedding load
- matching
- real-time capture
- tracking
- temporal confirmation
- optional liveness
- cooldown
- desktop notification
- logging
- calibration
- evaluation
- identity removal

3. CLI consistency
- Ensure every script has --help, clear exit codes, and consistent config handling.
- Ensure running modules from repository root works.
- Add a single primary run command.
- Avoid import-path hacks when packaging can solve them cleanly.

4. Dependency and packaging review
- Ensure requirements.txt contains all used direct dependencies and no clearly unused dependencies.
- Separate development dependencies if appropriate.
- Document supported Python versions based on actual dependency compatibility.
- Do not claim compatibility that was not tested.
- Add a pyproject.toml only if it improves packaging/testing and does not conflict with existing choices.

5. Configuration audit
- Ensure config.yaml matches code exactly.
- Validate every field.
- Remove unused fields or implement them.
- Ensure safe defaults:
  - CPU provider
  - unknown rejection
  - temporal confirmation
  - notification cooldown
  - logging privacy
  - snapshots disabled
  - liveness disabled unless explicitly enabled

6. Testing
- Run the complete unit test suite.
- Add missing integration tests using mocks/fakes.
- Run Python compilation/import checks.
- Run lint or type checks only if configured, fixing genuine issues rather than suppressing them broadly.
- Do not make hardware tests mandatory in CI.
- Ensure no test depends on real biometric images, camera hardware, desktop notifications, network access, or downloaded model assets.

7. Documentation
Update README.md so a new user can:
- install the project
- add private reference images
- validate images
- enroll faces
- run static recognition
- calibrate threshold
- run live detection
- understand notifications and cooldown
- evaluate results
- remove an identity
- enable experimental liveness
- troubleshoot camera, model, and desktop-session failures
- understand privacy and security limitations

Add a concise architecture diagram in text or Mermaid if useful.
Do not duplicate the full docs/plan.md unnecessarily.

8. Deployment
- Implement the manual launcher from the plan.
- Add an optional systemd user-service example or desktop autostart example.
- Keep it disabled by default.
- Document graphical-session requirements for notify-send.
- Do not install or enable services automatically.

9. Data safety
- Verify that Git does not track:
  - reference images
  - embeddings
  - calibration/evaluation images
  - logs
  - snapshots
  - generated sensitive reports
  - model assets
- Report any already tracked sensitive paths without deleting them.
- Verify no raw embeddings are printed or logged.

10. Final acceptance report
Produce a truthful matrix with:
- Requirement
- Implemented
- Automated test
- Manual test required
- Notes

Include all Minimum Viable Product checklist items from docs/plan.md.

Verification commands should include, as applicable:
- git status
- dependency/import check
- full unit tests
- compileall
- all CLI --help commands
- static synthetic end-to-end test
- git tracked-sensitive-file check

Hardware-dependent checks:
- Run them only if the environment supports them.
- Otherwise provide exact manual commands and mark them unverified.
- Do not claim the project is production secure or spoof proof.

Return:
- Final files changed
- Commands and exact outcomes
- Test summary
- Requirement matrix
- Manual validation checklist
- Known limitations
- Recommended next commit message

Do not begin a new feature after the final audit.
```

---

# Optional Bug-Fix Prompt After Any Phase

Use this prompt when a phase implementation fails tests or behaves incorrectly.

```text
Debug the current implementation without expanding project scope.

1. Read docs/plan.md and identify the current phase.
2. Inspect git diff and recent changes.
3. Reproduce the reported failure with the smallest reliable command.
4. Trace the failure to its root cause.
5. Do not mask the issue with broad exception handling, arbitrary sleeps, disabled assertions, relaxed thresholds, or skipped tests.
6. Fix the smallest coherent set of files.
7. Add or update a regression test that fails before the fix and passes after it.
8. Run the targeted test, then the full relevant test suite.
9. Report:
   - root cause
   - files changed
   - exact commands
   - test outcomes
   - any remaining uncertainty
10. Do not proceed to the next phase.
```

---

# Optional Code Review Prompt After Each Phase

```text
Review the current phase implementation as a strict senior Python, computer-vision, privacy, and reliability reviewer.

Read docs/plan.md and inspect the actual diff. Do not modify files yet.

Review for:
- Incorrect or hallucinated third-party APIs
- CPU incompatibility
- Resource leaks
- Camera cleanup failures
- Incorrect embedding normalization
- Wrong cosine-similarity logic
- Incorrect second-best identity calculation
- Weak unknown rejection
- Track identity leakage
- Notification spam
- Logging of biometric vectors or private camera credentials
- Unsafe file writes
- Pickle usage
- Path traversal
- Unhandled empty or corrupted data
- Tests that only assert mocks rather than behavior
- Claimed verification that was not actually run
- Unnecessary complexity
- Deviations from docs/plan.md

Return findings ordered by severity:
- Critical
- High
- Medium
- Low

For each finding include:
- file and line
- impact
- evidence
- precise fix
- required regression test

If no issue is found in a category, say so. Do not praise generally and do not implement fixes until asked.
```

---

# Optional Apply-Review-Fixes Prompt

```text
Apply the confirmed review fixes only.

1. Re-read the review findings and inspect the referenced code.
2. Validate each finding against the current repository before changing anything.
3. Skip findings that are no longer applicable and explain why.
4. Implement minimal coherent fixes.
5. Add regression tests for every behavioral bug.
6. Run targeted tests, then the full relevant suite.
7. Do not add unrelated features or refactor unaffected modules.
8. Report files changed, commands, outcomes, and unresolved findings.
9. Stop after the fixes.
```

---

# Recommended Git Commit Sequence

```text
chore: bootstrap cpu face alert project
feat: validate private reference images
feat: add deterministic face enrollment pipeline
feat: implement embedding matcher and unknown rejection
feat: add real-time camera recognition loop
feat: add lightweight tracking and temporal confirmation
feat: add desktop alerts with per-person cooldown
feat: add privacy-preserving event logging
feat: add threshold and margin calibration
feat: add offline evaluation and runtime benchmarks
feat: harden biometric data privacy and identity removal
feat: add optional experimental liveness challenge
chore: complete integration and release audit
```

Do not commit generated biometric data, models, logs, calibration images, evaluation images, snapshots, or private reports.
