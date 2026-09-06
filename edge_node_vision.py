import cv2  # pyrefly: ignore [missing-import]
import socket
import json
import time
import threading
import sys
import io
import os
import argparse
import numpy as np
from ultralytics import YOLO  # pyrefly: ignore [missing-import]

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

# Parse CLI arguments
parser = argparse.ArgumentParser(description="Edge AI Vision Node")
parser.add_argument("--source", type=str, default=None, help="Camera source: 0, 1, URL, or SIMULATION")
parser.add_argument("--target", type=str, default="ALL", help="Target defect: ALL or specific defect name (e.g., 'Large Hole')")
parser.add_argument("--conf", type=float, default=0.20, help="Confidence threshold (default: 0.20)")
parser.add_argument("--augment", action="store_true", help="Enable Test-Time Augmentation (TTA) for enhanced sensitivity")
args = parser.parse_known_args()[0]

CONF_THRESHOLD = float(args.conf) if args.conf is not None else 0.20
USE_AUGMENT = bool(args.augment)


# ============================================================
# CAMERA & NETWORK CONFIGURATION
# ============================================================

# Set CAMERA_SOURCE = 0 for built-in/USB webcam
# Or set CAMERA_SOURCE = "http://<PHONE_IP>:8080/video" for Smartphone IP Camera
CAMERA_SOURCE = 0

MY_PORT = 5013
NEIGHBOR_PORT = 5012

LABEL_MAP = {
    "Lubang Besar": "Large Hole",
    "Lubang Kecil": "Small Hole",
    "Sambungan Belt": "Belt Joint",
    "Sobekan Besar": "Large Tear",
    "Sobekan Kecil": "Small Tear"
}

ALL_DEFECT_TYPES = [
    "Large Hole",
    "Small Hole",
    "Belt Joint",
    "Large Tear",
    "Small Tear"
]

TARGET_OBJECT = args.target.strip() if args.target else "ALL"
TARGET_OBJECT = LABEL_MAP.get(TARGET_OBJECT, TARGET_OBJECT)

ALERT_COOLDOWN = 1.0


# ============================================================
# LIVE MJPEG VIDEO STREAM SERVER (PORT 5014)
# ============================================================

from http.server import HTTPServer, BaseHTTPRequestHandler

STREAM_PORT = 5014
latest_jpeg_frame = None
frame_lock = threading.Lock()

class MJPEGStreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/video_feed":
            self.send_response(200)
            self.send_header("Content-type", "multipart/x-mixed-replace; boundary=frame")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache, private")
            self.end_headers()
            while True:
                with frame_lock:
                    data = latest_jpeg_frame
                if data is not None:
                    try:
                        self.wfile.write(b"--frame\r\n")
                        self.wfile.write(b"Content-Type: image/jpeg\r\n\r\n")
                        self.wfile.write(data)
                        self.wfile.write(b"\r\n")
                    except Exception:
                        break
                time.sleep(0.035)  # ~28 FPS
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b'{"status":"active"}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def run_mjpeg_server():
    try:
        server = HTTPServer(("0.0.0.0", STREAM_PORT), MJPEGStreamHandler)
        server.serve_forever()
    except Exception as e:
        print(f"[STREAM] Video server notice: {e}")

mjpeg_thread = threading.Thread(target=run_mjpeg_server, daemon=True)
mjpeg_thread.start()
print(f"[NODE 1 STREAM] Live camera MJPEG streaming ready on port {STREAM_PORT}")


# ============================================================
# NODE 1 MESH LISTENER
# ============================================================

def listen_for_alerts():

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    sock.bind(
        ("127.0.0.1", MY_PORT)
    )

    print(
        f"[NODE 1 MESH] Active and listening "
        f"on port {MY_PORT}..."
    )

    while True:

        data, addr = sock.recvfrom(1024)

        try:

            message = json.loads(
                data.decode("utf-8")
            )

            print(
                f"\n[MESH ALERT] Received by Node 1: "
                f"{message}"
            )

        except json.JSONDecodeError:

            print(
                "[WARN] Invalid JSON received."
            )

        except Exception as e:

            print(
                f"[ERROR] Mesh listener error: {e}"
            )


# ============================================================
# SEND DEFECT ALERT TO NODE 2
# ============================================================

def broadcast_defect_alert(
    defect_name,
    confidence,
    bbox
):

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    payload = {

        "sender_id":
            "Node_1_Camera",

        "timestamp":
            time.time(),

        "defect_type":
            defect_name,

        "confidence":
            round(float(confidence), 2),

        "bounding_box":
            [int(x) for x in bbox]
    }

    sock.sendto(
        json.dumps(payload).encode("utf-8"),
        ("127.0.0.1", NEIGHBOR_PORT)
    )

    print(
        f"--> [MESH TRANSMIT] "
        f"Sent defect alert "
        f"({defect_name}) "
        f"to Port {NEIGHBOR_PORT}"
    )

    sock.close()


# ============================================================
# START NODE 1 MESH LISTENER
# ============================================================

threading.Thread(
    target=listen_for_alerts,
    daemon=True
).start()


# ============================================================
# INTERACTIVE CAMERA SELECTION
# ============================================================

def open_droidcam_stream(source_val):
    # 1. If source_val is IP or URL (e.g. 192.168.1.15:4747 or http://...)
    if isinstance(source_val, str) and (source_val.startswith("http") or ":" in source_val):
        url = source_val.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        if not url.endswith("/video") and not url.endswith("/mjpeg"):
            url = url.rstrip("/") + "/video"
        print(f"[NODE 1 CV] Connecting to DroidCam Wi-Fi stream: {url}")
        cap = cv2.VideoCapture(url)
        if cap.isOpened():
            return cap, url

    # 2. Prefer Camera Index 2 (where DroidCam Video resides on Windows when Camo is also installed)
    print("[NODE 1 CV] Connecting to DroidCam Video device on PC...")
    for idx in [2, 1, 3]:
        temp_cap = cv2.VideoCapture(idx)
        if temp_cap.isOpened():
            ret, frame = temp_cap.read()
            # Ignore Camo standby grey logo (shape 720x1280 with mean ~133)
            is_camo_standby = (frame is not None and frame.shape[0] == 720 and frame.shape[1] == 1280 and 125 < frame.mean() < 145)
            if ret and not is_camo_standby:
                print(f"[NODE 1 CV] Connected to DroidCam camera at Index {idx}!")
                return temp_cap, idx
            temp_cap.release()

    # Fallback
    for idx in [2, 1]:
        temp_cap = cv2.VideoCapture(idx)
        if temp_cap.isOpened():
            print(f"[NODE 1 CV] Connected to camera Index {idx}")
            return temp_cap, idx

    return cv2.VideoCapture(2), 2


def select_camera_device():
    print("\n" + "=" * 55)
    print("SELECT CAMERA SOURCE:")
    print("=" * 55)
    print("  [1] Local Laptop Camera")
    print("  [2] DroidCam (Phone Camera)")
    print("=" * 55)

    try:
        choice = input("Enter choice (1-2) [Default: 1]: ").strip()
    except Exception:
        choice = "1"

    if choice == "2":
        print("\n[DroidCam Connection Method]")
        print("  [1] USB / DroidCam PC Client (Auto)")
        print("  [2] Wi-Fi IP (e.g. 192.168.1.15:4747)")
        try:
            sub = input("Enter choice (1-2) [Default: 1]: ").strip()
        except Exception:
            sub = "1"
        if sub == "2":
            try:
                ip = input("Enter Phone IP from DroidCam app: ").strip()
            except Exception:
                ip = ""
            return ip if ip else "DROIDCAM"
        return "DROIDCAM"
    else:
        return 0


# ============================================================
# COMPUTER VISION INITIALIZATION
# ============================================================

print("[NODE 1 CV] Loading YOLO model...")

model = YOLO("best.pt")
# Translate YOLO model class names to English so visual bounding boxes display in English
if hasattr(model, "model") and hasattr(model.model, "names"):
    model.model.names = {k: LABEL_MAP.get(v, v) for k, v in model.model.names.items()}

if args.source is not None:
    raw_src = args.source.strip()
    if raw_src.isdigit():
        selected_source = int(raw_src)
    elif raw_src.upper() == "SIMULATION":
        selected_source = "SIMULATION"
    else:
        selected_source = raw_src
else:
    selected_source = select_camera_device()

if selected_source == "SIMULATION":
    cap = cv2.VideoCapture()
    use_simulation = True
elif selected_source == "DROIDCAM" or (isinstance(selected_source, str) and (selected_source.startswith("http") or ":" in selected_source or selected_source == "1") and selected_source != "0"):
    cap, actual_src = open_droidcam_stream(selected_source)
    use_simulation = not cap.isOpened()
    selected_source = f"DroidCam ({actual_src})"
else:
    src_idx = int(selected_source) if str(selected_source).isdigit() else 0
    if sys.platform == "win32":
        cap = cv2.VideoCapture(src_idx, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(src_idx)
    else:
        cap = cv2.VideoCapture(src_idx)
    use_simulation = not cap.isOpened()
    selected_source = f"Laptop Camera ({src_idx})"

if use_simulation:
    print("[WARN] Physical camera not opened. Switching to Simulation Mode...")
    print("[NODE 1 CV] Starting Simulated Vision Engine.")
else:
    print(f"[NODE 1 CV] Starting Real Vision Engine on source: {selected_source}")


# ============================================================
# GEOMETRIC DEFECT DISAMBIGUATION & REFINEMENT
# ============================================================

BOX_COLORS = {
    "Large Hole": (68, 63, 244),     # Red
    "Small Hole": (11, 158, 245),    # Amber
    "Large Tear": (22, 115, 249),    # Orange
    "Small Tear": (247, 85, 168),    # Purple
    "Belt Joint": (233, 165, 14),    # Sky Blue
}

def refine_defect_prediction(raw_label, confidence, bbox, frame_w, frame_h):
    """
    Refines defect classification using geometric spatial metrics (aspect ratio, area, scale)
    to correct model confusion between holes, tears, and belt joints.
    """
    x1, y1, x2, y2 = [int(v) for v in bbox[:4]]
    w = max(1, abs(x2 - x1))
    h = max(1, abs(y2 - y1))
    area = w * h
    aspect_ratio = w / float(h)
    max_dim = max(w, h)
    rel_width = w / float(frame_w) if frame_w > 0 else 0

    # Normalization: standard label
    label = LABEL_MAP.get(raw_label, raw_label)

    # 1. Belt Joint Detection:
    # A belt joint typically spans horizontally across a significant width (aspect_ratio >= 2.5 or rel_width >= 0.30)
    if label in ["Sambungan Belt", "Belt Joint"] or (aspect_ratio >= 2.8 and rel_width >= 0.30):
        return "Belt Joint", confidence, [x1, y1, x2, y2]

    # 2. Tear Detection:
    # Tears are elongated slits (aspect ratio >= 1.75 or aspect ratio <= 0.57)
    is_elongated = (aspect_ratio >= 1.75 or aspect_ratio <= 0.57)

    if is_elongated:
        if area >= 3800 or max_dim >= 110:
            refined_label = "Large Tear"
        else:
            refined_label = "Small Tear"
        return refined_label, confidence, [x1, y1, x2, y2]

    # 3. Hole Detection:
    # Holes are compact / circular (0.57 < aspect ratio < 1.75)
    if label in ["Sobekan Besar", "Large Tear", "Sobekan Kecil", "Small Tear"]:
        if not is_elongated:
            refined_label = "Large Hole" if (area >= 3800 or max_dim >= 100) else "Small Hole"
            return refined_label, confidence, [x1, y1, x2, y2]

    # 4. Hole size disambiguation based on area
    if label in ["Lubang Besar", "Large Hole", "Lubang Kecil", "Small Hole"]:
        if area >= 3800 or max_dim >= 100:
            return "Large Hole", confidence, [x1, y1, x2, y2]
        else:
            return "Small Hole", confidence, [x1, y1, x2, y2]

    return label, confidence, [x1, y1, x2, y2]


# ============================================================
# ALERT CONTROL
# ============================================================

last_alert_times = {}
last_alert_time = 0
frame_count = 0
sim_index = 0
current_sim_defect = None


# ============================================================
# MAIN COMPUTER VISION LOOP
# ============================================================

cv2.namedWindow("Node 1 - Edge AI Camera Feed", cv2.WINDOW_NORMAL)

while True:
    frame_count += 1

    if not use_simulation:
        ret, frame = cap.read()

        if not ret:
            print("[WARN] Unable to read camera frame. Switching to simulation mode...")
            use_simulation = True
            cap.release()
            continue

        # If camera frame is black (e.g. Camo/DroidCam virtual camera on standby)
        if frame is not None and frame.mean() < 1.0:
            cv2.putText(
                frame,
                "Waiting for Phone Camera Stream...",
                (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 165, 255),
                2
            )
            cv2.putText(
                frame,
                "Please connect your phone in Camo Studio or DroidCam",
                (30, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (200, 200, 200),
                1
            )
            annotated_frame = frame
        else:
            # Query model with slight headroom so lower-confidence tears & belt joints are captured
            effective_conf = min(CONF_THRESHOLD, 0.16)
            results = model(
                frame,
                conf=effective_conf,
                iou=0.40,
                imgsz=640,
                augment=USE_AUGMENT,
                verbose=False
            )

            annotated_frame = frame.copy()

            for result in results[0].boxes:
                cls_id = int(result.cls[0])
                raw_label = model.names[cls_id]
                confidence = float(result.conf[0])
                raw_bbox = result.xyxy[0].tolist()

                # Apply geometric refinement
                refined_label, confidence, bbox = refine_defect_prediction(
                    raw_label,
                    confidence,
                    raw_bbox,
                    frame.shape[1],
                    frame.shape[0]
                )

                # Class-specific threshold: tears and belt joints accept >= 0.18, holes use CONF_THRESHOLD
                required_conf = 0.18 if "Tear" in refined_label or "Joint" in refined_label else CONF_THRESHOLD
                if confidence < required_conf:
                    continue

                # Match target defect filter (ALL detects any defect class)
                is_target = (
                    TARGET_OBJECT.upper() == "ALL" or
                    refined_label.strip().lower() == TARGET_OBJECT.strip().lower()
                )

                if is_target:
                    # Draw neat custom bounding box
                    x1, y1, x2, y2 = bbox
                    color = BOX_COLORS.get(refined_label, (0, 255, 0))
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)

                    # Label background pill
                    label_text = f"{refined_label} {int(confidence * 100)}%"
                    (tw, th), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    py1 = max(0, y1 - th - 8)
                    cv2.rectangle(annotated_frame, (x1, py1), (x1 + tw + 8, y1), color, -1)
                    cv2.putText(annotated_frame, label_text, (x1 + 4, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

                    current_time = time.time()
                    if current_time - last_alert_times.get(refined_label, 0) >= ALERT_COOLDOWN:
                        broadcast_defect_alert(refined_label, confidence, bbox)
                        last_alert_times[refined_label] = current_time

    else:
        # Generate synthetic conveyor belt frame (640x480)
        frame_count += 1
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:] = (50, 50, 50)  # Conveyor belt dark gray background

        # Draw moving conveyor grid lines
        offset = (frame_count * 8) % 40
        for y in range(offset, 480, 40):
            cv2.line(frame, (0, y), (640, y), (80, 80, 80), 2)

        # Draw status overlay
        cv2.putText(
            frame,
            "Node 1 - Conveyor Belt Simulation (No Camera Detected)",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )

        current_time = time.time()
        # Simulate a defect every 5 seconds
        if current_time - last_alert_time >= 5.0:
            if TARGET_OBJECT.upper() == "ALL":
                active_defect = ALL_DEFECT_TYPES[sim_index % len(ALL_DEFECT_TYPES)]
                sim_index += 1
            else:
                active_defect = TARGET_OBJECT

            simulated_conf = round(0.82 + (frame_count % 15) * 0.01, 2)
            # Dynamic bounding boxes for visual variety
            box_x = 180 + (sim_index * 25) % 150
            box_y = 130 + (sim_index * 20) % 100
            simulated_bbox = [box_x, box_y, box_x + 220, box_y + 160]
            broadcast_defect_alert(active_defect, simulated_conf, simulated_bbox)
            current_sim_defect = active_defect
            last_alert_time = current_time

        # Draw simulated defect visual on frame if within alert display window
        if current_time - last_alert_time < 2.5 and current_sim_defect:
            box_x = 180 + (sim_index * 25) % 150
            box_y = 130 + (sim_index * 20) % 100
            cv2.rectangle(frame, (box_x, box_y), (box_x + 220, box_y + 160), (0, 0, 255), 3)
            cv2.putText(
                frame,
                f"DEFECT DETECTED: {current_sim_defect}",
                (box_x, max(30, box_y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2
            )

        annotated_frame = frame

    # Display on-screen instructions & live HUD
    tta_status = "ON" if USE_AUGMENT else "OFF"
    hud_text = f"Confidence: {int(CONF_THRESHOLD * 100)}% [+/-] | Deep Scan: {tta_status} [T] | [C] Photo | [Q] Exit"
    cv2.putText(
        annotated_frame,
        hud_text,
        (15, annotated_frame.shape[0] - 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (0, 255, 0) if not USE_AUGMENT else (0, 255, 255),
        1
    )

    # Update live web stream buffer and snapshot file
    try:
        ret_enc, enc_buf = cv2.imencode(".jpg", annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if ret_enc:
            with frame_lock:
                latest_jpeg_frame = enc_buf.tobytes()
            with open("latest_frame.jpg", "wb") as f:
                f.write(latest_jpeg_frame)
    except Exception:
        pass

    cv2.imshow(
        "Node 1 - Edge AI Camera Feed",
        annotated_frame
    )

    key = cv2.waitKey(30) & 0xFF
    window_closed = False
    if frame_count > 10:
        try:
            if cv2.getWindowProperty("Node 1 - Edge AI Camera Feed", cv2.WND_PROP_VISIBLE) < 1:
                window_closed = True
        except Exception:
            pass

    if key == ord("q") or window_closed:
        break
    elif key == ord("c") or key == ord("C"):
        os.makedirs("dataset/raw_images", exist_ok=True)
        img_filename = f"dataset/raw_images/capture_{int(time.time())}.jpg"
        cv2.imwrite(img_filename, frame)
        print(f"\n[CAPTURE] Saved training frame to: {img_filename}")
    elif key in (ord("+"), ord("=")):
        CONF_THRESHOLD = min(0.95, round(CONF_THRESHOLD + 0.05, 2))
        print(f"[SENSITIVITY] Increased confidence threshold to {int(CONF_THRESHOLD * 100)}%")
    elif key in (ord("-"), ord("_")):
        CONF_THRESHOLD = max(0.10, round(CONF_THRESHOLD - 0.05, 2))
        print(f"[SENSITIVITY] Decreased confidence threshold to {int(CONF_THRESHOLD * 100)}% (Catch subtle defects)")
    elif key in (ord("t"), ord("T")):
        USE_AUGMENT = not USE_AUGMENT
        print(f"[TTA BOOST] Test-Time Augmentation set to: {'ON' if USE_AUGMENT else 'OFF'}")




# ============================================================
# CLEANUP
# ============================================================

if cap.isOpened():
    cap.release()

cv2.destroyAllWindows()

print("[NODE 1 CV] Vision Engine stopped.")