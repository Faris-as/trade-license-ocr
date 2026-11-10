# Trade License OCR

Structured data extraction from **Abu Dhabi trade licenses**. Upload a license image or PDF, and the service returns validated JSON for license number, company name, dates, manager, and owners.

**Pipeline:** YOLOv8 object detection (Roboflow-trained) locates the field regions → each region is cropped and preprocessed → **EasyOCR** (English + Arabic) reads the text → a parser cleans, normalizes, and validates the result. PDF input is rendered to an image via **PyMuPDF** before detection.

| Platform | Component | Purpose |
|----------|-----------|---------|
| Detection | [YOLOv8](https://github.com/ultralytics/ultralytics) / [Roboflow](https://roboflow.com/) | Locate field regions on the document |
| OCR | [EasyOCR](https://github.com/JaidedAI/EasyOCR) | Read text from detected regions |
| API | [FastAPI](https://fastapi.tiangolo.com/) 0.104 + [Pydantic v2](https://docs.pydantic.dev/) | REST endpoint with typed response schemas |
| Runtime | [PyTorch](https://pytorch.org/) 2.1 · Python 3.10–3.11 | Model inference |

---

## Setup

Requires Python 3.10 or 3.11 with `pip`. With `make` (Linux/macOS/WSL):

```bash
git clone https://github.com/Faris-as/trade-license-ocr.git
cd trade-license-ocr

make setup        # venv + pip install -e ".[dev]"
make model        # download model.pt (~22MB) from the v1.0.0 release
make test         # run the parser test suite (no model needed)
make serve        # start the dev server → http://localhost:8000/docs
```

Without `make` (any OS):

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

mkdir -p ml_models/roboflow_model
curl -L -o ml_models/roboflow_model/model.pt \
  https://github.com/Faris-as/trade-license-ocr/releases/download/v1.0.0/model.pt

uvicorn app.main:app --host 0.0.0.0 --port 8000
```

> Model weights are not in the repository — they ship as a GitHub Release asset, or export your own from Roboflow (see `ml_models/README.md`).

### All make targets

| Command | Effect |
|---------|--------|
| `make setup` | Create `.venv`, install pinned dependencies (+ pytest) |
| `make model` | Download the YOLOv8 weights to `ml_models/roboflow_model/` |
| `make serve` | Dev server with autoreload |
| `make serve-prod` | Production-style server (`uvicorn --workers 1`) |
| `make test` | Parser unit tests |
| `make test-model` | Manual detection harness (needs a sample image in `uploads/`) |
| `make test-ocr` | Manual detection → crop → OCR harness |
| `make clean` | Remove venv, caches, and `uploads/` runtime artifacts |

---

## API

### `POST /ocr/trade-license`

Download one file: JPG / JPEG / PNG / PDF, up to 10MB.

```bash
curl -X POST "http://localhost:8000/ocr/trade-license" \
  -F "file=@/path/to/trade_license.jpg"
```

```python
import requests
resp = requests.post(
    "http://localhost:8000/ocr/trade-license",
    files={"file": open("trade_license.jpg", "rb")},
)
print(resp.json())
```

**Response**

```json
{
  "success": true,
  "message": "Trade license processed successfully",
  "data": {
    "license_number": "CN-2883802",
    "company_name": "TIGER FIRE FOR SECURITY SYSTEM",
    "establishment_date": "14-10-2019",
    "expiry_date": "25-12-2024",
    "manager_name": "NAJLA ANTAR ABDULLA ALJABERI",
    "owners": [
      { "name": "NAJLA ANTAR ABDULLA ALJABERI", "share_percentage": "100%" }
    ]
  },
  "validation": { "is_valid": true, "warnings": [], "errors": [] },
  "processing_time": 2.34,
  "timestamp": "2026-01-09T10:30:00.123456"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `data.license_number` | `string \| null` | Trade license number (`CN-XXXXXXX`) |
| `data.company_name` | `string \| null` | Registered company/trade name |
| `data.establishment_date` / `expiry_date` | `string \| null` | `DD-MM-YYYY` |
| `data.manager_name` | `string \| null` | Authorized signatory name |
| `data.owners` | `Owner[]` | Name + share percentage per owner |
| `validation` | `{is_valid, warnings, errors}` | Data-quality checks (expired license, missing number, share sums) |
| `processing_time` | `float` | Seconds spent end-to-end |

**Detected field classes** (what the model locates): `LICENSE_NUMBER`, `COMPANY_NAME`, `ESTABLISHMENT_DATE`, `EXPIRY_DATE`, `MANAGER_NAME`, `OWNER_NAME`, `SHARE_PERCENTAGE`.

**Errors:** `400` for unsupported/oversized/unreadable files or no fields detected; `500` for server-side failures — internals are logged server-side and never returned to clients. Interactive docs at `/docs` (Swagger) and `/redoc`; health checks at `/health` and `/ocr/health`.

---

## Testing

```bash
pytest tests/        # parser logic — pure stdlib, runs without the model
```

`test_model.py` and `test_ocr_pipeline.py` are manual harnesses for detection and the OCR pipeline; they need `model.pt` and a sample license image in `uploads/`.

---

## Configuration

| Setting | Where | Default |
|---------|-------|---------|
| `OCR_GPU` env var | EasyOCR device | `true` (set `false` for CPU-only servers) |
| CORS | `app/main.py` | `allow_origins=["*"]`, no credentials — LAN/dev; tighten before exposing publicly |
| Confidence threshold | `app/api/routes.py` | `0.25` |
| Max upload size | `app/utils/file_handler.py` | `10MB` |
| File upload limit and PDF render | `app/utils/file_handler.py` | page 1 @ ~200 DPI (licenses are single-page) |
| Serving | `run.py` is dev-only (reload) | prod: `uvicorn app.main:app --workers N` |

There is **no authentication** — treat this as an internal/LAN service; add auth + rate limiting before any public deployment.

---

## Project Structure

```
trade-license-ocr/
├── app/                      # FastAPI application
│   ├── main.py               # App factory, CORS, lifespan (model pre-load)
│   ├── api/routes.py         # POST /ocr/trade-license endpoint
│   ├── models/schemas.py     # Pydantic response models
│   ├── services/             # ocr_service (YOLO), ocr_pipeline (crop+OCR), parser_service
│   └── utils/file_handler.py # Upload validation, PDF render, cleanup
├── ml_models/                # YOLOv8 weights (not in repo — release asset)
├── tests/                    # pytest suite (parser, no model needed)
├── frontend/                 # planned
├── Makefile                  # one-command dev workflows
└── pyproject.toml            # deps, Python gate, pytest config
```

## Roadmap

- [x] YOLOv8 detection, OCR pipeline, parsing, validation
- [x] PDF input (single-page render via PyMuPDF)
- [x] Automated parser test suite + manual harnesses
- [x] Packaging (`pyproject.toml`) and `Makefile` workflows
- [ ] Arabic extraction quality verification + `_ar` mirror fields — [#1](https://github.com/Faris-as/trade-license-ocr/issues/1)
- [ ] Batch endpoint (inline, cap 10) — [#2](https://github.com/Faris-as/trade-license-ocr/issues/2)
- [ ] Frontend dashboard — [#3](https://github.com/Faris-as/trade-license-ocr/issues/3)
- [ ] Docker + auth/rate limiting for public deployment — [#4](https://github.com/Faris-as/trade-license-ocr/issues/4)

## Contributing

Fork → feature branch → PR. Please extend `tests/` for parser changes, use typed Pydantic schemas (`model_config`, not legacy `class Config`), mark deliberate simplifications with a `# shortcut:` comment naming their ceiling, and don't commit model weights or license scans.

## License

[MIT](LICENSE)
