# SafeSight – Context-Aware Behaviour Intelligence

SafeSight is an end-to-end AI pipeline and command center dashboard that analyzes industrial CCTV footage to track workers, understand their behaviour, and generate explainable risk alerts based on configurable safety policies.

## 🎯 Problem Statement

Continuous CCTV monitoring in warehouses and industrial factories is often manual, tedious, and prone to human error. While simple AI systems can detect people or vehicles, they fail to understand the *context* of what those people are doing. A person walking in a designated pedestrian aisle is safe; a person running through an active loading bay is a critical risk. 

Identifying these unusual or unsafe behaviours requires a system that goes beyond simple object detection to provide continuous tracking, spatial awareness (zones), timestamped event sequences, and explainable justifications for why a specific action is considered risky.

## 💡 Solution

SafeSight solves this by passing uploaded CCTV video through a deep learning pipeline (YOLOv8 + ByteTrack) to identify and persistently track individuals. 

The system then analyzes their movement speed (walking, running, idle), maps their locations to predefined spatial zones (e.g., Restricted Areas, Loading Bays), and evaluates their behaviour against configured context rules (e.g., shift hours). The backend processes this data to generate a dynamic, interpretable risk score (0-100) and extracts physical evidence snapshots. All results, including the AI-annotated video and chronological event timeline, are immediately presented on a modern React dashboard.

## ✨ Features

- **Person Detection:** Detects people frame-by-frame using YOLOv8.
- **Persistent Tracking:** Tracks individuals continuously across frames using ByteTrack.
- **Behaviour Analysis:** Computes movement speed to classify actions as walking, running, or idle.
- **Zone-Based Analysis:** Maps person coordinates to predefined polygon zones using Point-in-Polygon logic.
- **Context-Aware Analysis:** Evaluates behaviour against configured time-based policies (e.g., shift hours).
- **Behaviour Sequence Analysis:** Groups frame-level actions into logical event sequences.
- **Configurable Risk Scoring:** Calculates dynamic 0-100 risk scores using a rule-based engine.
- **Explainable Alerts:** Generates human-readable text explaining exactly why an alert was triggered.
- **Evidence Generation:** Captures and saves JPEG snapshots of high-risk incidents.
- **Annotated CCTV Video:** Renders bounding boxes, IDs, and risk overlays directly onto the output video.
- **Person Activity Timeline:** Displays a chronological log of all tracked activity and severity.
- **Dynamic React Dashboard:** Presents metrics, charts, and incidents using real API data.

## 🏗️ System Architecture

```text
CCTV Video
      ↓
Video Upload (FastAPI)
      ↓
YOLOv8 Detection
      ↓
ByteTrack Tracking
      ↓
Behaviour Analysis (Speed, Idle, Running)
      ↓
Zone / Context Analysis
      ↓
Risk Assessment (Rule-based scoring)
      ↓
Evidence & Events (Snapshots & JSON)
      ↓
FastAPI Backend (REST API)
      ↓
React Dashboard (Vite / Tailwind / Recharts)
```

## 🛠️ Technologies Used

### Frontend
- **React (TypeScript):** Component-based UI.
- **Vite:** Fast frontend build tool.
- **Tailwind CSS:** Utility-first styling with a premium glassmorphism aesthetic.
- **Recharts:** Dynamic data visualization (Pie and Bar charts).
- **Lucide React:** Iconography.

### Backend
- **FastAPI:** High-performance asynchronous REST API framework.
- **Uvicorn:** ASGI web server.
- **Pydantic:** Data validation and schema definition.

### AI / Computer Vision
- **YOLOv8 (Ultralytics):** Deep learning object detection (yolov8n.pt).
- **ByteTrack:** Multi-object tracking algorithm.
- **OpenCV (cv2):** Video frame reading, writing, and annotation.
- **NumPy & Shapely:** Matrix operations and spatial polygon geometry.

### Data / Storage
- **Local File System:** Stores raw uploaded videos, processed annotated videos, evidence snapshots, JSON metrics, and HTML incident reports. *(No external database is currently used; all data is file-based).*

## 📂 Project Structure

```text
SafeSight/
├── backend/
│   ├── main.py                     # FastAPI application entrypoint
│   ├── schemas.py                  # API data models
│   ├── routes/                     # Video, events, and incident API endpoints
│   └── services/                   # Background processing manager
├── core/
│   ├── detector.py                 # YOLOv8 integration
│   ├── tracker.py                  # ByteTrack integration
│   ├── behaviour.py                # Speed and action classification
│   ├── zones.py                    # Polygon zone geometry engine
│   ├── risk.py                     # Configurable risk score calculator
│   └── report.py                   # JSON and HTML report generator
├── frontend/
│   ├── src/
│   │   ├── components/             # React UI components (Navbar, Charts, Tables)
│   │   ├── pages/Dashboard.tsx     # Main dashboard layout
│   │   └── services/api.ts         # Backend API client
│   ├── package.json
│   └── vite.config.ts
├── config/
│   ├── zones.json                  # Polygon coordinates for spatial areas
│   ├── context_config.json         # Shift hours and temporal rules
│   └── risk_config.json            # Base risk weights and multipliers
├── videos/                         # Storage for raw and processed MP4s
├── output/                         # Generated evidence, reports, and AI data
├── pipeline.py                     # Core AI synchronous execution pipeline
├── requirements.txt                # Python dependencies
└── README.md                       # Project documentation
```

## ⚙️ Installation

### 1. Repository Setup
```bash
git clone https://github.com/himalilibel-06/HackNex_Hackathon.git
cd HackNex_Hackathon
```

### 2. Python Environment & Backend
Requires Python 3.9+.
```bash
python -m venv venv
venv\Scripts\activate      # On Windows
pip install -r requirements.txt
```

### 3. Frontend Dependencies
Requires Node.js 18+.
```bash
cd frontend
npm install
```

## ▶️ Running the Project

You must run both the backend and frontend simultaneously in separate terminals.

### 1. Start the FastAPI Backend
Open Terminal 1:
```bash
# Ensure you are in the root directory and venv is active
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
*(API runs on `http://127.0.0.1:8000`)*

### 2. Start the React Frontend
Open Terminal 2:
```bash
cd frontend
npm run dev
```
*(Dashboard runs on `http://localhost:5173`)*

## 🎥 How to Use SafeSight

1. Open the dashboard at `http://localhost:5173`.
2. Click **Upload Video** and select a raw CCTV `.mp4` file.
3. Once uploaded, click the **Run SafeSight AI** button.
4. Wait for the real-time background processing to complete (the progress bar will track frame-by-frame analysis).
5. View the generated summary metrics, dynamic Risk Chart, and Annotated CCTV video.
6. Scroll through the chronological **Person Activity Timeline**.
7. Filter data by clicking a specific person in the **Tracked Workers Directory**.
8. Inspect critical/high-risk events in the **Safety Incidents** table, and click "Details" to view explanations and snapshot evidence.

## 📊 Output

When a video is processed, SafeSight generates actual files on the backend:
- `{video_id}_risk.mp4`: An annotated video with bounding boxes, IDs, and risk overlays.
- `{video_id}_summary.json`: High-level metrics and tracking statistics.
- `{video_id}_timeline.json`: A detailed chronological sequence of events.
- `{video_id}_incidents.json`: Filtered high-risk alerts.
- `{video_id}_tracks.json`: Comprehensive data on every tracked individual.
- Evidence JPEG snapshots captured at the exact moment of high-risk incidents.

## 🧠 Behaviour Understanding

The current implementation derives behaviour mechanically from tracking data:
- **Walking:** Moderate pixel displacement between frames.
- **Running:** High pixel displacement between frames.
- **Idle:** Near-zero pixel displacement over a sustained period.
- **Zone Presence:** Detected when a person's bottom-center bounding box coordinate intersects a defined polygon zone.
- **Zone Entry/Exit:** Detected when a person's coordinates transition across zone boundaries.

## ⚠️ Risk Assessment

Risk scoring in this project is **rule-based and configurable**, not machine-learned.

Risk is calculated using values defined in `config/risk_config.json`. The engine adds a base score for a specific behaviour (e.g., Running = 30) and applies multipliers based on context (e.g., inside a Restricted Zone = x1.5, during Non-Shift hours = x1.2). Scores are capped at 100.

## 🔍 Explainable Behaviour Alerts

For every logged incident, the API returns a structured object containing:
- **Person ID:** (e.g., P-01)
- **Timestamp:** The exact second the incident occurred in the video.
- **Behaviour:** The classified action (e.g., running).
- **Zone:** The spatial location (e.g., Loading Bay).
- **Risk Level:** LOW, MEDIUM, HIGH, or CRITICAL.
- **Reason / Explanation:** A generated human-readable sentence (e.g., *"Person P-01 was running in Loading Bay during Night Shift"*).
- **Evidence:** Array of URLs pointing to extracted CCTV snapshot images.

## 📁 Data and Resources

- **CCTV Video Sources:** Uses standard `.mp4` files uploaded by the user. (Source/license information should be added for the final demonstration footage).
- **Pretrained Models:** YOLOv8 Nano (`yolov8n.pt`) via the Ultralytics library.
- **External Libraries:** ByteTrack (via Ultralytics tracking integration), Shapely for spatial mapping.

## 📌 Scope

### Implemented
- YOLOv8 Person Detection
- ByteTrack Persistent ID Tracking
- Configurable Polygon Zone logic
- Speed-based behaviour classification
- Rule-based dynamic risk scoring
- Snapshot evidence extraction
- Complete FastAPI backend
- Dynamic React / Tailwind / Recharts dashboard

### Future Enhancements
- Live RTSP/IP Camera stream processing (currently processes uploaded MP4s).
- Deep learning-based action recognition (e.g., detecting "lifting" or "falling" rather than just speed).
- Persistent relational database (PostgreSQL) instead of local JSON file storage.
- Real-time email/webhook notifications for CRITICAL incidents.

## 🚧 Limitations

- **Camera Angle Dependency:** Because behaviour is derived from pixel displacement, extreme camera angles or occlusion can cause inaccurate speed calculations.
- **Tracking ID Switches:** If a person leaves the camera frame or is heavily obscured, ByteTrack may assign them a new ID when they reappear.
- **Rule-Based Risk:** The risk engine relies heavily on properly configured zones and multipliers rather than understanding abstract safety concepts.

## 🎯 HackNex Problem Statement

**HNX26PSI07 – Autonomous Vision & Behaviour Understanding**

SafeSight directly addresses this problem statement by providing continuous, automated monitoring of CCTV feeds. It shifts the paradigm from simple "person detection" to true "behaviour understanding" by applying temporal tracking, spatial zones, and contextual rules. The system successfully separates normal operations from unusual behaviour, logs accurate timestamps, and most importantly, provides *explainable* evidence to justify its risk assessments.

## 👥 Team

- **Hima Lilibel A** – Team Leader & Project Coordinator
- **Rithanya S** – AI / Computer Vision & Backend Developer
- **Mridula A V** – Frontend Developer & UI/UX Designer
- **Raajaganapathy V** – Testing, Integration & Documentation

## 📜 Acknowledgements

- [Ultralytics](https://github.com/ultralytics/ultralytics) for the YOLOv8 object detection framework.
- [ByteTrack](https://github.com/ifzhang/ByteTrack) for the multi-object tracking algorithm.
- [FastAPI](https://fastapi.tiangolo.com/) for the high-performance Python backend.
- [React](https://reactdev.com/), [Vite](https://vitejs.dev/), and [Tailwind CSS](https://tailwindcss.com/) for the frontend stack.
- [Recharts](https://recharts.org/) for declarative React charts.
