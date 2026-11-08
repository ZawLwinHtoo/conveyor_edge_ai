"""Local UDP receiver and validated CSV telemetry logger."""
from pathlib import Path
import argparse
import csv
import json
import math
import socket
import threading
import time

ROOT = Path(__file__).resolve().parent
MY_PORT, NEIGHBOR_PORT = 5012, 5013
LOG_FILE = ROOT / "detections.csv"
FIELDS = ["Timestamp", "Sender ID", "Defect Type", "Confidence", "Bounding Box"]


def validate_message(message):
    if not isinstance(message, dict):
        raise ValueError("Expected an object")
    result = dict(message)
    for key in ("timestamp", "confidence"):
        value = result.get(key)
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(f"Invalid {key}")
    if not 0 <= result["confidence"] <= 1:
        raise ValueError("Confidence must be between zero and one")
    for key in ("sender_id", "defect_type"):
        if not isinstance(result.get(key), str) or not 1 <= len(result[key]) <= 80:
            raise ValueError(f"Invalid {key}")
    box = result.get("bounding_box", [])
    if not isinstance(box, list) or len(box) not in (0, 4) or any(type(value) is not int or value < 0 for value in box):
        raise ValueError("Invalid bounding box")
    if len(box) == 4 and (box[2] < box[0] or box[3] < box[1]):
        raise ValueError("Invalid bounding box order")
    result["bounding_box"] = box
    if result.get("simulation") is True:
        result["sender_id"] = "SIMULATION"
    return result


def save_defect_log(message, log_file=LOG_FILE):
    message = validate_message(message)
    path = Path(log_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if needs_header:
            writer.writerow(FIELDS)
        writer.writerow([message["timestamp"], message["sender_id"], message["defect_type"], message["confidence"], message["bounding_box"]])


def listen_for_alerts(port=MY_PORT, log_file=LOG_FILE, stop_event=None, sock=None):
    stop_event = stop_event or threading.Event()
    supplied_socket = sock is not None
    sock = sock or socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Windows cannot query getsockname() before a UDP socket is bound.
        if not supplied_socket:
            sock.bind(("127.0.0.1", port))
        sock.settimeout(.2)
        print(f"[NODE 2] Listening on {sock.getsockname()[1]}; logging to {log_file}", flush=True)
        while not stop_event.is_set():
            try:
                payload, _ = sock.recvfrom(65535)
                message = validate_message(json.loads(payload.decode("utf-8")))
                save_defect_log(message, log_file)
                print(f"[LOG] {message['sender_id']}: {message['defect_type']} ({message['confidence']:.2f})", flush=True)
            except socket.timeout:
                continue
            except (ValueError, UnicodeError) as error:
                print(f"[WARN] Ignored malformed telemetry: {error}", flush=True)
    finally:
        sock.close()


def send_defect_alert(defect_type, confidence):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(json.dumps({"sender_id": "Node_2_Camera", "timestamp": time.time(), "defect_type": defect_type, "confidence": confidence}).encode(), ("127.0.0.1", NEIGHBOR_PORT))


def main():
    parser = argparse.ArgumentParser(description="Receive local conveyor defect telemetry")
    parser.add_argument("--port", type=int, default=MY_PORT)
    parser.add_argument("--log-file", type=Path, default=LOG_FILE)
    args = parser.parse_args()
    try:
        listen_for_alerts(args.port, args.log_file)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
