import streamlit as st  # pyrefly: ignore [missing-import]
import pandas as pd
import os
import textwrap
import subprocess
import sys
import altair as alt
import ast

PYTHON_EXE = sys.executable

LABEL_MAP = {
    "Lubang Besar": "Large Hole",
    "Lubang Kecil": "Small Hole",
    "Sambungan Belt": "Belt Joint",
    "Sobekan Besar": "Large Tear",
    "Sobekan Kecil": "Small Tear"
}

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Conveyor Belt Quality Monitor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# MODERN, NEAT, HIGH-END INDUSTRIAL STYLING
# ============================================================

st.markdown(
    textwrap.dedent("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --canvas-bg: #0f172a;
        --card-bg: #1e293b;
        --card-border: #334155;
        --card-header-bg: #1e293b;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --accent-blue: #3b82f6;
        --accent-blue-hover: #2563eb;
        --danger-red: #ef4444;
        --danger-red-hover: #dc2626;
        --font-mono: 'JetBrains Mono', monospace;
    }

    /* Global Canvas (Normal Clean Dark Slate) */
    html, body, .stApp, [data-testid="stApp"], [data-testid="stAppViewContainer"],
    .main, section.main, [data-testid="stMain"], [data-testid="stHeader"] {
        background-color: var(--canvas-bg) !important;
        background: var(--canvas-bg) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        background-color: #111827 !important;
        background: #111827 !important;
        border-right: 1px solid #1f2937 !important;
    }

    /* COMPLETE ELIMINATION OF ALL DIMMING, FADING, AND OPACITY SHIFTS */
    [data-st-loading="true"],
    [data-st-loading="true"] *,
    [data-testid="stFragment"],
    [data-testid="stFragment"] *,
    [data-testid="stElementContainer"],
    [data-testid="stAppViewContainer"] [data-st-loading="true"],
    div[data-testid="stVerticalBlock"] > div,
    .stApp [data-st-loading="true"] {
        opacity: 1 !important;
        transition: none !important;
        animation: none !important;
        filter: none !important;
    }

    [data-testid="stAppViewContainer"] * {
        transition: opacity 0s !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    #MainMenu, footer {
        visibility: hidden !important;
    }

    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1650px !important;
    }

    /* Sidebar Clean Styling */
    [data-testid="stSidebar"] {
        background-color: #0e1422 !important;
        border-right: 1px solid var(--card-border) !important;
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
    }

    .sidebar-section-title {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        margin: 18px 0 10px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid #1c263b;
    }

    /* Top Brand & Status Bar */
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 8px;
        padding: 14px 22px;
        margin-bottom: 20px;
    }

    .brand-section {
        display: flex;
        align-items: center;
        gap: 14px;
    }

    .brand-badge {
        width: 38px;
        height: 38px;
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #38bdf8;
    }

    .brand-headings h1 {
        font-size: 18px;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.02em;
        margin: 0;
        line-height: 1.2;
    }

    .brand-headings p {
        font-size: 12px;
        color: var(--text-secondary);
        margin: 2px 0 0 0;
    }

    .status-badges {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
        background: #162033;
        border: 1px solid #223049;
        color: var(--text-secondary);
    }

    .status-pill b {
        color: var(--text-primary);
    }

    .led-circle {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
    }

    .led-online {
        background: #10b981;
        box-shadow: 0 0 8px rgba(16, 185, 129, 0.4);
    }

    .led-offline {
        background: #64748b;
    }

    /* KPI Stat Cards */
    .metric-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 8px;
        padding: 16px 20px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .metric-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-muted);
        margin-bottom: 6px;
    }

    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.03em;
        font-variant-numeric: tabular-nums;
        line-height: 1.1;
    }

    .metric-footer {
        font-size: 12px;
        color: var(--text-secondary);
        margin-top: 8px;
    }

    /* Content Cards */
    .content-box {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 20px;
    }

    .content-box-header {
        background: var(--card-header-bg);
        border-bottom: 1px solid var(--card-border);
        padding: 12px 18px;
        font-size: 13px;
        font-weight: 600;
        color: var(--text-primary);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .content-box-body {
        padding: 18px 20px;
    }

    /* Category Distribution Rows */
    .dist-row {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
        gap: 14px;
        font-size: 13px;
    }

    .dist-label {
        width: 90px;
        font-weight: 500;
        color: var(--text-secondary);
        white-space: nowrap;
    }

    .dist-track {
        flex: 1;
        height: 8px;
        background: #1e293b;
        border-radius: 4px;
        overflow: hidden;
    }

    .dist-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.3s ease;
    }

    .dist-numbers {
        width: 85px;
        text-align: right;
        font-family: var(--font-mono);
        font-size: 12px;
        font-weight: 600;
        color: var(--text-primary);
    }

    /* Clean Modern Table - Full Width Fixed Distribution */
    .neat-table-wrap {
        width: 100%;
        overflow-x: auto;
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 8px;
    }

    .neat-table {
        width: 100%;
        table-layout: fixed;
        border-collapse: collapse;
        font-size: 13px;
        text-align: left;
    }

    .neat-table th {
        background: var(--card-header-bg);
        color: var(--text-secondary);
        font-weight: 600;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 12px 16px;
        border-bottom: 1px solid var(--card-border);
        white-space: nowrap;
    }

    .neat-table td {
        padding: 12px 16px;
        border-bottom: 1px solid #1a2233;
        color: var(--text-primary);
        vertical-align: middle;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .neat-table tr:last-child td {
        border-bottom: none;
    }

    .neat-table tr:hover td {
        background: #162033;
    }

    .font-mono {
        font-family: var(--font-mono);
        font-size: 12px;
        color: #cbd5e1;
    }

    /* Badges */
    .defect-badge {
        font-family: var(--font-mono);
        font-size: 11px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 4px;
        display: inline-block;
        white-space: nowrap;
    }

    .defect-red { background: rgba(244, 63, 94, 0.15); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3); }
    .defect-amber { background: rgba(245, 158, 11, 0.15); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.3); }
    .defect-orange { background: rgba(249, 115, 22, 0.15); color: #fdba74; border: 1px solid rgba(249, 115, 22, 0.3); }
    .defect-purple { background: rgba(168, 85, 247, 0.15); color: #d8b4fe; border: 1px solid rgba(168, 85, 247, 0.3); }
    .defect-sky { background: rgba(14, 165, 233, 0.15); color: #7dd3fc; border: 1px solid rgba(14, 165, 233, 0.3); }

    /* Action Status Tags */
    .status-tag {
        font-family: var(--font-mono);
        font-size: 11px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 4px;
        display: inline-block;
        white-space: nowrap;
    }
    .tag-critical { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .tag-warning { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .tag-info { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
    .tag-neutral { background: rgba(100, 116, 139, 0.15); color: #94a3b8; border: 1px solid rgba(100, 116, 139, 0.3); }

    /* Button Polish */
    div[data-testid="stButton"] button {
        border-radius: 6px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        min-height: 40px !important;
        transition: all 0.15s ease !important;
    }

    button[key="btn_start_cam"] {
        background: #2563eb !important;
        border: 1px solid #3b82f6 !important;
        color: #ffffff !important;
    }
    button[key="btn_start_cam"]:hover {
        background: #1d4ed8 !important;
    }

    button[key="btn_stop_cam"] {
        background: #dc2626 !important;
        border: 1px solid #ef4444 !important;
        color: #ffffff !important;
    }
    button[key="btn_stop_cam"]:hover {
        background: #b91c1c !important;
    }
    </style>
    """),
    unsafe_allow_html=True
)

# ============================================================
# PROCESS MANAGEMENT & UTILITIES
# ============================================================

DATA_FILE = "detections.csv"
ROWS_PER_PAGE = 10

def is_proc_active(proc):
    return proc is not None and proc.poll() is None

def kill_proc_tree(proc):
    if proc is not None:
        try:
            pid = proc.pid
            if sys.platform == "win32":
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                proc.kill()
        except Exception:
            pass

import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return False
        except OSError:
            return True

import psutil

def is_node2_active():
    if is_proc_active(st.session_state.get("node2_proc")):
        return True
    return is_port_in_use(5012)

def is_vision_active():
    if is_proc_active(st.session_state.get("vision_proc")):
        return True
    try:
        for p in psutil.process_iter(["name", "cmdline"]):
            try:
                if "python" in (p.info.get("name") or "").lower():
                    cmdline = " ".join(p.info.get("cmdline") or []).lower()
                    if "edge_node_vision.py" in cmdline:
                        return True
            except Exception:
                continue
    except Exception:
        pass
    return False

def start_node2():
    if not is_node2_active():
        flags = subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        st.session_state.node2_proc = subprocess.Popen(
            [PYTHON_EXE, "node2.py"],
            cwd=os.getcwd(),
            creationflags=flags
        )

def stop_node2():
    if is_proc_active(st.session_state.get("node2_proc")):
        kill_proc_tree(st.session_state.node2_proc)
        st.session_state.node2_proc = None

    try:
        current_pid = os.getpid()
        for p in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if p.info.get("pid") == current_pid:
                    continue
                if "python" in (p.info.get("name") or "").lower():
                    cmdline = " ".join(p.info.get("cmdline") or []).lower()
                    if "node2.py" in cmdline:
                        p.kill()
            except Exception:
                continue
    except Exception:
        pass

def start_vision(source_val, target_val="ALL", conf_val=0.20, augment=False):
    stop_vision()
    cmd = [
        PYTHON_EXE,
        "edge_node_vision.py",
        "--source",
        str(source_val),
        "--target",
        str(target_val),
        "--conf",
        str(conf_val)
    ]
    if augment:
        cmd.append("--augment")

    flags = subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    st.session_state.vision_proc = subprocess.Popen(
        cmd,
        cwd=os.getcwd(),
        creationflags=flags
    )
    st.session_state.vision_source = str(source_val)
    st.session_state.vision_target = str(target_val)
    st.session_state.vision_conf = float(conf_val)
    st.session_state.vision_augment = bool(augment)

def stop_vision():
    if is_proc_active(st.session_state.get("vision_proc")):
        kill_proc_tree(st.session_state.vision_proc)
        st.session_state.vision_proc = None

    try:
        current_pid = os.getpid()
        for p in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if p.info.get("pid") == current_pid:
                    continue
                if "python" in (p.info.get("name") or "").lower():
                    cmdline = " ".join(p.info.get("cmdline") or []).lower()
                    if "edge_node_vision.py" in cmdline:
                        p.kill()
            except Exception:
                continue
    except Exception:
        pass

def init_state():
    if "recent_page_number" not in st.session_state:
        st.session_state.recent_page_number = 1

    if "node2_proc" not in st.session_state:
        st.session_state.node2_proc = None

    if "vision_proc" not in st.session_state:
        st.session_state.vision_proc = None

    if "vision_source" not in st.session_state:
        st.session_state.vision_source = "0"

    if "vision_target" not in st.session_state:
        st.session_state.vision_target = "ALL"

    if "vision_conf" not in st.session_state:
        st.session_state.vision_conf = 0.20

    if "vision_augment" not in st.session_state:
        st.session_state.vision_augment = False

    if not is_node2_active():
        start_node2()

# ============================================================
# TABLE RENDERER
# ============================================================

def get_badge(defect_type):
    if defect_type == "Large Hole":
        return f'<span class="defect-badge defect-red">{defect_type}</span>'
    elif defect_type == "Small Hole":
        return f'<span class="defect-badge defect-amber">{defect_type}</span>'
    elif defect_type == "Large Tear":
        return f'<span class="defect-badge defect-orange">{defect_type}</span>'
    elif defect_type == "Small Tear":
        return f'<span class="defect-badge defect-purple">{defect_type}</span>'
    elif defect_type == "Belt Joint":
        return f'<span class="defect-badge defect-sky">{defect_type}</span>'
    return f'<span class="defect-badge">{defect_type}</span>'

def parse_bbox_details(bbox_str):
    try:
        if isinstance(bbox_str, (list, tuple)):
            coords = bbox_str
        else:
            s = str(bbox_str).strip()
            coords = ast.literal_eval(s)
        if isinstance(coords, (list, tuple)) and len(coords) >= 4:
            x1, y1, x2, y2 = [int(float(c)) for c in coords[:4]]
            w = abs(x2 - x1)
            h = abs(y2 - y1)
            return f"{w} × {h} px", f"[{x1}, {y1}, {x2}, {y2}]"
    except Exception:
        pass
    return "-", str(bbox_str)

def get_status_badge(defect_type):
    if defect_type in ["Large Hole", "Large Tear"]:
        return '<span class="status-tag tag-critical">Critical Action</span>'
    elif defect_type in ["Small Hole", "Small Tear"]:
        return '<span class="status-tag tag-warning">Surface Flaw</span>'
    elif defect_type == "Belt Joint":
        return '<span class="status-tag tag-info">Belt Splice</span>'
    return '<span class="status-tag tag-neutral">Inspected</span>'

def render_table_html(df_subset):
    if df_subset.empty:
        return "<div style='color:#64748b; font-size:13px; padding:18px;'>No defect events recorded yet.</div>"

    rows = []
    for _, row in df_subset.iterrows():
        ts = row.get("Timestamp", "")
        if isinstance(ts, (int, float)):
            ts = pd.to_datetime(ts, unit="s").strftime("%H:%M:%S")
        elif pd.notnull(ts):
            ts = str(ts)

        defect = str(row.get("Defect Type", ""))
        conf = row.get("Confidence", 0.0)
        try:
            conf_num = float(conf) * 100.0
        except Exception:
            conf_num = 0.0
        conf_str = f"{conf_num:.1f}%"
        sender = str(row.get("Sender ID", "Node 1 (Camera)"))
        dims, bbox_clean = parse_bbox_details(row.get("Bounding Box", "[]"))
        status_badge = get_status_badge(defect)

        rows.append(f"""
        <tr>
            <td class="font-mono" style="color:#94a3b8;">{ts}</td>
            <td>{get_badge(defect)}</td>
            <td>
                <div style="display:flex; align-items:center; gap:8px;">
                    <span class="font-mono" style="min-width:44px; color:#f8fafc;">{conf_str}</span>
                    <div style="flex:1; max-width:80px; height:5px; background:#1e293b; border-radius:3px; overflow:hidden;">
                        <div style="width:{min(100, max(0, int(conf_num)))}%; height:100%; background:#3b82f6; border-radius:3px;"></div>
                    </div>
                </div>
            </td>
            <td class="font-mono" style="color:#38bdf8;">{dims}</td>
            <td style="color:#94a3b8;">{sender}</td>
            <td class="font-mono" style="color:#cbd5e1; font-size:11px;">{bbox_clean}</td>
            <td>{status_badge}</td>
        </tr>
        """)

    return f"""
    <div class="neat-table-wrap">
        <table class="neat-table">
            <thead>
                <tr>
                    <th style="width: 11%;">Timestamp</th>
                    <th style="width: 15%;">Defect Type</th>
                    <th style="width: 16%;">Certainty</th>
                    <th style="width: 14%;">Flaw Dimensions</th>
                    <th style="width: 14%;">Source Node</th>
                    <th style="width: 16%;">Bounding Box</th>
                    <th style="width: 14%;">System Action</th>
                </tr>
            </thead>
            <tbody>
                {"".join(rows)}
            </tbody>
        </table>
    </div>
    """

# ============================================================
# ALTAIR CERTAINTY CHART
# ============================================================

def create_certainty_chart(df):
    plot_df = df.copy().reset_index(drop=True)
    plot_df["Event Number"] = range(1, len(plot_df) + 1)
    plot_df["Confidence %"] = (plot_df["Confidence"] * 100).round(1)

    chart = (
        alt.Chart(plot_df)
        .mark_area(
            line={"color": "#3b82f6", "strokeWidth": 2},
            color=alt.Gradient(
                gradient="linear",
                stops=[
                    alt.GradientStop(color="rgba(59, 130, 246, 0.3)", offset=0),
                    alt.GradientStop(color="rgba(59, 130, 246, 0.0)", offset=1),
                ],
                x1=1,
                x2=1,
                y1=1,
                y2=0,
            ),
        )
        .encode(
            x=alt.X(
                "Event Number:Q",
                title="Event Sequence",
                axis=alt.Axis(
                    labelColor="#94a3b8",
                    titleColor="#94a3b8",
                    gridColor="#1e293b",
                    domainColor="#1e293b"
                ),
            ),
            y=alt.Y(
                "Confidence %:Q",
                title="Confidence (%)",
                scale=alt.Scale(domain=[0, 100]),
                axis=alt.Axis(
                    labelColor="#94a3b8",
                    titleColor="#94a3b8",
                    gridColor="#1e293b",
                    domainColor="#1e293b"
                ),
            ),
        )
        .properties(height=210, background="transparent")
        .configure_view(strokeWidth=0)
    )
    return chart

# ============================================================
# MAIN APPLICATION
# ============================================================

def main():
    init_state()

    # --------------------------------------------------------
    # SIDEBAR: HARDWARE & SETTINGS
    # --------------------------------------------------------
    with st.sidebar:
        st.markdown('<div style="font-size:16px; font-weight:700; color:#f8fafc; margin-bottom:4px;">Control Panel</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px; color:#64748b; margin-bottom:14px;">Hardware & Inspection Setup</div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section-title">Video Input</div>', unsafe_allow_html=True)
        cam_choice = st.radio(
            "Camera Device:",
            options=[
                "Laptop Camera (Integrated)",
                "Phone Camera (DroidCam)"
            ],
            index=0,
            key="side_cam_device"
        )

        target_src = "0"
        if "Phone Camera" in cam_choice:
            droidcam_mode = st.radio(
                "Connection Mode:",
                options=[
                    "USB Cable / DroidCam PC Client",
                    "Wi-Fi Network (IP Stream)"
                ],
                key="side_droidcam_mode"
            )
            if "Wi-Fi" in droidcam_mode:
                ip_input = st.text_input("Phone IP Address:", "192.168.1.15:4747", key="side_droidcam_ip")
                target_src = ip_input.strip()
            else:
                target_src = "DROIDCAM"

        st.markdown('<div class="sidebar-section-title">Detection Filters</div>', unsafe_allow_html=True)
        defect_choice = st.selectbox(
            "Filter Defect Class:",
            options=[
                "All Defects (Full Inspection)",
                "Large Hole",
                "Small Hole",
                "Belt Joint",
                "Large Tear",
                "Small Tear"
            ],
            index=0,
            key="side_defect_filter"
        )

        target_defect = "ALL"
        if "Large Hole" in defect_choice:
            target_defect = "Large Hole"
        elif "Small Hole" in defect_choice:
            target_defect = "Small Hole"
        elif "Belt Joint" in defect_choice:
            target_defect = "Belt Joint"
        elif "Large Tear" in defect_choice:
            target_defect = "Large Tear"
        elif "Small Tear" in defect_choice:
            target_defect = "Small Tear"

        conf_slider = st.slider(
            "Sensitivity Threshold:",
            min_value=10,
            max_value=80,
            value=int(st.session_state.vision_conf * 100),
            step=5,
            key="side_conf_slider"
        ) / 100.0

        enable_tta = st.checkbox(
            "Multi-Pass Inference (TTA)",
            value=st.session_state.get("vision_augment", False),
            key="side_tta_check"
        )

        st.markdown('<div class="sidebar-section-title">System Controls</div>', unsafe_allow_html=True)
        v_active = is_vision_active()
        n_active = is_node2_active()

        if v_active:
            if st.button("Stop Inspection Camera", key="btn_stop_cam", use_container_width=True):
                stop_vision()
                st.rerun()
        else:
            if st.button("Start Inspection Camera", key="btn_start_cam", use_container_width=True):
                start_vision(target_src, target_defect, conf_slider, enable_tta)
                st.rerun()

        if not n_active:
            if st.button("Start Defect Logger", key="btn_start_logger", use_container_width=True):
                start_node2()
                st.rerun()
        else:
            if st.button("Restart Defect Logger", key="btn_restart_logger", use_container_width=True):
                stop_node2()
                start_node2()
                st.rerun()

        st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
        if st.button("Refresh Telemetry Data", key="btn_refresh_data", use_container_width=True):
            st.rerun()

        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
        if st.button("Open Defect Test Targets", key="btn_open_test_targets", use_container_width=True):
            test_path = os.path.abspath("test_defects.html")
            import webbrowser
            webbrowser.open(f"file:///{test_path}")

    # --------------------------------------------------------
    # MAIN WORKSPACE
    # --------------------------------------------------------

    # Top Status Bar
    v_status = f"Active ({st.session_state.vision_source})" if v_active else "Offline"
    n_status = "Listening (Port 5012)" if n_active else "Offline"
    v_led = "led-online" if v_active else "led-offline"
    n_led = "led-online" if n_active else "led-offline"

    st.html(f"""
    <div class="top-bar">
        <div class="brand-section">
            <div class="brand-badge">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="2" y="3" width="20" height="14" rx="2"></rect>
                    <line x1="8" y1="21" x2="16" y2="21"></line>
                    <line x1="12" y1="17" x2="12" y2="21"></line>
                </svg>
            </div>
            <div class="brand-headings">
                <h1>Conveyor Belt Quality Monitor</h1>
                <p>Surface Integrity &amp; Optical Flaw Detection</p>
            </div>
        </div>
        <div class="status-badges">
            <div class="status-pill">
                <span class="led-circle {v_led}"></span>
                <span>Camera Node: <b>{v_status}</b></span>
            </div>
            <div class="status-pill">
                <span class="led-circle {n_led}"></span>
                <span>Defect Logger: <b>{n_status}</b></span>
            </div>
        </div>
    </div>
    """)

    # Live Camera Feed Viewport (Real-Time In-Browser Inspection)
    if v_active:
        st.html("""
        <div class="content-box" style="margin-bottom: 20px;">
            <div class="content-box-header">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span class="led-circle led-online"></span>
                    <span>Live Camera Inspection Monitor (Real-Time Edge AI)</span>
                </div>
                <span style="font-size:11px; color:#10b981; font-family:var(--font-mono); font-weight:600;">ACTIVE STREAM &bull; PORT 5014</span>
            </div>
            <div style="background:#000000; display:flex; justify-content:center; align-items:center; min-height:360px; overflow:hidden;">
                <img src="http://127.0.0.1:5014/video_feed" 
                     style="max-width:100%; height:auto; max-height:480px; display:block;" 
                     onerror="this.onerror=null; this.src='latest_frame.jpg';"
                     alt="Live Edge AI Camera Feed">
            </div>
        </div>
        """)
    else:
        st.html("""
        <div class="content-box" style="margin-bottom: 20px;">
            <div class="content-box-header">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span class="led-circle led-offline"></span>
                    <span>Live Camera Inspection Monitor</span>
                </div>
                <span style="font-size:11px; color:#64748b; font-weight:500;">CAMERA OFFLINE</span>
            </div>
            <div style="background:#0c1017; display:flex; flex-direction:column; justify-content:center; align-items:center; min-height:220px; color:#64748b; gap:10px; padding:24px;">
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#475569" stroke-width="1.5">
                    <rect x="2" y="3" width="20" height="14" rx="2"></rect>
                    <line x1="8" y1="21" x2="16" y2="21"></line>
                    <line x1="12" y1="17" x2="12" y2="21"></line>
                </svg>
                <div style="font-size:14px; color:#94a3b8; font-weight:600;">Camera inspection feed is offline</div>
                <div style="font-size:12px; color:#64748b; text-align:center;">Click <b>Start Inspection Camera</b> in the left sidebar to stream live video with defect detection</div>
            </div>
        </div>
        """)

    render_live_telemetry()

def render_live_telemetry():
    # Load Data
    df = pd.DataFrame()
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            if not df.empty and "Defect Type" in df.columns:
                df["Defect Type"] = df["Defect Type"].replace(LABEL_MAP)
        except Exception:
            pass

    total_defects = len(df) if not df.empty else 0
    large_hole = len(df[df["Defect Type"] == "Large Hole"]) if not df.empty else 0
    small_hole = len(df[df["Defect Type"] == "Small Hole"]) if not df.empty else 0
    large_tear = len(df[df["Defect Type"] == "Large Tear"]) if not df.empty else 0
    small_tear = len(df[df["Defect Type"] == "Small Tear"]) if not df.empty else 0
    belt_joint = len(df[df["Defect Type"] == "Belt Joint"]) if not df.empty else 0
    avg_conf = df["Confidence"].mean() if not df.empty and "Confidence" in df.columns else 0.0

    # 1. KPI Stat Row (4 Clean Aligned Cards)
    k1, k2, k3, k4 = st.columns(4, gap="medium")
    with k1:
        st.html(f"""
        <div class="metric-card">
            <div class="metric-label">Total Defects</div>
            <div class="metric-value">{total_defects}</div>
            <div class="metric-footer">Logged inspection events</div>
        </div>
        """)
    with k2:
        st.html(f"""
        <div class="metric-card">
            <div class="metric-label">Hole Defects</div>
            <div class="metric-value">{large_hole + small_hole}</div>
            <div class="metric-footer">{large_hole} large &bull; {small_hole} small</div>
        </div>
        """)
    with k3:
        st.html(f"""
        <div class="metric-card">
            <div class="metric-label">Tear Defects</div>
            <div class="metric-value">{large_tear + small_tear}</div>
            <div class="metric-footer">{large_tear} severe &bull; {small_tear} minor</div>
        </div>
        """)
    with k4:
        st.html(f"""
        <div class="metric-card">
            <div class="metric-label">Mean Certainty</div>
            <div class="metric-value">{avg_conf:.1%}</div>
            <div class="metric-footer">Average model certainty</div>
        </div>
        """)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # 2. Visual Analytics Row (2 Equal-Height Balanced Columns)
    col_dist, col_chart = st.columns([1, 1], gap="medium")

    with col_dist:
        denom = max(1, total_defects)
        pct_lh = int((large_hole / denom) * 100)
        pct_sh = int((small_hole / denom) * 100)
        pct_lt = int((large_tear / denom) * 100)
        pct_st = int((small_tear / denom) * 100)
        pct_bj = int((belt_joint / denom) * 100)

        st.html(f"""
        <div class="content-box">
            <div class="content-box-header">
                <span>Defect Breakdown by Classification</span>
                <span style="font-size:11px; color:#64748b; font-weight:500;">{total_defects} Total</span>
            </div>
            <div class="content-box-body">
                <div class="dist-row">
                    <span class="dist-label">Large Hole</span>
                    <div class="dist-track"><div class="dist-fill" style="width:{pct_lh}%; background:#f43f5e;"></div></div>
                    <span class="dist-numbers">{large_hole} ({pct_lh}%)</span>
                </div>
                <div class="dist-row">
                    <span class="dist-label">Small Hole</span>
                    <div class="dist-track"><div class="dist-fill" style="width:{pct_sh}%; background:#f59e0b;"></div></div>
                    <span class="dist-numbers">{small_hole} ({pct_sh}%)</span>
                </div>
                <div class="dist-row">
                    <span class="dist-label">Large Tear</span>
                    <div class="dist-track"><div class="dist-fill" style="width:{pct_lt}%; background:#f97316;"></div></div>
                    <span class="dist-numbers">{large_tear} ({pct_lt}%)</span>
                </div>
                <div class="dist-row">
                    <span class="dist-label">Small Tear</span>
                    <div class="dist-track"><div class="dist-fill" style="width:{pct_st}%; background:#a855f7;"></div></div>
                    <span class="dist-numbers">{small_tear} ({pct_st}%)</span>
                </div>
                <div class="dist-row" style="margin-bottom:0;">
                    <span class="dist-label">Belt Joint</span>
                    <div class="dist-track"><div class="dist-fill" style="width:{pct_bj}%; background:#0ea5e9;"></div></div>
                    <span class="dist-numbers">{belt_joint} ({pct_bj}%)</span>
                </div>
            </div>
        </div>
        """)

    with col_chart:
        if not df.empty and "Confidence" in df.columns:
            st.html("""
            <div class="content-box">
                <div class="content-box-header">
                    <span>Certainty Trend Over Time</span>
                    <span style="font-size:11px; color:#64748b; font-weight:500;">Per-Event Confidence</span>
                </div>
            </div>
            """)
            st.altair_chart(create_certainty_chart(df), use_container_width=True)
        else:
            st.html("""
            <div class="content-box" style="height:250px; display:flex; align-items:center; justify-content:center; color:#64748b; font-size:13px;">
                Awaiting detection events to plot certainty curve...
            </div>
            """)

    # 3. Detection Event Stream & History
    st.html("""
    <div class="content-box" style="margin-bottom:12px;">
        <div class="content-box-header">
            <span>Recent Detection Activity</span>
            <span style="font-size:11px; color:#64748b; font-weight:500;">Latest Logged Events</span>
        </div>
    </div>
    """)

    if not df.empty:
        display_df = df.copy().iloc[::-1].reset_index(drop=True)
        total_records = len(display_df)
        total_pages = max(1, (total_records + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE)

        page_num = min(max(st.session_state.recent_page_number, 1), total_pages)
        st.session_state.recent_page_number = page_num

        start_idx = (page_num - 1) * ROWS_PER_PAGE
        end_idx = min(start_idx + ROWS_PER_PAGE, total_records)

        paged_df = display_df.iloc[start_idx:end_idx].copy()
        st.html(render_table_html(paged_df))

        # Pagination controls
        if total_pages > 1:
            col_p, col_m, col_n = st.columns([1, 2, 1])
            with col_p:
                if page_num > 1 and st.button("Previous Page", key="tbl_prev_btn", use_container_width=True):
                    st.session_state.recent_page_number = page_num - 1
                    st.rerun()
            with col_m:
                st.markdown(f"<div style='text-align:center; color:#64748b; padding-top:10px; font-size:13px; font-family:var(--font-mono);'>Page {page_num} of {total_pages} &bull; {total_records} total events</div>", unsafe_allow_html=True)
            with col_n:
                if page_num < total_pages and st.button("Next Page", key="tbl_next_btn", use_container_width=True):
                    st.session_state.recent_page_number = page_num + 1
                    st.rerun()
    else:
        st.html("""
        <div style="background:#111827; border:1px solid #1f293d; border-radius:8px; padding:32px; text-align:center; color:#64748b; font-size:14px;">
            No defect records detected yet. Start the inspection camera in the sidebar to begin scanning.
        </div>
        """)

if __name__ == "__main__":
    main()