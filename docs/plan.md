# Real-Time Three-Person Desktop Alert Detector

## 1. Project Overview

### 1.1 Goal

Build a local desktop application that:

1. Captures video from a webcam or IP camera.
2. Detects faces in real time.
3. Recognizes only three enrolled people.
4. Labels every other person as `Unknown`.
5. Shows a desktop popup when one of the three enrolled people is detected.
6. Avoids repeated notifications for the same person.
7. Runs on Ubuntu without an NVIDIA GPU.

### 1.2 Main Constraint

Only two or three reference images are currently available for each person.

This is enough for a prototype because the system will not train a new face-classification model. It will use a pretrained face-recognition model to convert each face into a numerical embedding and compare live faces with saved reference embeddings.

### 1.3 Expected Use Case

This system is suitable for:

- A personal desktop alert tool
- A controlled office room
- A home entrance camera
- A fixed indoor webcam
- Low-security identity notification

It should not initially be treated as:

- A secure access-control system
- A police or public-surveillance system
- A biometric attendance system without consent
- A system that guarantees resistance to photo or video spoofing

---

## 2. Success Criteria

The first usable version should satisfy the following requirements:

- Detect at least one visible face from the webcam.
- Recognize the three enrolled people.
- Reject people who are not enrolled.
- Require repeated confirmation across multiple frames.
- Show a popup containing the recognized person's name.
- Apply a cooldown so the same person does not trigger repeated alerts.
- Save optional event logs with timestamps and similarity scores.
- Run acceptably on CPU.
- Start with a simple command such as:

```bash
python src/main.py
```

---

## 3. Recommended Technology Stack

### 3.1 Language

- Python 3.11 or Python 3.12

### 3.2 Core Libraries

- OpenCV
  - Webcam capture
  - Frame resizing
  - Drawing bounding boxes
  - Preview window

- InsightFace
  - Face detection
  - Face alignment
  - Face embedding extraction

- ONNX Runtime CPU
  - CPU model inference

- NumPy
  - Embedding storage
  - Vector normalization
  - Cosine similarity

- PyYAML
  - Configuration file loading

- `notify-send`
  - Ubuntu desktop popup notifications

### 3.3 Optional Libraries

- Rich
  - Better terminal logging

- Pandas
  - Event-log analysis

- SQLite
  - Structured event storage

- Pillow
  - Image validation and conversion

- pytest
  - Unit testing

---

## 4. High-Level Architecture

```text
Reference Images
      |
      v
Enrollment Script
      |
      v
Face Detection + Alignment
      |
      v
Pretrained Face Embeddings
      |
      v
known_faces.npz
      |
      +------------------------------+
                                     |
Webcam / IP Camera                   |
      |                              |
      v                              |
Frame Capture                        |
      |                              |
      v                              |
Face Detection                       |
      |                              |
      v                              |
Face Alignment                       |
      |                              |
      v                              |
Live Face Embedding -----------------+
      |
      v
Similarity Matching
      |
      +--> Known Person
      |        |
      |        v
      |   Temporal Confirmation
      |        |
      |        v
      |   Cooldown Check
      |        |
      |        v
      |   Desktop Notification
      |
      +--> Unknown
```

---

## 5. Recognition Strategy

### 5.1 Do Not Train a Classifier

Do not train a CNN classifier using only six to nine total images. That would overfit almost immediately.

Use a pretrained face-recognition model instead.

### 5.2 Embedding-Based Recognition

Each face is converted into a fixed-length vector:

```text
Face image -> pretrained model -> embedding vector
```

A live embedding is compared against stored reference embeddings using cosine similarity.

### 5.3 Store Every Reference Separately

Do not immediately average the two or three images into one embedding.

Store all reference embeddings separately:

```text
Person A:
- embedding from image 1
- embedding from image 2
- embedding from image 3
```

For a live face, compare it with all references and use:

- Maximum similarity, or
- Mean of the top two similarities

The recommended first implementation uses the maximum similarity with a margin rule.

### 5.4 Unknown Rejection

A face should be accepted only when all recognition conditions are satisfied:

```text
best similarity >= recognition threshold
best similarity - second-best similarity >= identity margin
face quality >= minimum quality
```

Otherwise, label the face as `Unknown`.

### 5.5 Temporal Confirmation

Do not notify based on one frame.

Recommended rule:

```text
Recognized as the same person in at least 4 of the last 6 processed frames
```

This reduces false alerts caused by:

- Blur
- Partial faces
- Bad lighting
- Detection errors
- Brief similarity spikes

---

## 6. Recommended Project Structure

```text
person-alert-detector/
├── README.md
├── plan.md
├── requirements.txt
├── config.yaml
├── .gitignore
│
├── data/
│   ├── reference_images/
│   │   ├── person_1/
│   │   │   ├── image_1.jpg
│   │   │   ├── image_2.jpg
│   │   │   └── image_3.jpg
│   │   ├── person_2/
│   │   │   ├── image_1.jpg
│   │   │   ├── image_2.jpg
│   │   │   └── image_3.jpg
│   │   └── person_3/
│   │       ├── image_1.jpg
│   │       ├── image_2.jpg
│   │       └── image_3.jpg
│   │
│   ├── embeddings/
│   │   └── known_faces.npz
│   │
│   ├── calibration/
│   │   ├── known/
│   │   └── unknown/
│   │
│   └── logs/
│       └── events.csv
│
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── camera.py
│   ├── face_engine.py
│   ├── enrollment.py
│   ├── matcher.py
│   ├── temporal_filter.py
│   ├── alert_manager.py
│   ├── event_logger.py
│   └── utils.py
│
├── scripts/
│   ├── enroll_faces.py
│   ├── calibrate_threshold.py
│   ├── test_camera.py
│   └── evaluate_images.py
│
└── tests/
    ├── test_matcher.py
    ├── test_temporal_filter.py
    └── test_alert_manager.py
```

---

## 7. Configuration Design

Create `config.yaml`:

```yaml
camera:
  source: 0
  width: 640
  height: 480
  target_fps: 15
  process_every_n_frames: 2
  mirror_preview: true

model:
  provider: CPUExecutionProvider
  detection_size: [640, 640]
  minimum_detection_confidence: 0.60
  minimum_face_width: 70
  minimum_face_height: 70

recognition:
  similarity_threshold: 0.45
  identity_margin: 0.05
  top_k_average: 1
  unknown_label: Unknown

temporal_confirmation:
  history_size: 6
  required_matches: 4
  maximum_gap_seconds: 2.0

alerts:
  enabled: true
  cooldown_seconds: 60
  popup_title: Person Alert
  save_snapshot: false
  snapshot_directory: data/logs/snapshots

logging:
  enabled: true
  event_file: data/logs/events.csv
  log_unknown_people: false

privacy:
  store_live_frames: false
  store_unknown_faces: false
```

The initial similarity threshold is only a starting value. It must be calibrated using local images and videos.

---

## 8. Development Phases

# Phase 1: Environment and Camera Verification

## Objective

Confirm that Python, OpenCV, the webcam, InsightFace, and ONNX Runtime work correctly on CPU.

## Tasks

1. Create the project directory.
2. Create a virtual environment.
3. Install dependencies.
4. Test webcam access.
5. Verify that a frame can be displayed.
6. Verify that the face model loads using the CPU provider.
7. Detect a face in a static image.

## Suggested Commands

```bash
mkdir person-alert-detector
cd person-alert-detector

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install opencv-python insightface onnxruntime numpy pyyaml pillow pytest
```

Install Ubuntu notification support if needed:

```bash
sudo apt update
sudo apt install libnotify-bin
```

Test notification:

```bash
notify-send "Person Alert" "Notification system is working."
```

## Deliverables

- Working virtual environment
- `requirements.txt`
- Successful webcam test
- Successful face detection test
- Successful Ubuntu popup test

## Completion Check

Phase 1 is complete when:

- The webcam preview opens.
- At least one face box appears.
- The model runs without CUDA.
- `notify-send` creates a popup.

---

# Phase 2: Reference Image Preparation

## Objective

Prepare clean reference images for all three people.

## Tasks

1. Create one folder per person.
2. Add two or three images for each person.
3. Ensure each image contains only one main face.
4. Avoid extremely small, blurred, or heavily filtered faces.
5. Use meaningful folder names because folder names become identity labels.

Example:

```text
data/reference_images/
├── Alice/
├── Bob/
└── Charlie/
```

## Image Quality Requirements

Each image should ideally have:

- Face width of at least 150 pixels
- Clear eyes
- Limited motion blur
- Limited compression artifacts
- No extreme rotation
- Similar appearance to the live environment
- Different expressions or slight head angles

## Best Improvement

Capture five to ten additional images from the actual target webcam:

- Front-facing
- Slightly left
- Slightly right
- Neutral expression
- Normal expression
- With glasses, if usually worn
- Under expected room lighting

These extra images do not require model training.

## Deliverables

- Valid folder for each enrolled person
- At least two usable images per person
- Preferably five or more images per person after initial testing

---

# Phase 3: Enrollment Pipeline

## Objective

Convert reference images into saved face embeddings.

## `scripts/enroll_faces.py` Responsibilities

1. Scan every person folder.
2. Read each image.
3. Detect faces.
4. Reject images with:
   - No face
   - Multiple major faces
   - Very small faces
5. Extract an aligned face embedding.
6. Normalize the embedding.
7. Save:
   - Person name
   - Image path
   - Embedding
   - Detection confidence
   - Bounding box
8. Produce an enrollment summary.

## Example Enrollment Output

```text
Enrollment Summary
------------------
Alice:   3 valid images, 0 rejected
Bob:     2 valid images, 1 rejected
Charlie: 3 valid images, 0 rejected

Saved 8 embeddings to:
data/embeddings/known_faces.npz
```

## Suggested Embedding File Fields

```text
names
embeddings
source_paths
detection_scores
```

## Validation

After enrollment:

- Embeddings must have consistent dimensions.
- Every embedding must be normalized.
- Every person must have at least one valid embedding.
- The script must fail clearly when a person has no valid references.

## Deliverables

- `data/embeddings/known_faces.npz`
- Enrollment report
- Clear error handling

---

# Phase 4: Face Matcher

## Objective

Match a live face embedding against all stored references.

## Core Algorithm

```python
live_embedding = normalize(live_embedding)

scores = known_embeddings @ live_embedding

best_index = argmax(scores)
best_score = scores[best_index]
best_name = names[best_index]

second_best_score = highest_score_from_different_identity()

if (
    best_score >= similarity_threshold
    and best_score - second_best_score >= identity_margin
):
    return best_name, best_score
else:
    return "Unknown", best_score
```

## Important Detail

The second-best score should ideally come from a different identity, not simply a second image belonging to the same person.

## Matching Modes

Implement these modes:

### Mode A: Maximum Reference Similarity

```text
Identity score = highest score among that person's reference images
```

Recommended for the first version.

### Mode B: Mean Top-K Similarity

```text
Identity score = mean of the top two scores for that person
```

Useful after collecting more reference images.

### Mode C: Identity Centroid

```text
Identity score = similarity with the person's averaged embedding
```

Useful later, but it may lose variation when only two references exist.

## Deliverables

- `src/matcher.py`
- Unit tests using synthetic normalized vectors
- Known/unknown response structure

## Suggested Result Object

```python
{
    "label": "Alice",
    "accepted": True,
    "best_score": 0.67,
    "second_best_score": 0.48,
    "margin": 0.19,
}
```

---

# Phase 5: Real-Time Video Pipeline

## Objective

Recognize faces from the webcam while maintaining acceptable CPU performance.

## Processing Loop

```text
Open camera
    |
Read frame
    |
Resize frame
    |
Process every Nth frame
    |
Detect faces
    |
Filter low-quality detections
    |
Extract embeddings
    |
Match each embedding
    |
Update temporal history
    |
Trigger alert if confirmed
    |
Draw results
    |
Display preview
```

## CPU Optimizations

1. Capture at `640 x 480`.
2. Process every second or third frame.
3. Use a detection size no larger than required.
4. Ignore very small faces.
5. Reuse loaded models.
6. Avoid writing frames to disk unless an event occurs.
7. Limit preview FPS.
8. Consider face tracking later if CPU usage is high.

## Preview Overlay

For known people:

```text
Alice | 0.67 | Confirmed
```

For uncertain matches:

```text
Unknown | 0.39
```

Use different box colors only as a visual convenience. The decision must be based on scores, not colors.

## Keyboard Controls

Recommended:

- `q`: quit
- `p`: pause
- `s`: save current frame for testing
- `d`: toggle debug information

## Deliverables

- `src/camera.py`
- `src/face_engine.py`
- `src/main.py`
- Functional live preview

---

# Phase 6: Temporal Confirmation

## Objective

Prevent notifications caused by a single incorrect frame.

## Recommended Design

Maintain a short history for each tracked face or recent screen position.

Simplified first version:

```text
Recent labels:
[Alice, Alice, Unknown, Alice, Alice, Alice]

Alice appears 5 times in the last 6 processed frames.
Required matches = 4.
Result = Confirmed.
```

## First-Version Logic

For each detected face:

1. Associate it with a recent face using bounding-box overlap or center distance.
2. Add the current predicted label to its history.
3. Count accepted predictions for the same person.
4. Confirm when the required count is reached.
5. Reset history after the face disappears for too long.

## More Robust Later Version

Add a lightweight tracker such as:

- OpenCV tracker
- SORT
- ByteTrack

For only a few faces and a fixed camera, center-distance matching is enough for the first version.

## Deliverables

- `src/temporal_filter.py`
- Tests for:
  - Stable identity
  - Alternating identity
  - Unknown interruptions
  - Face disappearance
  - Multiple faces

---

# Phase 7: Desktop Notification System

## Objective

Show a popup only after a stable identity confirmation.

## Notification Content

Title:

```text
Person Alert
```

Body:

```text
Alice detected at 05:42:13 PM
Similarity: 0.67
```

## Notification Command

```python
subprocess.run(
    [
        "notify-send",
        "Person Alert",
        "Alice detected at 05:42:13 PM",
    ],
    check=False,
)
```

## Cooldown Rule

Recommended:

```text
Per-person cooldown: 60 seconds
```

This means:

- Alice can trigger once.
- Alice cannot trigger again for 60 seconds.
- Bob can still trigger during Alice's cooldown.
- A new alert is allowed after Alice leaves and returns, depending on cooldown policy.

## Cooldown State

```python
last_alert_time = {
    "Alice": timestamp,
    "Bob": timestamp,
    "Charlie": timestamp,
}
```

## Optional Features

- Play a short sound
- Use a custom icon
- Save an event snapshot
- Send Telegram message
- Write events to SQLite
- Run silently without preview

## Deliverables

- `src/alert_manager.py`
- Per-person cooldown
- Notification failure handling

---

# Phase 8: Logging

## Objective

Create enough data to evaluate and debug the system.

## Recommended CSV Fields

```text
timestamp
person_name
accepted
best_score
second_best_score
margin
detection_confidence
face_width
face_height
alert_sent
camera_source
```

Example:

```csv
2026-06-30T17:42:13+06:00,Alice,true,0.67,0.48,0.19,0.96,142,151,true,0
```

## Privacy Defaults

Do not save:

- Continuous video
- Unknown faces
- Full-resolution frames

Only save a snapshot when explicitly enabled.

## Deliverables

- `src/event_logger.py`
- `data/logs/events.csv`
- Configurable logging

---

# Phase 9: Threshold Calibration

## Objective

Find a threshold that recognizes the three enrolled people while rejecting unknown people.

Do not assume the default threshold is correct.

## Calibration Dataset

Collect:

### Known Samples

For each enrolled person:

- 10 to 20 webcam frames
- Frontal view
- Slight left and right views
- Different expressions
- Normal distance
- Slightly far distance
- Expected lighting

### Unknown Samples

Collect:

- 5 to 10 people not enrolled, when consent is available
- Multiple frames per person
- Similar camera conditions

If other people are unavailable, use additional non-enrolled face images for preliminary calibration, but final testing should use the actual camera.

## Calibration Procedure

For every test face:

1. Extract embedding.
2. Compare with references.
3. Record:
   - Ground-truth identity
   - Best identity
   - Best score
   - Second-best identity
   - Second-best score
   - Margin
4. Sweep candidate thresholds.
5. Compute:
   - True accept rate
   - False reject rate
   - False accept rate
   - Unknown rejection rate

## Threshold Selection Rule

Choose a threshold that prioritizes low false alerts.

For a desktop alert system, a missed detection is usually less harmful than repeatedly alerting for the wrong person.

Recommended priority:

```text
1. Minimize false acceptance of unknown people
2. Minimize confusion between the three known people
3. Improve recall after the first two conditions are satisfied
```

## Margin Calibration

Also test margin values:

```text
0.02
0.03
0.05
0.07
0.10
```

Use the smallest margin that reliably separates similar enrolled identities.

## Deliverables

- `scripts/calibrate_threshold.py`
- Calibration CSV
- Recommended threshold
- Recommended identity margin
- Summary report

---

# Phase 10: Evaluation

## Objective

Measure whether the system is reliable enough for the intended room and camera.

## Test Scenarios

### Scenario 1: Known Person, Front View

Expected:

- Correct name
- Stable score
- Alert after temporal confirmation

### Scenario 2: Known Person, Side View

Expected:

- Correct recognition or safe unknown rejection
- No wrong-person alert

### Scenario 3: Unknown Person

Expected:

- Label `Unknown`
- No popup

### Scenario 4: Two People Simultaneously

Expected:

- Separate bounding boxes
- Correct alert for known person
- Unknown person remains unknown

### Scenario 5: Enrolled People Together

Expected:

- Correct names for both
- Separate cooldown handling

### Scenario 6: Low Light

Expected:

- Reduced confidence
- Safe unknown rejection rather than wrong alert

### Scenario 7: Printed Photo or Phone Screen

Expected for the first version:

- It may incorrectly recognize the image

This limitation must be documented.

### Scenario 8: Person Leaves and Returns

Expected:

- No repeated alert during cooldown
- New alert after cooldown when configured

## Main Metrics

- Known-person recognition accuracy
- Unknown rejection rate
- False alert count per hour
- Missed alert count
- Average recognition latency
- Average CPU usage
- Average FPS

## Initial Acceptance Targets

For the controlled environment:

- Unknown rejection rate: at least 95%
- Wrong-person alert rate: below 1%
- False alerts during a 30-minute unknown-person test: 0
- Alert delay after appearance: below 3 seconds
- CPU utilization: acceptable for normal desktop use
- No repeated popup spam

These are project targets, not guarantees.

---

# Phase 11: Privacy and Security

## Biometric Data

Face embeddings are biometric identifiers and must be treated as sensitive data.

## Required Protections

1. Obtain consent from the three enrolled people.
2. Keep the embedding file local.
3. Do not upload embeddings to external services.
4. Restrict file permissions.
5. Do not store unknown faces by default.
6. Do not save video unless necessary.
7. Document how to delete a person's data.
8. Avoid using the system for high-stakes decisions.

## Suggested File Permissions

```bash
chmod 600 data/embeddings/known_faces.npz
```

## Person Removal

To remove one person:

1. Delete the person's reference-image folder.
2. Rerun enrollment.
3. Confirm that their name is absent from the embedding file.
4. Delete related snapshots if any were saved.

---

# Phase 12: Anti-Spoofing Upgrade

## Initial Limitation

The first version may recognize:

- A printed photo
- A phone displaying the person's face
- A replayed video

## Optional Upgrade

Add passive liveness or challenge-based liveness.

### Passive Options

- Texture-based spoof classifier
- Reflection analysis
- Screen moiré detection
- Depth estimation
- Blink analysis

### Challenge-Based Options

Ask the person to:

- Blink
- Turn left
- Turn right
- Smile

For a simple notification application, anti-spoofing can be a later milestone.

Do not claim the application is secure until spoof testing has been completed.

---

## 13. Suggested Core Classes

### `FaceEngine`

Responsibilities:

- Load InsightFace model
- Detect faces
- Extract aligned embeddings
- Return bounding boxes and quality metadata

Suggested methods:

```python
class FaceEngine:
    def detect_and_embed(self, frame):
        ...
```

### `FaceMatcher`

Responsibilities:

- Load known embeddings
- Compare live embeddings
- Apply threshold and margin
- Return identity decision

Suggested methods:

```python
class FaceMatcher:
    def match(self, embedding):
        ...
```

### `TemporalFilter`

Responsibilities:

- Store recent identity predictions
- Confirm stable recognition
- Remove expired tracks

Suggested methods:

```python
class TemporalFilter:
    def update(self, track_id, prediction, timestamp):
        ...
```

### `AlertManager`

Responsibilities:

- Track cooldowns
- Generate desktop popup
- Prevent duplicate alerts

Suggested methods:

```python
class AlertManager:
    def should_alert(self, person_name, timestamp):
        ...

    def send_alert(self, person_name, score):
        ...
```

### `EventLogger`

Responsibilities:

- Save recognition decisions
- Save alert events
- Support evaluation

Suggested methods:

```python
class EventLogger:
    def log_event(self, event):
        ...
```

---

## 14. Data Models

### Recognition Result

```python
from dataclasses import dataclass

@dataclass
class RecognitionResult:
    label: str
    accepted: bool
    best_score: float
    second_best_score: float
    margin: float
    reference_path: str | None
```

### Detection Result

```python
@dataclass
class DetectionResult:
    bbox: tuple[int, int, int, int]
    detection_score: float
    embedding: object
    face_width: int
    face_height: int
```

### Alert Event

```python
@dataclass
class AlertEvent:
    person_name: str
    timestamp: str
    similarity: float
    alert_sent: bool
```

---

## 15. Error Handling Requirements

The application should handle:

- Camera unavailable
- Camera disconnected during execution
- Missing embedding file
- Empty person folder
- No face in a reference image
- Multiple faces in a reference image
- Invalid image format
- Notification utility unavailable
- Corrupted configuration
- Corrupted embedding file
- Model download or loading failure
- Unsupported camera source

Each failure should produce a clear message and exit safely when recovery is not possible.

---

## 16. Testing Plan

### Unit Tests

#### Matcher

Test:

- Correct best match
- Unknown below threshold
- Rejection when margin is too small
- Multiple references for one identity
- Empty embedding database
- Non-normalized input handling

#### Temporal Filter

Test:

- Confirmation after required matches
- No confirmation below required matches
- Unknown frames interrupting history
- Track expiration
- Multiple simultaneous tracks

#### Alert Manager

Test:

- First alert allowed
- Duplicate alert blocked during cooldown
- Different person allowed during cooldown
- Alert allowed after cooldown
- Notification command failure

### Integration Tests

- Static reference enrollment
- Static known-image recognition
- Static unknown-image rejection
- Webcam recognition
- Popup notification
- End-to-end event logging

---

## 17. Performance Optimization Plan

Start with a correct implementation. Optimize only after measuring.

### First-Level Optimizations

- Lower camera resolution
- Process every second frame
- Set minimum face size
- Disable unknown logging
- Avoid snapshots
- Use CPU execution provider explicitly

### Second-Level Optimizations

- Track faces between recognition frames
- Run recognition only when a face changes significantly
- Cache track embeddings briefly
- Use a smaller detector
- Separate capture and inference threads

### Third-Level Optimizations

- Quantized ONNX models
- Intel OpenVINO provider
- Asynchronous pipeline
- Dedicated lightweight detector

---

## 18. Deployment Plan

### Option A: Manual Start

```bash
source .venv/bin/activate
python src/main.py
```

### Option B: Shell Launcher

Create `run.sh`:

```bash
#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"
source .venv/bin/activate
python src/main.py
```

Make executable:

```bash
chmod +x run.sh
```

### Option C: Ubuntu Startup Application

Create a desktop entry or systemd user service after the system is stable.

Do not configure automatic startup before:

- Camera recovery works
- Logging is stable
- Notifications are not spammy
- Thresholds are calibrated

---

## 19. Suggested Development Schedule

### Day 1

- Create environment
- Install dependencies
- Test webcam
- Test notifications
- Load face model

### Day 2

- Prepare reference-image folders
- Build enrollment script
- Save embeddings

### Day 3

- Build matcher
- Implement threshold and margin
- Test with static images

### Day 4

- Build real-time webcam loop
- Draw face boxes and labels
- Measure CPU usage

### Day 5

- Add temporal confirmation
- Add cooldown notifications
- Add CSV logging

### Day 6

- Collect calibration images
- Tune similarity threshold
- Tune margin and confirmation settings

### Day 7

- Run unknown-person tests
- Fix false alerts
- Improve error handling
- Write README

### Additional Week

- Add face tracking
- Add background mode
- Add startup service
- Add liveness detection
- Improve user interface

---

## 20. Minimum Viable Product Checklist

- [ ] Python environment created
- [ ] Webcam works
- [ ] Desktop popup works
- [ ] Face model runs on CPU
- [ ] Three reference-image folders created
- [ ] Enrollment script validates images
- [ ] Embeddings saved locally
- [ ] Matcher returns known or unknown
- [ ] Threshold is configurable
- [ ] Identity margin is configurable
- [ ] Temporal confirmation works
- [ ] Per-person cooldown works
- [ ] CSV logging works
- [ ] Unknown faces do not trigger alerts
- [ ] False alerts tested for at least 30 minutes
- [ ] README documents installation and use
- [ ] Biometric data deletion procedure documented

---

## 21. Version Roadmap

### Version 0.1: Static Image Prototype

- Enroll three people
- Test known and unknown images
- Print identity and score

### Version 0.2: Webcam Recognition

- Live camera
- Bounding boxes
- Known/unknown labels

### Version 0.3: Reliable Alerting

- Temporal confirmation
- Cooldown
- Desktop popup
- Event logs

### Version 0.4: Calibration and Evaluation

- Threshold calibration tool
- Metrics report
- False-alert testing

### Version 0.5: Usability

- Background mode
- Startup launcher
- Configuration validation
- Better logs

### Version 1.0: Stable Local Release

- Tested camera recovery
- Documented privacy controls
- Calibrated thresholds
- Reliable recognition in target environment
- Packaged launcher

### Version 1.1: Security Upgrade

- Passive liveness detection
- Photo and phone-screen spoof tests
- Encrypted embedding storage

---

## 22. Recommended Initial Settings

Use these only to begin testing:

```yaml
camera:
  width: 640
  height: 480
  process_every_n_frames: 2

recognition:
  similarity_threshold: 0.45
  identity_margin: 0.05

temporal_confirmation:
  history_size: 6
  required_matches: 4

alerts:
  cooldown_seconds: 60
```

These values must be replaced with calibrated values after collecting real camera samples.

---

## 23. Important Design Decisions

### Decision 1

Use pretrained embeddings instead of model training.

Reason:

- Only two or three images per person
- Better generalization
- Faster development
- No GPU required

### Decision 2

Keep an explicit `Unknown` class through threshold rejection.

Reason:

- A closed three-class classifier would force every face into one of the three identities.
- That would cause dangerous false alerts.

### Decision 3

Require temporal confirmation.

Reason:

- Single-frame recognition is unstable.
- Confirmation reduces false positives.

### Decision 4

Use per-person cooldowns.

Reason:

- Prevents popup spam.
- Allows different people to trigger independently.

### Decision 5

Calibrate using the final camera and room.

Reason:

- Similarity scores depend on lighting, distance, angle, camera quality, and reference-image quality.

### Decision 6

Keep all processing local.

Reason:

- Lower latency
- No recurring API cost
- Better privacy
- No internet dependency

---

## 24. Final Recommended Workflow

```text
1. Install dependencies.
2. Test the webcam.
3. Test Ubuntu notifications.
4. Add two or three images for each person.
5. Run the enrollment script.
6. Test recognition with static known images.
7. Test unknown-image rejection.
8. Start the webcam recognizer.
9. Collect real camera samples.
10. Calibrate threshold and margin.
11. Enable temporal confirmation.
12. Enable desktop popup.
13. Run a 30-minute false-alert test.
14. Improve reference images where necessary.
15. Add background startup only after stability is confirmed.
```

---

## 25. Final Feasibility Assessment

The project is technically feasible on the available Ubuntu CPU-based desktop.

Two or three images per person are enough to build the first prototype, provided that:

- The images are clear.
- The environment is reasonably controlled.
- A pretrained face-recognition model is used.
- Unknown-person rejection is implemented.
- Recognition is confirmed across multiple frames.
- Thresholds are calibrated using the actual webcam.

For better reliability, collect five to ten images per person from the final camera after the prototype works. This improves coverage of normal pose, expression, distance, and lighting changes without training a new model.
