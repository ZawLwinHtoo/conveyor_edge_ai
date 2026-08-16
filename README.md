# Edge AI Conveyor Belt Defect Mesh Network

## Project Overview

The Edge AI Conveyor Belt Defect Mesh Network is a computer vision-based
defect detection and monitoring system for conveyor belts.

The system uses an edge device with a camera to detect conveyor belt defects
using a YOLO-based AI model. Detected defects are sent through a mesh-style
communication system to another node, where detection results are logged.
A Streamlit dashboard provides real-time monitoring and visualization of
the detected defects.

## System Architecture

Camera
   ↓
Edge Node 1
   ↓
YOLO AI Defect Detection
   ↓
Mesh Alert Communication
   ↓
Node 2
   ↓
Detection Logging
   ↓
Streamlit Dashboard

## Main Components

### 1. Edge Node – AI Detection

File:

`edge_node_vision.py`

Responsibilities:

- Captures video from the camera
- Performs defect detection using YOLO
- Uses the trained `best.pt` model
- Calculates detection confidence
- Generates bounding boxes
- Sends detected defect information to Node 2

### 2. Node 2 – Alert Receiver and Logger

File:

`node2.py`

Responsibilities:

- Receives detection alerts from the edge node
- Processes detection information
- Saves detection records into `detections.csv`
- Provides the detection data for dashboard monitoring

### 3. Streamlit Dashboard

File:

`dashboard.py`

Responsibilities:

- Displays total detected defects
- Displays defect statistics
- Shows recent detections
- Displays confidence values
- Displays detection information from `detections.csv`

## Technologies Used

- Python
- YOLO / Ultralytics
- OpenCV
- Streamlit
- Pandas
- TCP/IP Socket Communication
- CSV Data Logging

## Project Files

```text
conveyor_edge_ai/
│
├── best.pt
├── dashboard.py
├── detections.csv
├── edge_node_vision.py
├── node2.py
├── README.md
└── requirements.txt

## How to Run (1-Terminal / 1-Click Execution)

You only need to run **one command** in your terminal:

```powershell
.\.venv\Scripts\python.exe -m streamlit run dashboard.py
```

*(Or double-click `run_dashboard.bat` on Windows).*

Opening the dashboard automatically manages background services (`node2.py` and `edge_node_vision.py`).

---

## Camera Setup Instructions for Users

You can choose your camera device directly inside the **⚙️ Camera Selection & Edge AI Control Center** at the top of the dashboard:

### 1. 💻 PC / Laptop Built-in Webcam (Camera 0)
- **Setup**: None required!
- **How to use**: Select **Option 1**, then click **▶️ Start AI Detection Node**.

### 2. 📱 iPhone / DroidCam / External USB Camera (Camera 1)
- **Best & Most Reliable Setup (DroidCam)**:
  1. Download **DroidCam** (App Store on iPhone / Play Store on Android).
  2. Download free **DroidCam Client for Windows** on your laptop from [dev47apps.com](https://www.dev47apps.com/).
  3. Connect your phone to your PC via USB cable (or same Wi-Fi network).
  4. Open DroidCam on both phone and PC, then click **Start**.
  5. Select **Option 2: 📱 iPhone / DroidCam / USB Camera (Camera 1)** in the dashboard and click **▶️ Start AI Detection Node**.
- *(Alternative for iPhone)*: Use **Camo App** (iPhone) + **Camo Studio** (Windows). *Note: Requires Microsoft Windows App SDK Runtime installed on Windows 10/11.*

### 3. 🌐 Smartphone IP Camera Stream (HTTP URL)
- **Step 1**: Connect Phone & PC to the **same Wi-Fi network**.
- **Step 2 (Important)**: Turn **OFF** any VPN/Proxy (e.g. NekoBox, WARP, NordVPN) or iCloud Private Relay on your laptop and phone, as VPNs block local stream routing.
- **Step 3 (App Setup)**:
  - **iPhone**: Download **IP Camera Lite** or **DroidCam** (App Store). Tap *Start* and note the stream URL (e.g., `http://192.168.1.9:8081/video`).
  - **Android**: Download **IP Webcam** (Play Store). Tap *Start server* and note the stream URL (e.g., `http://192.168.1.15:8080/video`).
- **Step 4**: Test `http://<PHONE_IP>:8081/video` in your laptop browser first to confirm the stream is live.
- **Step 5**: Paste the URL into **Option 3** in the dashboard and click **▶️ Start AI Detection Node**.

### 4. ⚙️ Conveyor Belt Simulation Mode
- **Setup**: No hardware or camera needed!
- **How to use**: Select **Option 4: ⚙️ Conveyor Belt Simulation Mode** and click **▶️ Start AI Detection Node** to generate synthetic conveyor belt defect simulations automatically for testing.