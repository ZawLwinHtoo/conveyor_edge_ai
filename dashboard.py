import streamlit as st
import pandas as pd
import os
import textwrap
import subprocess
import sys

PYTHON_EXE = sys.executable


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Conveyor AI Monitor",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    textwrap.dedent("""
    <style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    html, body {
        background-color: #080b10 !important;
        color: #f8fafc !important;
    }

    [data-testid="stAppViewContainer"] {
        background-color: #080b10 !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    .block-container {
        padding-top: 0.7rem !important;
        padding-bottom: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1600px !important;
    }


    /* ======================================================
       HEADER
       ====================================================== */

    .dashboard-header {
        background: linear-gradient(
            135deg,
            #111827,
            #0f172a
        );

        padding: 14px 22px;
        border-radius: 14px;
        margin-bottom: 12px;

        border: 1px solid #1e293b;

        box-shadow:
            0 5px 24px rgba(0, 0, 0, 0.40);
    }

    .dashboard-title {
        color: #f8fafc;
        font-size: 25px;
        font-weight: 700;
        margin: 0;
    }

    .dashboard-subtitle {
        color: #94a3b8;
        font-size: 12px;
        margin-top: 3px;
    }


    /* ======================================================
       KPI CARDS
       ====================================================== */

    .metric-card {
        background: #111827;
        border-radius: 12px;

        padding: 10px 15px;
        min-height: 68px;

        border: 1px solid #233046;

        box-shadow:
            0 3px 12px rgba(0, 0, 0, 0.25);
    }

    .metric-label {
        color: #94a3b8;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.4px;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 24px;
        font-weight: 700;
        margin-top: 1px;
    }

    .metric-icon {
        float: right;
        font-size: 19px;
    }


    /* ======================================================
       SECTION TITLES
       ====================================================== */

    .section-title {
        color: #e2e8f0;
        font-size: 14px;
        font-weight: 700;
        margin-top: 5px;
        margin-bottom: 6px;
    }

    .section-title-large {
        color: #f8fafc;
        font-size: 22px;
        font-weight: 700;
        margin: 0;
    }


    /* ======================================================
       PAGE TITLE CARD
       ====================================================== */

    .page-title-card {
        width: 100%;
        box-sizing: border-box;

        background: #11161d;

        border: 1px solid #252d38;
        border-radius: 14px;

        padding: 17px 20px;

        margin-bottom: 14px;

        box-shadow:
            0 4px 18px rgba(0, 0, 0, 0.25);
    }


    /* ======================================================
       TABLE VIEW STYLING
       ====================================================== */

    [data-testid="stDataFrame"] {
        background: #11161d !important;
        border: 1px solid #2a3441 !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    [data-testid="stDataFrame"] > div {
        background: #11161d !important;
    }

    .table-summary {
        color: #94a3b8;
        font-size: 13px;
        margin: 5px 0 10px 2px;
    }


    /* ======================================================
       STATUS CARDS
       ====================================================== */

    .status-box {
        background: #11161d;

        border: 1px solid #252d38;

        border-radius: 10px;

        padding: 8px 12px;

        box-shadow:
            0 2px 8px rgba(0, 0, 0, 0.20);

        font-size: 11px;

        color: #cbd5e1;
    }

    .status-dot {
        color: #22c55e;
        font-weight: 700;
    }


    /* ======================================================
       BUTTONS
       ====================================================== */

    [data-testid="stButton"] button {
        background-color: #11161d !important;

        color: #f8fafc !important;

        border: 1px solid #334155 !important;

        border-radius: 8px !important;

        box-shadow: none !important;

        min-height: 38px;
    }

    [data-testid="stButton"] button:hover {
        background-color: #1f2937 !important;

        color: #ffffff !important;

        border-color: #475569 !important;
    }


    /* ======================================================
       SPACING
       ====================================================== */

    div[data-testid="stVerticalBlock"] {
        gap: 0.35rem;
    }

    [data-testid="stHorizontalBlock"] {
        gap: 0.65rem;
    }

    </style>
    """),
    unsafe_allow_html=True
)


# ============================================================
# DATA
# ============================================================

DATA_FILE = "detections.csv"
ROWS_PER_PAGE = 10


# ============================================================
# SESSION STATE & PROCESS MANAGEMENT
# ============================================================

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


def start_node2():
    if not is_proc_active(st.session_state.node2_proc):
        st.session_state.node2_proc = subprocess.Popen(
            [PYTHON_EXE, "node2.py"],
            cwd=os.getcwd()
        )


def stop_node2():
    if is_proc_active(st.session_state.node2_proc):
        kill_proc_tree(st.session_state.node2_proc)
        st.session_state.node2_proc = None


def start_vision(source_val):
    stop_vision()
    st.session_state.vision_proc = subprocess.Popen(
        [PYTHON_EXE, "edge_node_vision.py", "--source", str(source_val)],
        cwd=os.getcwd()
    )
    st.session_state.vision_source = str(source_val)


def stop_vision():
    if is_proc_active(st.session_state.vision_proc):
        kill_proc_tree(st.session_state.vision_proc)
        st.session_state.vision_proc = None

    # Fallback cleanup for lingering vision processes on Windows
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["powershell", "-Command", "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*edge_node_vision.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            pass


def init_state():
    if "dashboard_page" not in st.session_state:
        st.session_state.dashboard_page = "overview"

    if "recent_page_number" not in st.session_state:
        st.session_state.recent_page_number = 1

    if "node2_proc" not in st.session_state:
        st.session_state.node2_proc = None

    if "vision_proc" not in st.session_state:
        st.session_state.vision_proc = None

    if "vision_source" not in st.session_state:
        st.session_state.vision_source = "0"

    # Auto-start Node 2 Logger if not running
    if not is_proc_active(st.session_state.node2_proc):
        start_node2()


# ============================================================
# CONTROL PANEL
# ============================================================

def render_control_panel():
    with st.expander("⚙️ Camera Selection & Edge AI Control Center", expanded=True):
        col1, col2 = st.columns([3, 2])

        with col1:
            cam_choice = st.radio(
                "Select Camera Source for AI Detection:",
                options=[
                    "💻 PC / Laptop Built-in Webcam (Camera 0)",
                    "📱 iPhone / DroidCam / USB Camera (Camera 1)",
                    "🌐 Smartphone IP Camera Stream (HTTP URL)",
                    "⚙️ Conveyor Belt Simulation Mode"
                ],
                index=0,
                key="cam_radio_select"
            )

            target_src = "0"
            if "Camera 1" in cam_choice:
                target_src = "1"
            elif "HTTP URL" in cam_choice:
                ip_url = st.text_input("Enter Smartphone IP Stream URL:", "http://192.168.1.15:8080/video")
                target_src = ip_url.strip()
            elif "Simulation" in cam_choice:
                target_src = "SIMULATION"

        with col2:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            v_active = is_proc_active(st.session_state.vision_proc)
            n_active = is_proc_active(st.session_state.node2_proc)

            if v_active:
                if st.button("⏹️ Stop AI Detection Node", key="btn_stop_vision", use_container_width=True):
                    stop_vision()
                    st.rerun()
            else:
                if st.button("▶️ Start AI Detection Node", key="btn_start_vision", use_container_width=True):
                    start_vision(target_src)
                    st.rerun()

            if not n_active:
                if st.button("▶️ Start Node 2 Logger", key="btn_start_node2", use_container_width=True):
                    start_node2()
                    st.rerun()
            else:
                if st.button("🔄 Restart Node 2 Logger", key="btn_restart_node2", use_container_width=True):
                    stop_node2()
                    start_node2()
                    st.rerun()

        st.markdown("<hr style='margin:12px 0 10px 0; border-color:#2a3441;'>", unsafe_allow_html=True)
        with st.expander("📖 Camera Setup Guide & Notes for Users", expanded=False):
            st.markdown("""
            #### 📌 Instructions for Camera Methods:

            * **💻 Option 1: PC / Laptop Built-in Webcam (Camera 0)**
              - **No setup required.** Uses your computer's built-in webcam.

            * **📱 Option 2: iPhone / DroidCam / USB Camera (Camera 1)**
              - **Best Setup**: Download free **DroidCam** (App Store on iPhone / Play Store on Android) and **DroidCam Client** on Windows (`dev47apps.com`). Connect via USB or Wi-Fi.
              - *(Alternative)*: Download **Camo App** (iPhone) & **Camo Studio** (Windows). *Note: Requires Microsoft Windows App SDK Runtime.*

            * **🌐 Option 3: Smartphone IP Camera Stream (HTTP URL)**
              - **Step 1**: Connect Phone & PC to the **same Wi-Fi network**.
              - **Step 2 (Important)**: Turn **OFF** any VPN/Proxy (e.g. NekoBox, WARP) or iCloud Private Relay on laptop and phone.
              - **Step 3 (App Setup)**: Download **IP Camera Lite** or **DroidCam** (iPhone) / **IP Webcam** (Android), tap *Start*, and note stream URL (e.g. `http://192.168.1.9:8081/video`).
              - **Step 4**: Test URL in laptop browser first, then paste into the input box above and click **▶️ Start AI Detection Node**.

            * **⚙️ Option 4: Conveyor Belt Simulation Mode**
              - **No hardware needed.** Generates synthetic conveyor belt defect simulations automatically.
            """)


# ============================================================
# HTML HELPER
# ============================================================

def render_html(content):
    st.html(content)


# ============================================================
# HEADER
# ============================================================

def render_header():
    render_html("""
    <div class="dashboard-header">

        <div class="dashboard-title">
            🚨 Conveyor Belt AI Monitor
        </div>

        <div class="dashboard-subtitle">
            Real-time defect detection & monitoring system
        </div>

    </div>
    """)


# ============================================================
# DATAFRAME STYLING FOR RECENT DETECTIONS
# ============================================================

def style_recent_dataframe(df):
    return (
        df.style
        .set_properties(**{
            "background-color": "#11161d",
            "color": "#e2e8f0",
            "border": "1px solid #2a3441",
            "padding": "12px 14px",
            "font-size": "14px",
            "text-align": "left",
            "white-space": "normal",
            "word-wrap": "break-word"
        })
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("background-color", "#171e27"),
                    ("color", "#f8fafc"),
                    ("font-weight", "700"),
                    ("text-transform", "uppercase"),
                    ("letter-spacing", "0.08em"),
                    ("padding", "12px 14px"),
                    ("border", "1px solid #2a3441"),
                    ("text-align", "left")
                ]
            },
            {
                "selector": "td",
                "props": [
                    ("border", "1px solid #252d38"),
                    ("padding", "12px 14px"),
                    ("color", "#e2e8f0"),
                    ("background-color", "#11161d")
                ]
            },
            {
                "selector": "tbody tr:hover",
                "props": [("background-color", "#1a222c")]
            }
        ])
    )


# ============================================================
# SYSTEM STATUS
# ============================================================

def render_system_status():
    status1, status2, status3 = st.columns(3)

    v_active = is_proc_active(st.session_state.vision_proc)
    n_active = is_proc_active(st.session_state.node2_proc)
    v_src = st.session_state.vision_source if v_active else "Stopped"

    with status1:
        dot_color = "#22c55e" if v_active else "#ef4444"
        text_label = f"Online ({v_src})" if v_active else "Stopped"
        render_html(f"""
        <div class="status-box">
            <span class="status-dot" style="color:{dot_color}">●</span>
            &nbsp; Vision Node <b>{text_label}</b>
        </div>
        """)

    with status2:
        dot_color = "#22c55e" if v_active else "#64748b"
        text_label = "Active (YOLO)" if v_active else "Idle"
        render_html(f"""
        <div class="status-box">
            <span class="status-dot" style="color:{dot_color}">●</span>
            &nbsp; YOLO AI Detection <b>{text_label}</b>
        </div>
        """)

    with status3:
        dot_color = "#22c55e" if n_active else "#ef4444"
        text_label = "Active (Port 5012)" if n_active else "Stopped"
        render_html(f"""
        <div class="status-box">
            <span class="status-dot" style="color:{dot_color}">●</span>
            &nbsp; Node 2 Logger <b>{text_label}</b>
        </div>
        """)


# ============================================================
# PAGE 1 - OVERVIEW
# ============================================================

def render_overview_page(
    df,
    total_defects,
    lubang_besar,
    lubang_kecil,
    avg_confidence
):
    # KPI
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_html(f"""
        <div class="metric-card">

            <span class="metric-icon">🚨</span>

            <div class="metric-label">
                TOTAL DEFECTS
            </div>

            <div class="metric-value">
                {total_defects}
            </div>

        </div>
        """)

    with col2:
        render_html(f"""
        <div class="metric-card">

            <span class="metric-icon">🔴</span>

            <div class="metric-label">
                LUBANG BESAR
            </div>

            <div class="metric-value">
                {lubang_besar}
            </div>

        </div>
        """)

    with col3:
        render_html(f"""
        <div class="metric-card">

            <span class="metric-icon">🟡</span>

            <div class="metric-label">
                LUBANG KECIL
            </div>

            <div class="metric-value">
                {lubang_kecil}
            </div>

        </div>
        """)

    with col4:
        render_html(f"""
        <div class="metric-card">

            <span class="metric-icon">🎯</span>

            <div class="metric-label">
                AVG CONFIDENCE
            </div>

            <div class="metric-value">
                {avg_confidence:.0%}
            </div>

        </div>
        """)

    # Charts
    chart1, chart2 = st.columns(2)

    with chart1:
        render_html("""
        <div class="section-title">
            📊 Defect Distribution
        </div>
        """)

        defect_counts = df["Defect Type"].value_counts()
        st.bar_chart(defect_counts, height=270)

    with chart2:
        render_html("""
        <div class="section-title">
            🎯 Detection Confidence
        </div>
        """)

        confidence_data = df[["Confidence"]].copy()
        confidence_data.index = range(1, len(confidence_data) + 1)
        st.line_chart(confidence_data, height=270)

    render_system_status()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if st.button(
        "📋 Recent Detections →",
        key="navigate_recent",
        use_container_width=True
    ):
        st.session_state.dashboard_page = "recent"
        st.session_state.recent_page_number = 1
        st.rerun()


# ============================================================
# PAGE 2 - RECENT DETECTIONS
# ============================================================

def render_recent_detections_page(df):
    render_html("""
    <div class="page-title-card">
        <div class="section-title-large">
            📋 Recent Detections
        </div>
    </div>
    """)

    back_col, _ = st.columns([1, 4])

    with back_col:
        if st.button(
            "← Back to Overview",
            key="back_to_overview"
        ):
            st.session_state.dashboard_page = "overview"
            st.session_state.recent_page_number = 1
            st.rerun()

    display_df = df.copy().iloc[::-1].reset_index(drop=True)
    total_records = len(display_df)
    total_pages = max(1, (total_records + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE)

    page_number = min(max(st.session_state.recent_page_number, 1), total_pages)
    st.session_state.recent_page_number = page_number

    start_index = (page_number - 1) * ROWS_PER_PAGE
    end_index = min(start_index + ROWS_PER_PAGE, total_records)

    page_df = display_df.iloc[start_index:end_index].copy()

    if "Timestamp" in page_df.columns:
        page_df["Timestamp"] = pd.to_datetime(page_df["Timestamp"], unit="s").dt.strftime("%H:%M:%S")

    if "Confidence" in page_df.columns:
        page_df["Confidence"] = (page_df["Confidence"] * 100).round(1).astype(str) + "%"

    page_df = page_df[[
        "Timestamp",
        "Sender ID",
        "Defect Type",
        "Confidence",
        "Bounding Box"
    ]].copy()

    summary_text = f"Showing {start_index + 1}–{end_index} of {total_records} detections"
    st.markdown(f"<div class='table-summary'>{summary_text}</div>", unsafe_allow_html=True)

    styled_df = style_recent_dataframe(page_df)
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        height=390
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    prev_col, page_col, next_col = st.columns([1, 1, 1])

    with prev_col:
        if page_number > 1 and st.button("← Previous", key="prev_page", use_container_width=True):
            st.session_state.recent_page_number = page_number - 1
            st.rerun()

    with page_col:
        st.markdown(
            f"<div style='text-align:center; color:#94a3b8; padding-top:9px; font-size:13px;'>Page {page_number} of {total_pages}</div>",
            unsafe_allow_html=True
        )

    with next_col:
        if page_number < total_pages and st.button("Next →", key="next_page", use_container_width=True):
            st.session_state.recent_page_number = page_number + 1
            st.rerun()


# ============================================================
# MAIN DASHBOARD
# ============================================================

@st.fragment(run_every="5s")
def dashboard():
    init_state()
    render_header()
    render_control_panel()

    if not os.path.exists(DATA_FILE):
        st.warning("⚠️ Waiting for detection data from Node 1...")
        return

    try:
        df = pd.read_csv(DATA_FILE)
    except Exception as e:
        st.error(f"Unable to read detection data: {e}")
        return

    if df.empty:
        st.info("Waiting for defect detection data...")
        return

    total_defects = len(df)
    lubang_besar = len(df[df["Defect Type"] == "Lubang Besar"])
    lubang_kecil = len(df[df["Defect Type"] == "Lubang Kecil"])
    avg_confidence = df["Confidence"].mean()

    current_page = st.session_state.dashboard_page

    if current_page == "recent":
        render_recent_detections_page(df)
    else:
        render_overview_page(
            df,
            total_defects,
            lubang_besar,
            lubang_kecil,
            avg_confidence
        )


# ============================================================
# START
# ============================================================

dashboard()