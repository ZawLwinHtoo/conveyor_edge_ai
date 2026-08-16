import socket
import json
import time
import threading
import csv
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# ============================================================
# NETWORK CONFIGURATION
# ============================================================

MY_PORT = 5012
NEIGHBOR_PORT = 5013

LOG_FILE = "detections.csv"


# ============================================================
# SAVE DEFECT DETECTION
# ============================================================

def save_defect_log(message):

    file_exists = os.path.exists(LOG_FILE)

    with open(
        LOG_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        # Create CSV header if file is new
        if not file_exists or os.path.getsize(LOG_FILE) == 0:

            writer.writerow([
                "Timestamp",
                "Sender ID",
                "Defect Type",
                "Confidence",
                "Bounding Box"
            ])

        writer.writerow([
            message.get("timestamp"),
            message.get("sender_id"),
            message.get("defect_type"),
            message.get("confidence"),
            message.get("bounding_box")
        ])

    print("💾 Detection saved to detections.csv")


# ============================================================
# TRIGGER ALARM
# ============================================================

def trigger_alert(message):

    defect_type = message.get(
        "defect_type",
        "Unknown"
    )

    confidence = message.get(
        "confidence",
        0
    )

    print("\n" + "=" * 50)
    print("🚨 DEFECT ALERT!")
    print(f"Defect Type : {defect_type}")
    print(f"Confidence  : {confidence:.2f}")
    print("=" * 50)

    # Simulated alarm
    print("🔔 [ALARM] Warning triggered!")


# ============================================================
# LISTEN FOR NODE 1 ALERTS
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
        f"[NODE 2] Active and listening "
        f"on port {MY_PORT}..."
    )

    while True:

        data, addr = sock.recvfrom(1024)

        try:

            message = json.loads(
                data.decode("utf-8")
            )

            print(
                "\n🚨 [MESH ALERT RECEIVED BY NODE 2]"
            )

            print(message)

            # 1. Trigger alarm
            trigger_alert(message)

            # 2. Save detection
            save_defect_log(message)

        except json.JSONDecodeError:

            print(
                "⚠️ Invalid JSON data received."
            )

        except Exception as e:

            print(
                f"⚠️ Error processing alert: {e}"
            )


# ============================================================
# SEND DEFECT ALERT
# ============================================================

def send_defect_alert(
    defect_type,
    confidence
):

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    payload = {

        "sender_id":
            "Node_2_Camera",

        "timestamp":
            time.time(),

        "defect_type":
            defect_type,

        "confidence":
            confidence
    }

    sock.sendto(
        json.dumps(payload).encode("utf-8"),
        ("127.0.0.1", NEIGHBOR_PORT)
    )

    print(
        f"--> [MESH TRANSMIT] "
        f"Sent defect alert "
        f"({defect_type}) "
        f"to Port {NEIGHBOR_PORT}"
    )

    sock.close()


# ============================================================
# START NODE 2
# ============================================================

threading.Thread(
    target=listen_for_alerts,
    daemon=True
).start()


# ============================================================
# KEEP NODE 2 RUNNING
# ============================================================

while True:

    time.sleep(1)