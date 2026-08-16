import cv2
import socket
import json
import time
import threading
import sys
import io
import argparse
import numpy as np
from ultralytics import YOLO

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Parse CLI arguments
parser = argparse.ArgumentParser(description="Edge AI Vision Node")
parser.add_argument("--source", type=str, default=None, help="Camera source: 0, 1, URL, or SIMULATION")
args = parser.parse_known_args()[0]


# ============================================================
# ============================================================
# CAMERA & NETWORK CONFIGURATION
# ============================================================

# Set CAMERA_SOURCE = 0 for built-in/USB webcam
# Or set CAMERA_SOURCE = "http://<PHONE_IP>:8080/video" for Smartphone IP Camera
CAMERA_SOURCE = 0

MY_PORT = 5013
NEIGHBOR_PORT = 5012

TARGET_OBJECT = "Lubang Besar"

ALERT_COOLDOWN = 3.0


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
                f"\n🚨 [MESH ALERT RECEIVED BY NODE 1]: "
                f"{message}"
            )

        except json.JSONDecodeError:

            print(
                "⚠️ Invalid JSON received."
            )

        except Exception as e:

            print(
                f"⚠️ Mesh listener error: {e}"
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

def select_camera_device():
    print("\n" + "=" * 55)
    print("📷 SELECT CAMERA DEVICE FOR EDGE AI DETECTION:")
    print("=" * 55)
    print("  [1] PC / Laptop Built-in Webcam (Index 0)")
    print("  [2] iPhone / DroidCam / External USB Phone Camera (Index 1)")
    print("  [3] Smartphone IP Camera Stream (HTTP URL)")
    print("  [4] Conveyor Belt Simulation Mode")
    print("=" * 55)

    try:
        choice = input("Enter choice (1-4) [Default: 1]: ").strip()
    except Exception:
        choice = "1"

    if choice == "2":
        print("\n--> Selected: iPhone / DroidCam / USB Phone Camera (Index 1)")
        return 1
    elif choice == "3":
        try:
            url = input("Enter Phone IP Stream URL (e.g. http://192.168.1.15:8080/video): ").strip()
        except Exception:
            url = ""
        print(f"\n--> Selected IP Stream: {url}")
        return url if url else 0
    elif choice == "4":
        print("\n--> Selected: Conveyor Belt Simulation Mode")
        return "SIMULATION"
    else:
        print("\n--> Selected: PC / Laptop Built-in Webcam (Index 0)")
        return 0


# ============================================================
# COMPUTER VISION INITIALIZATION
# ============================================================

print("[NODE 1 CV] Loading YOLO model...")

model = YOLO("best.pt")

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
else:
    cap = cv2.VideoCapture(selected_source)
    use_simulation = not cap.isOpened()

if use_simulation:
    print("⚠️ Physical camera not opened. Switching to Mock / Simulation Mode...")
    print("[NODE 1 CV] Starting Simulated Vision Engine.")
else:
    print(f"[NODE 1 CV] Starting Real Vision Engine on source: {selected_source}")


# ============================================================
# ALERT CONTROL
# ============================================================

last_alert_time = 0
frame_count = 0


# ============================================================
# MAIN COMPUTER VISION LOOP
# ============================================================

while True:

    if not use_simulation:
        ret, frame = cap.read()

        if not ret:
            print("⚠️ Unable to read camera frame. Switching to simulation mode...")
            use_simulation = True
            cap.release()
            continue

        results = model(
            frame,
            conf=0.50,
            verbose=False
        )

        annotated_frame = results[0].plot()

        for result in results[0].boxes:
            cls_id = int(result.cls[0])
            label = model.names[cls_id]
            confidence = float(result.conf[0])
            bbox = result.xyxy[0].tolist()

            if label == TARGET_OBJECT and confidence >= 0.50:
                current_time = time.time()
                if current_time - last_alert_time >= ALERT_COOLDOWN:
                    broadcast_defect_alert(label, confidence, bbox)
                    last_alert_time = current_time

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
            simulated_conf = 0.85 + (frame_count % 10) * 0.01
            simulated_bbox = [200, 150, 440, 330]
            broadcast_defect_alert(TARGET_OBJECT, simulated_conf, simulated_bbox)
            last_alert_time = current_time

        # Draw simulated defect visual on frame if within alert display window
        if current_time - last_alert_time < 2.0:
            cv2.rectangle(frame, (200, 150), (440, 330), (0, 0, 255), 3)
            cv2.putText(
                frame,
                f"DEFECT DETECTED: {TARGET_OBJECT}",
                (200, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2
            )

        annotated_frame = frame

    cv2.imshow(
        "Node 1 - Edge AI Camera Feed",
        annotated_frame
    )

    key = cv2.waitKey(30) & 0xFF
    if key == ord("q") or cv2.getWindowProperty("Node 1 - Edge AI Camera Feed", cv2.WND_PROP_VISIBLE) < 1:
        break


# ============================================================
# CLEANUP
# ============================================================

if cap.isOpened():
    cap.release()

cv2.destroyAllWindows()

print("[NODE 1 CV] Vision Engine stopped.")