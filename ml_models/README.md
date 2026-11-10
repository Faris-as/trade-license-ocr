# ML Models

This directory is **empty in the repo** — model weights are gitignored because they are large binaries.

## Setup

Export your Roboflow-trained YOLOv8 model and place it here:

```
ml_models/roboflow_model/model.pt
```

The server loads it at startup (`app/services/ocr_service.load_model()`). If it is missing, the app starts but every OCR request fails with `DetectionError` until you drop the file in place.
