# SafeSight 🛡️
> **Context-Aware Behaviour Intelligence and Explainable Risk Scoring for Factory & Warehouse Safety**

"WE DON'T JUST DETECT, WE UNDERSTAND, JUSTIFY, AND DOCUMENT."

---

## 📌 Architecture Overview

```text
                    REACT FRONTEND (Vite / TypeScript / Tailwind)
                                        │
                                        │ HTTP / JSON REST APIs
                                        ▼
                    FASTAPI BACKEND (Uvicorn / Pydantic)
                                        │
                                        ▼
                     BACKGROUND AI PROCESSING SERVICE
                                        │
                                        ▼
                         SAFE SIGHT AI CORE ENGINE
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        ▼                               ▼                               ▼
  YOLOv8 Detection            ByteTrack Tracking               Behaviour Analysis
  (Person & Vehicles)         (Persistent Track IDs)          (Speed, Idle, Running)
        │                               │                               │
        └───────────────────────────────┼───────────────────────────────┘
                                        ▼
                            Spatial Polygon Zones
                                        │
                                        ▼
                            Context-Aware Intelligence
                                        │
                                        ▼
                            Behaviour Sequence Engine
                                        │
                                        ▼
                            Dynamic Risk Scoring (0-100)
                                        │
                                        ▼
                            Explainable Alert Engine
                                        │
                                        ▼
                            Evidence & Snapshots Recorder
                                        │
                                        ▼
                            Automatic Incident Reports (JSON & HTML)
```

---

## 🛠️ Project Directory Structure

```text
warehouse-ai/
├── backend/
│   ├── main.py                     # FastAPI application entrypoint with CORS & static mounts
│   ├── schemas.py                  # Pydantic data models for API endpoints
│   ├── routes/
│   │   ├── videos.py               # Video upload, listing, and processing trigger routes
│   │   ├── events.py               # Events, tracks, and timeline API endpoints
│   │   ├── incidents.py            # Safety incident management endpoints
│   │   └── reports.py              # Evidence image and report file serving endpoints
│   └── services/
│       └── processing_service.py   # State manager & background pipeline executor
├── core/
│   ├── video.py                    # OpenCV video inspection & metadata loader
│   ├── detector.py                 # YOLOv8 object detector (Person & Vehicles)
│   ├── tracker.py                  # ByteTrack multi-object persistent person tracker
│   ├── behaviour.py                # Movement speed, action state, & vehicle proximity
│   ├── zones.py                    # Spatial polygon zone manager & point-in-polygon engine
│   ├── context.py                  # Context-aware intelligence engine & explanation generator
│   ├── sequence.py                 # Multi-event sequence analyzer & timeline builder
│   ├── risk.py                     # Configurable 0-100 dynamic risk score calculator
│   ├── explanation.py              # Explainable alert text generator
│   ├── evidence.py                 # Evidence snapshot image recorder
│   ├── incidents.py                # High/Critical incident logger
│   └── report.py                   # Master JSON & HTML incident report generator
├── frontend/                       # React + TypeScript + Vite + Tailwind Dashboard
│   ├── src/
│   │   ├── components/             # Navbar, SummaryCards, VideoUpload, IncidentTable, Modal, etc.
│   │   ├── pages/Dashboard.tsx     # Main interactive dashboard page
│   │   ├── services/api.ts         # Centralized API service client
│   │   └── types/index.ts          # TypeScript API data interfaces
│   ├── .env                        # VITE_API_BASE_URL=http://localhost:8000
│   ├── package.json
│   └── vite.config.ts
├── config/
│   ├── zones.json                  # Polygon zone definitions
│   ├── context_config.json         # Shift hours & context policy rules
│   └── risk_config.json            # Configurable risk weights & severity thresholds
├── videos/
│   ├── raw/                        # Input CCTV video clips
│   └── processed/
├── output/
│   ├── annotated/                  # Annotated video outputs, full events CSV/JSON, tracks
│   ├── evidence/                   # Snapshot evidence image files
│   └── reports/                    # Generated JSON & HTML incident reports
├── pipeline.py                     # End-to-end command line AI processing entrypoint
├── video_loader.py                 # Command line video metadata inspector
├── requirements.txt                # Python dependencies
└── README.md                       # Project documentation
```

---

## 🚀 How to Run the Application

### 1. Start the FastAPI Backend Server
In Terminal 1:
```bash
cd e:\Hacknex\warehouse-ai
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- **Backend API Base URL**: `http://127.0.0.1:8000`
- **Interactive API Documentation (Swagger)**: `http://127.0.0.1:8000/docs`

---

### 2. Start the React Frontend Dashboard
In Terminal 2:
```bash
cd e:\Hacknex\warehouse-ai\frontend
npm run dev
```
- **React Dashboard URL**: `http://localhost:5173`

---

## 🌐 End-to-End API Routes

- `GET /api/health` — Backend health status
- `POST /api/videos/upload` — Upload raw CCTV video
- `GET /api/videos` — List registered CCTV clips
- `POST /api/videos/{id}/process` — Launch background SafeSight AI pipeline
- `GET /api/videos/{id}/status` — Poll background pipeline progress
- `GET /api/videos/{id}/summary` — Summary metric cards data
- `GET /api/videos/{id}/events` — Filtered behaviour events data
- `GET /api/videos/{id}/tracks` — Per-person tracking Lifespan directory
- `GET /api/videos/{id}/incidents` — Logged safety incidents list
- `GET /api/videos/{id}/timeline` — Chronological person activity timeline
- `GET /api/videos/{id}/evidence/{filename}` — Serve evidence snapshot image
- `GET /api/videos/{id}/reports/{filename}` — Serve HTML / JSON incident reports

---

## ⚙️ Honest Technical Limitations
- **Configurable Risk Policies**: Risk scores and shift hours are rule-based policy values configured in `config/risk_config.json`, not learned probabilities.
- **Camera Perspective**: 2D CCTV perspective displacement is measured in pixels per frame rather than calibrated 3D real-world speed.
