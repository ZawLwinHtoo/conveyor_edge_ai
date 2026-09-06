# Conveyor Belt Edge AI Quality Inspection System
## Comprehensive Technical Documentation & Presentation Reference

---

## 1. Executive Summary & Industrial Purpose

### What Is This Project?
This project is an **Autonomous Industrial Edge AI Computer Vision System** built for real-time surface flaw inspection on heavy-duty industrial conveyor belts (such as those used in mining, cement factories, distribution warehouses, and manufacturing plants).

### The Industrial Problem It Solves
Conveyor belts operate 24/7 under high mechanical tension, transporting tons of abrasive materials across miles of rough terrain. When sharp debris or foreign metal objects wedge into a transfer chute, they act like a fixed knife, slicing a rubber belt lengthwise across hundreds of meters in just a couple of minutes (causing tens of thousands of dollars in damages and halting production).

Human visual monitoring of conveyor belts is dangerous, fatiguing, and inconsistent. This system provides:
* **24/7 Autonomous Optical Inspection**: Constant monitoring at 30 FPS.
* **Millisecond Edge Latency**: Runs entirely on local hardware with zero dependency on cloud internet.
* **Instant Automated Triage**: Differentiates between catastrophic rips (urgent emergency stop), routine seams (belt joints), and minor punctures (preventative patching).

---

## 2. Distributed Edge Architecture

The system uses a **Decoupled Distributed Edge Architecture** where three independent nodes run concurrently and communicate across local network sockets:

```text
 ┌──────────────────────────────────────────────────────────────────┐
 │                    NODE 1: VISION EDGE ENGINE                    │
 │                     (edge_node_vision.py)                        │
 │                                                                  │
 │  [ Camera Stream: Webcam / DroidCam Phone / Synthetic Sim ]      │
 │                               │                                  │
 │                               ▼                                  │
 │              [ CLAHE Contrast Normalization ]                    │
 │                               │                                  │
 │                               ▼                                  │
 │              [ YOLOv8 Neural Network Inference ]                 │
 │                               │                                  │
 │                               ▼                                  │
 │           [ Physical Texture & Edge Truth Filter ]               │
 │                               │                                  │
 │                               ▼                                  │
 │        [ OpenCV Morphological & Circularity Verifier ]           │
 │                               │                                  │
 │                               ▼                                  │
 │               [ Multi-Frame Persistence Gater ]                  │
 └─────────────────┬──────────────────────────────┬─────────────────┘
                   │                              │
     HTTP MJPEG Stream (Port 5014)         UDP Socket (Port 5012)
                   │                       JSON Defect Telemetry Payload
                   ▼                              ▼
 ┌──────────────────────────────────┐   ┌───────────────────────────┐
 │       OPERATOR DASHBOARD         │   │   NODE 2: DEFECT RECORDER │
 │         (dashboard.py)           │   │         (node2.py)        │
 │                                  │   │                           │
 │ • Real-Time In-Browser Video     │   │ • Listens on UDP 5012     │
 │ • Defect Counts & Statistics     │   │ • Appends record to CSV   │
 │ • Category Distribution Bars     │   │                           │
 │ • Confidence Trend Line Chart    │   └─────────────┬─────────────┘
 │ • Full-Width History Table       │                 │
 │ • Hardware Subprocess Controls   │                 ▼
 └──────────────────────────────────┘       [ detections.csv ]
```

### End-to-End System Workflow
1. **Video Ingestion**: `edge_node_vision.py` captures frames from a laptop camera, smartphone camera (via DroidCam IP stream/USB), or a built-in synthetic conveyor simulator.
2. **Preprocessing & Neural Inference**: Frames are contrast-normalized using **CLAHE** and evaluated by **YOLOv8** at 30 FPS.
3. **Computer Vision Verification**: Candidate bounding boxes pass through physical variance checks (to reject shadows and plain walls) and contour circularity analysis (to separate tears from holes).
4. **Mesh Transmission**: When a genuine defect is confirmed, Node 1 broadcasts a compact JSON packet over a **local UDP socket (`127.0.0.1:5012`)** to Node 2.
5. **Data Recording**: `node2.py` receives the packet and logs the event (timestamp, defect type, confidence, coordinates) into `detections.csv`.
6. **Live Visualization**: 
   - Node 1 serves a low-latency MJPEG video stream directly over HTTP on port `5014`.
   - `dashboard.py` displays the live camera stream with green/color-coded defect overlays and loads the logged records into responsive charts, cards, and data tables.

---

## 3. Technologies, Frameworks & Libraries Used

| Component / Layer | Technology | Version / Tool | Purpose in Project |
| :--- | :--- | :--- | :--- |
| **Object Detection AI** | **Ultralytics YOLOv8** | Python Library | Real-time object localization and classification. |
| **Image Processing** | **OpenCV** | `opencv-python` | Video capture, CLAHE lighting equalization, Canny edge detection, and contour circularity analysis. |
| **Numerical Processing**| **NumPy** | `numpy` | Matrix manipulation, spatial Euclidean distance, and variance calculations. |
| **Web Dashboard** | **Streamlit** | `streamlit` | Reactive, industrial dark-slate operator interface. |
| **Interactive Charts** | **Altair & Vega-Lite**| `altair` | Time-series certainty trend line and area curves. |
| **Data Tabulation** | **Pandas** | `pandas` | Tabular parsing, rolling metrics, and CSV time-series handling. |
| **Video Server** | **Python Standard Library** | `http.server` | Zero-dependency, multi-threaded MJPEG streaming on port 5014. |
| **Inter-Node Comm** | **Socket API** | `socket` (UDP) | Connectionless, low-latency inter-process messaging. |
| **Process Control** | **`psutil` & `subprocess`** | Python Standard | Clean process life-cycle management (starting/stopping cameras). |

---

## 4. The 5 Defect Categories & Failure Modes

The system is trained and calibrated around **5 standard industrial conveyor failure conditions**:

```text
 1. LARGE HOLE           2. SMALL HOLE           3. BELT JOINT (SEAM)
   ┌───────────┐           ┌───────────┐           ┌───────────────────┐
   │   █████   │           │     ▪     │           │═══════════════════│
   │  ███████  │           │           │           │═══════════════════│
   │   █████   │           │           │           └───────────────────┘
   └───────────┘           └───────────┘           Aspect Ratio >= 2.5
   Circularity > 0.40      Circularity > 0.40
   Area >= 2400 px         Area < 2400 px

 4. LARGE TEAR           5. SMALL TEAR
   ┌───────────┐           ┌───────────┐
   │    ╱      │           │     ╱     │
   │   ╱       │           │           │
   │  ╱        │           │           │
   └───────────┘           └───────────┘
   Circularity < 0.38      Circularity < 0.38
   Length >= 95 px         Length < 95 px
```

| Category | Indonesian Dataset Name | Physical Description | Industrial Severity | Action Triage |
| :--- | :--- | :--- | :--- | :--- |
| **Belt Joint** | `Sambungan Belt` | Vulcanized rubber seam or metal fastener connecting belt segments. | Normal Operational Feature | **Belt Joint / Normal:** Prevents false alarms on every belt revolution. |
| **Large Hole** | `Lubang Besar` | Deep perforation piercing entirely through rubber and fabric carcass (>50mm). | Critical Failure | **Critical Defect:** Stop belt; prevents material from leaking onto motor rollers. |
| **Small Hole** | `Lubang Kecil` | Superficial surface puncture or rock impact gouge (<25mm). | Low / Medium Wear | **Minor Flaw:** Scheduled weekend maintenance patching. |
| **Large Tear** | `Sobekan Besar` | Longitudinal rip extending along the belt length. | Catastrophic Disaster | **Critical Defect:** Emergency belt stop to avoid slicing the belt in two. |
| **Small Tear** | `Sobekan Kecil` | Edge fraying or minor diagonal surface laceration. | Medium Warning | **Minor Flaw:** Warns of belt mistracking against the steel frame. |

---

## 5. How the Model Was Trained & How Detection Works

### The Neural Network Model (`best.pt`)
- **Architecture**: **YOLOv8 Nano (`yolov8n`)**, a deep single-stage convolutional object detection network.
- **Weights File Size**: ~6.2 MB (~3.2 million parameters).
- **Backbone**: CSPDarknet53 feature extractor with Path Aggregation Network (PANet) neck for multi-scale feature maps (P3, P4, P5).
- **Training Hyperparameters**:
  - Image input size: $640 \times 640$ pixels.
  - Loss formulation: Complete IoU (CIoU) for bounding box regression + Binary Cross-Entropy (BCE) for class classification + Distribution Focal Loss (DFL).
  - Pre-trained on an industrial Indonesian dataset with classes: `Lubang Besar`, `Lubang Kecil`, `Sambungan Belt`, `Sobekan Besar`, and `Sobekan Kecil`.

### The Hybrid Computer Vision Pipeline (Overcoming Nano Model Limitations)
Because lightweight Nano models can struggle with lighting variations or confuse an elongated hole with a tear, this project combines **YOLOv8 deep learning proposals** with **OpenCV morphological verification**:

1. **CLAHE Contrast Normalization**:
   Normalizes the image's luminance channel before inference so faint tears and joint lines stand out under camera glare or dim workshop lighting.
2. **Physical Texture Variance Filter (`is_genuine_defect_present`)**:
   Measures pixel standard deviation ($\sigma$) and Canny edge count inside every candidate box:
   - Smooth walls and flat shadows ($\sigma < 9.5$) have zero texture and are **immediately rejected** as false alarms.
   - Genuine flaws have high boundary contrast ($\sigma > 25$) and pass through.
3. **Contour Circularity (Isoperimetric Quotient)**:
   Extracts the defect contour inside the bounding box and computes:
   $$\text{Circularity} = \frac{4 \pi \times \text{Area}}{\text{Perimeter}^2}$$
   - **Holes** (round/oval) score **`0.45 – 0.90`**.
   - **Tears** (elongated slits) score **`0.05 – 0.35`**.
   *This mathematically prevents holes from ever being misclassified as tears.*
4. **Anti-Ghost Multi-Frame Persistence Gater (`DefectSmoother`)**:
   Tracks defects across consecutive frames. Only defects confirmed for at least **2 consecutive frames** (~0.06 seconds) are broadcast and logged, completely eliminating momentary 1-frame camera flickers.

---

## 6. Where Data Is Stored in the System

| File / Folder | Content Description | Operational Role |
| :--- | :--- | :--- |
| **`best.pt`** | Trained neural network checkpoint (~6.2 MB). | Loaded by `edge_node_vision.py` on startup. |
| **`detections.csv`** | Structured event log of all detected defects. | Node 2 writes to it; Dashboard reads and plots it. |
| **`assets/logo.jpg`** | High-res optical AI inspection brand logo. | Displayed in the dashboard top bar. |
| **`test_defects.html`** | 5 high-contrast optical SVG test target cards. | Used for camera testing and live examiner demonstrations. |
| **`latest_frame.jpg`** | Snapshot of the latest analyzed video frame. | Fallback preview when camera server initializes. |
| **`train_conveyor_yolo.ipynb`** | Google Colab Jupyter Notebook. | Prepared workflow for retraining larger models (YOLOv8s/m). |
| **`train.py`** | Local Python CLI training script. | For training on local machines with an NVIDIA GPU. |

---

## 7. Structure of the Data Records (`detections.csv`)

When a defect is verified, Node 2 records a structured entry:

```csv
Timestamp,Sender ID,Defect Type,Confidence,Bounding Box
1788628325.89,Node_1_Camera,Large Tear,0.85,"[332, 316, 560, 357]"
1788628329.49,Node_1_Camera,Small Hole,0.82,"[48, 232, 150, 253]"
```

* **`Timestamp`**: Unix epoch float (converted in the UI to human-readable `HH:MM:SS`).
* **`Sender ID`**: Identifies which camera node captured the defect (e.g. `Node_1_Camera`).
* **`Defect Type`**: One of the 5 verified classes.
* **`Confidence`**: Model certainty percentage (e.g. `0.85` = 85.0%).
* **`Bounding Box`**: Four integer pixel coordinates `[X1, Y1, X2, Y2]` indicating the exact top-left and bottom-right corners on the camera screen.

---

## 8. Presentation & Defense Script (For Exams)

When presenting this project to your teacher or examiner, use this concise, professional narrative:

### 1. The Opening Pitch (30 Seconds)
> *"Conveyor belt failure in heavy industry accounts for millions of dollars in mechanical damage and production downtime. We designed an **Autonomous Edge AI Quality Monitor** that uses computer vision to detect, classify, and track the 5 primary conveyor failure modes in real time: **Belt Joints, Large Holes, Small Holes, Large Tears, and Small Tears**."*

### 2. The Technical Architecture (1 Minute)
> *"Our project uses a **Distributed Edge Computing Architecture**:*
> * * **Node 1 (Vision Edge Engine)** runs a pre-trained YOLOv8 neural network combined with OpenCV morphological verification at 30 FPS.*
> * * When damage is confirmed, Node 1 broadcasts a lightweight JSON payload over **local UDP sockets** to **Node 2 (Defect Recorder)**, which logs the telemetry to a persistent CSV database.*
> * * Meanwhile, an **industrial operator dashboard** built in Streamlit displays live in-browser MJPEG video streams, dynamic certainty charts, and actionable triage status badges without any cloud latency."*

### 3. The Engineering Highlight (Why Our System Is Accurate)
> *"Rather than relying solely on raw neural network predictions, we engineered a **Hybrid Computer Vision Pipeline**:*
> 1. * **CLAHE** normalizes lighting to eliminate screen glare and lighting variations.*
> 2. * **Physical Variance Filters** reject flat walls and shadows.*
> 3. * **Contour Circularity Analysis (Isoperimetric Quotient)** mathematically separates round punctures (holes) from linear slits (tears).*
> 4. * **Multi-Frame Persistence Gating** requires defects to persist across multiple frames, eliminating false alarms."*
