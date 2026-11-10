# ML Models

This directory is **empty in the repo** — model weights are gitignored because they are large binaries.

## Setup

Download the YOLOv8 weights from the v1.0.0 release:

```bash
mkdir -p ml_models/roboflow_model
curl -L -o ml_models/roboflow_model/model.pt \
  https://github.com/Faris-as/trade-license-ocr/releases/download/v1.0.0/model.pt
```

Or export your own (re-trained) model from Roboflow and place it at:

```
ml_models/roboflow_model/model.pt
```

The server expects the file at that path and loads it at startup (`app/services/ocr_service.load_model()`). If it is missing, the app starts but every OCR request fails with `DetectionError` until you drop the file in place.
