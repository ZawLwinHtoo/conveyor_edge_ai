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

### 1. 💻 Local Laptop Camera
- **Setup**: None required!
- **How to use**: Select **💻 Local Laptop Camera**, then click **▶️ Start AI Detection Node**.

### 2. 📱 DroidCam (Phone Camera)
- **Method A (Direct Wi-Fi IP - Easiest)**:
  1. Open **DroidCam** on your iPhone or Android (must be on the same Wi-Fi network).
  2. Select **📶 Wi-Fi IP Address** in the dashboard and enter the IP shown on your phone screen (e.g. `192.168.1.15:4747`).
  3. Click **▶️ Start AI Detection Node**.
- **Method B (USB / DroidCam PC Client)**:
  1. Open **DroidCam** on your phone.
  2. Open **DroidCam Client** on your PC (`C:\Program Files\DroidCam\Client\DroidCamApp.exe`).
  3. Connect via USB or Wi-Fi and click **Start** in DroidCam Client.
  4. Select **🔌 USB / DroidCam PC Client** in the dashboard and click **▶️ Start AI Detection Node**.