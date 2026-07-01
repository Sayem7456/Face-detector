# Reference Image Guide

## Folder Layout

```
data/reference_images/
├── person_1/          # One directory per identity
│   ├── image_1.jpg
│   ├── image_2.jpg
│   └── image_3.jpg
├── person_2/
│   └── ...
└── person_3/
    └── ...
```

Directory names become identity labels. Choose names that are meaningful to you
(e.g. "alice", "bob", "charlie"). Do not use dots, slashes, or special
characters.

## Recommended Image Quality

Each image should ideally have:

- **Face width** at least 150 pixels (the detector minimum is 70 px but larger
  gives better embeddings).
- **Clear eyes** — no sunglasses, heavy shadows, or extreme squinting.
- **Limited motion blur** — avoid fast head movement while capturing.
- **Limited compression artifacts** — use JPEG quality 90+ or PNG.
- **No extreme rotation** — keep the face roughly upright (±30°).
- **Frontal or near-frontal pose** — the pretrained model works best with
  frontal faces.
- **Good exposure** — avoid overexposed (washed out) or underexposed (too dark)
  faces.

## Pose and Lighting Variation

For the prototype, two or three images per person with **different expressions
or slight head angles** are enough:

```
Front view      → slightly left   → neutral expression
```

Once the prototype works, improve results by adding:

- Slightly left
- Slightly right
- Neutral expression
- Normal expression
- With glasses if usually worn
- Under expected room lighting

## Minimum Starter Images

**Two or three images per person are enough** for the prototype because the
system uses a pretrained face-recognition model — it does not train a new
classifier.

```
person_1/
├── front.jpg
├── left.jpg
└── right.jpg
```

## Recommended Five to Ten Images

After the prototype works, collect **five to ten images per person** captured
from the actual target webcam. More images improve recognition coverage across
normal pose, expression, distance, and lighting changes — without requiring any
model training.

## Consent and Privacy

- **Obtain explicit consent** from every person whose face you store.
- Images must be kept **local** — do not upload, share, or commit them.
- Face embeddings (the numerical vectors derived from images) are biometric
  identifiers. Treat them as sensitive data.
- **To delete a person's data**: delete their directory under
  `data/reference_images/` and rerun enrollment.
- The `.gitignore` file prevents biometric files from being committed.

## Running Validation

```bash
python scripts/validate_reference_images.py
```

Optional JSON report:

```bash
python scripts/validate_reference_images.py --json-report data/validation_report.json
```

The script:

1. Scans every identity directory under `data/reference_images/`.
2. Decodes each image.
3. Detects faces using the pretrained model.
4. Rejects images with zero faces, multiple substantial faces, or faces that
   are too small.
5. Prints a per-identity summary.
6. Exits with code 0 only when every identity has at least one valid image.

## Do Not Commit Images

The `.gitignore` file ignores `data/reference_images/` content. Run
`git check-ignore data/reference_images/person_1/photo.jpg` to confirm.
**Never use `git add -f` to override this.**
