# Conveyor Edge AI

A local camera inspection demo: YOLO detection -> UDP telemetry -> CSV -> Streamlit dashboard. The bundled `best.pt` loads locally. Hardware accuracy and industrial reliability have not been established.

## Run

Use Python 3.11–3.13. From this directory:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m streamlit run dashboard.py
```

On macOS/Linux use `.venv/bin/python`. Windows users can also run `run_dashboard.bat`. Select a camera in the dashboard and start detection. A missing camera stops detection with an error. Select **SIMULATION** explicitly for a hardware-free demonstration; these events are labelled `SIMULATION` in telemetry and CSV.

The dashboard manages only the child processes it starts. UDP receiver defaults to loopback port 5012; video/health endpoints use loopback port 8081. Stop the dashboard's services before starting standalone processes on the same ports.

## Standalone pipeline

```sh
python node2.py
python edge_node_vision.py --source SIMULATION --headless --max-frames 100
```

Run the commands in separate terminals. Paths are resolved relative to the project, including when launched from another working directory. Logs are appended to `detections.csv`. Simulation events are synthetic and do not measure model accuracy. A real camera requires OS permissions and a valid camera index. UDP delivery has no persistence or delivery guarantee; this is a single-machine portfolio demo.

## Checks

```sh
python -m unittest discover -s tests -v
```

Checks exercise real UDP reception, malformed payload rejection and CSV output. A recovery smoke run additionally loaded the bundled model, streamed 100 headless frames, kept the health endpoint responsive during streaming, and logged simulated alerts.
