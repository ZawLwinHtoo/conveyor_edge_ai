from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event, Thread
import csv
import json
import socket
import time
import unittest
from node2 import listen_for_alerts, save_defect_log, validate_message


class TelemetryTests(unittest.TestCase):
    def message(self):
        return {"sender_id":"Test node", "timestamp":time.time(), "defect_type":"Small Hole", "confidence":.8, "bounding_box":[1,2,20,30]}

    def test_real_udp_packets_are_logged_once_with_a_single_header(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/"detections.csv"
            sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            sock.bind(("127.0.0.1",0))
            destination=sock.getsockname()
            stop=Event()
            worker=Thread(target=listen_for_alerts,kwargs={"sock":sock,"log_file":path,"stop_event":stop})
            worker.start()
            try:
                with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sender:
                    for payload in [b"not-json", json.dumps(self.message()).encode(), json.dumps({**self.message(),"simulation":True}).encode()]:
                        sender.sendto(payload,destination)
                deadline=time.monotonic()+3
                while time.monotonic()<deadline:
                    if path.exists() and len(path.read_text().splitlines())>=3: break
                    time.sleep(.05)
            finally:
                stop.set(); worker.join(timeout=3)
            self.assertFalse(worker.is_alive())
            with path.open(newline="") as file: rows=list(csv.DictReader(file))
            self.assertEqual(len(rows),2)
            self.assertEqual(rows[1]["Sender ID"],"SIMULATION")

    def test_bad_values_are_rejected_before_writing(self):
        for update in [{"confidence":float("nan")},{"confidence":2},{"bounding_box":[20,2,1,30]},{"defect_type":None}]:
            with self.assertRaises(ValueError): validate_message({**self.message(),**update})


if __name__ == "__main__":
    unittest.main()
