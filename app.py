from __future__ import annotations

import base64
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

from data_generator import ZONES, generate_scada_data, ensure_sample_csv

APP_DIR = Path(__file__).resolve().parent
DATA_PATH = APP_DIR / "sample_scada_data.csv"
LOGO_PATH = APP_DIR / "sewa_logo.png"
PPT_PATH = APP_DIR / "AquaSmart_SEWA_Executive_Pitch.pptx"

st.set_page_config(
    page_title="AquaSmart SEWA Control Room",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Styling
# -----------------------------
def img_to_base64(path: Path) -> str:
    if not path.exists():
        return ""
    return base64.b64encode(path.read_bytes()).decode("utf-8")

logo_b64 = img_to_base64(LOGO_PATH)


def hex_to_rgba(hex_color: str, alpha: float = 0.28) -> str:
    """Convert #RRGGBB to Plotly rgba() for soft GIS zone polygons."""
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="stAppViewContainer"] {
    background:
      radial-gradient(circle at 18% 12%, rgba(0, 156, 255, .22), transparent 30%),
      radial-gradient(circle at 78% 20%, rgba(0, 80, 160, .25), transparent 28%),
      linear-gradient(135deg, #051525 0%, #06284a 48%, #020a14 100%);
    color: #F8FBFF;
}
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0b396d 0%, #061628 72%, #030a12 100%); border-right: 1px solid rgba(0, 174, 255, .30); }
[data-testid="stSidebar"] * { color: #f4f9ff; }
.block-container { padding-top: 1.0rem; padding-bottom: 2rem; max-width: 1900px; }

.topbar {
    display: grid;
    grid-template-columns: 260px 1fr 230px 260px;
    gap: 18px;
    align-items: center;
    margin-bottom: 16px;
}
.logo-card {
    background: #ffffff;
    border-radius: 2px;
    padding: 10px 14px;
    height: 94px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 22px rgba(34, 180, 255, .18);
}
.logo-card img { max-height: 82px; max-width: 230px; object-fit: contain; }
.brand {
    display: flex;
    gap: 22px;
    align-items: center;
}
.water-icon {
    width: 76px; height: 76px; border-radius: 50%;
    background: radial-gradient(circle at 30% 25%, #c8f8ff 0%, #52c9ff 34%, #0066cc 68%, #04172c 100%);
    box-shadow: 0 0 34px rgba(65, 205, 255, .65);
    display: flex; align-items: center; justify-content: center;
    font-size: 42px;
}
.brand h1 { margin: 0; font-size: 2.45rem; font-weight: 850; letter-spacing: -.04em; color: white; }
.brand p { margin: 8px 0 0; color: #35ccff; font-size: 1.05rem; font-weight: 650; }
.status-card, .alert-summary {
    border: 1px solid rgba(63, 180, 255, .55);
    border-radius: 14px;
    padding: 16px 18px;
    background: linear-gradient(140deg, rgba(11, 48, 86, .94), rgba(4, 18, 35, .92));
    box-shadow: inset 0 0 20px rgba(47, 173, 255, .08), 0 0 16px rgba(0, 125, 255, .16);
    min-height: 94px;
}
.alert-summary {
    border-color: rgba(255, 52, 52, .95);
    background: radial-gradient(circle at 15% 25%, rgba(255, 94, 57, .42), transparent 34%), linear-gradient(140deg, rgba(82, 5, 12, .95), rgba(27, 5, 9, .92));
    box-shadow: 0 0 28px rgba(255, 28, 28, .30), inset 0 0 18px rgba(255, 50, 50, .12);
}
.online-pill { background: linear-gradient(90deg,#0a8f3d,#20d86c); color: white; border-radius: 9px; padding: 4px 12px; font-size: .72rem; font-weight: 850; float: right; }
.alert-big { font-size: 2.4rem; font-weight: 900; float: right; }
.panel {
    background: linear-gradient(180deg, rgba(4, 31, 58, .88), rgba(3, 14, 26, .88));
    border: 1px solid rgba(61, 176, 255, .48);
    border-radius: 12px;
    box-shadow: 0 0 20px rgba(0, 137, 255, .12), inset 0 0 20px rgba(0, 180, 255, .035);
    padding: 16px;
    min-height: 95px;
}
.panel-title {
    text-transform: uppercase;
    font-weight: 850;
    color: #f7fbff;
    letter-spacing: -.02em;
    margin-bottom: 12px;
    font-size: 1rem;
}
.kpi-card {
    height: 114px;
    border: 1px solid rgba(60, 180, 255, .50);
    border-radius: 12px;
    background: linear-gradient(140deg, rgba(12, 48, 88, .88), rgba(3, 15, 29, .92));
    padding: 18px 18px;
    box-shadow: inset 0 0 22px rgba(44, 175, 255, .05), 0 0 15px rgba(0, 119, 220, .12);
}
.kpi-label { color: #bfe6ff; font-weight: 800; text-transform: uppercase; font-size: .76rem; text-align: right; }
.kpi-value { color: white; font-size: 1.85rem; font-weight: 900; margin-top: 6px; }
.kpi-change.good { color: #21ff84; font-weight: 800; font-size: .82rem; }
.kpi-change.bad { color: #ff5757; font-weight: 800; font-size: .82rem; }
.kpi-icon { font-size: 2.4rem; filter: drop-shadow(0 0 14px rgba(76, 202, 255, .72)); float:left; margin-right:12px; }
.alarm-card {
    position: relative;
    margin-bottom: 16px;
    border-radius: 10px;
    padding: 18px 18px;
    border: 1.8px solid #ff3333;
    background: linear-gradient(140deg, rgba(107, 0, 12, .72), rgba(42, 0, 7, .88));
    box-shadow: 0 0 22px rgba(255, 39, 39, .30);
    animation: blinkBorder 1.1s infinite;
}
.alarm-card.warning {
    border-color: #ffc233;
    background: linear-gradient(140deg, rgba(119, 77, 0, .70), rgba(46, 27, 0, .90));
    box-shadow: 0 0 20px rgba(255, 184, 33, .25);
    animation: blinkWarning 1.4s infinite;
}
.alarm-level { position:absolute; right:18px; top:20px; background:#ff2f38; color:#fff; font-size:.68rem; font-weight:850; padding:7px 10px; border-radius:6px; }
.alarm-card.warning .alarm-level { background:#c97902; }
.alarm-title { font-weight:900; color:white; margin-bottom:16px; }
.alarm-zone { font-size:1.05rem; font-weight:900; }
.alarm-desc { color:#ffffff; font-size:.88rem; margin-top:4px; }
.alarm-time { color:#ffffff; font-size:.82rem; margin-top:18px; }
@keyframes blinkBorder { 0%,100% { box-shadow: 0 0 8px rgba(255, 30, 30, .35); } 50% { box-shadow: 0 0 36px rgba(255, 30, 30, .95); } }
@keyframes blinkWarning { 0%,100% { box-shadow: 0 0 8px rgba(255, 198, 44, .25); } 50% { box-shadow: 0 0 30px rgba(255, 198, 44, .82); } }
.zone-grid { display:grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }
.zone-card { background: rgba(2, 18, 36, .75); border: 1px solid rgba(70, 185, 255, .30); padding: 13px; border-radius: 12px; }
.zone-name { font-weight: 900; font-size: 1rem; }
.normal { color: #29ff8b; } .warning-text { color: #ffc226; } .critical { color:#ff4545; }
.small-muted { color: #9bc7e9; font-size: .78rem; }
.footer { color:#8ecdf9; font-size:.85rem; border-top:1px solid rgba(73,178,255,.25); margin-top:22px; padding-top:14px; }
.mobile-card { border: 1px solid rgba(80, 190, 255, .40); border-radius: 14px; padding: 16px; margin-bottom:12px; background: rgba(1, 18, 33, .84); }
.stButton > button, .stDownloadButton > button { background: linear-gradient(90deg,#0057c8,#00a6ff); color:white; border:0; border-radius:10px; font-weight:800; }
[data-testid="stMetricValue"] { color: white; }

.summary-card { border: 1px solid rgba(49, 210, 255, .55); background: linear-gradient(90deg, rgba(0, 94, 180, .34), rgba(1, 22, 43, .86)); border-radius: 14px; padding: 14px 18px; margin: 10px 0 18px 0; box-shadow: 0 0 22px rgba(0, 171, 255, .16); }
.detail-card { background: rgba(2, 20, 40, .82); border:1px solid rgba(70,185,255,.35); border-radius:12px; padding:14px; min-height:125px; }
.action-card { background: linear-gradient(140deg, rgba(0,78,139,.55), rgba(2,17,34,.88)); border-left: 5px solid #35ccff; border-radius:12px; padding:14px; margin-bottom:10px; }
.workflow { display:flex; gap:10px; flex-wrap:wrap; align-items:center; }
.workflow-step { border:1px solid rgba(80,190,255,.42); background:rgba(3,25,50,.78); border-radius:10px; padding:10px 12px; font-weight:800; }
.workflow-arrow { color:#35ccff; font-weight:900; }

@media (max-width: 900px) {
    .topbar { grid-template-columns: 1fr; }
    .logo-card { height: 86px; }
    .brand h1 { font-size: 1.9rem; }
    .zone-grid { grid-template-columns: 1fr; }
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Data
# -----------------------------
@st.cache_data(show_spinner=False)
def load_data(seed: int) -> pd.DataFrame:
    # Generate a fresh deterministic dataset from seed so the demo is repeatable.
    df = generate_scada_data(seed=seed)
    return df

with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_column_width=True)
    st.markdown("### AquaSmart SEWA")
    st.markdown("Synthetic SCADA control room demo")
    mobile_mode = st.toggle("📱 Field mobile view", value=False)
    st.divider()
    window = st.slider("Data refresh window", 48, 336, 168, step=24)
    seed = st.number_input("Demo seed", min_value=1, max_value=999, value=42, step=1)
    zone_options = list(ZONES.keys())
    selected_zones = st.multiselect("Zones", zone_options, default=zone_options)
    selected_detail_zone = st.selectbox("Zone detail page", zone_options, index=zone_options.index("Al Wurrayah") if "Al Wurrayah" in zone_options else 0)
    if st.button("↻ Refresh synthetic data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    st.caption("Synthetic demo only. Not connected to live SEWA systems.")
    st.markdown("<div style='height:130px'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;color:#35ccff;'>Water is Life</h3><p style='text-align:center;color:#dff6ff;'>Let's Protect Every Drop</p>", unsafe_allow_html=True)

if not selected_zones:
    selected_zones = zone_options

full_df = load_data(int(seed))
full_df = full_df[full_df["zone_name"].isin(selected_zones)].copy()
latest_ts = full_df["timestamp"].max()
start_cutoff = latest_ts - pd.Timedelta(hours=int(window))
df = full_df[full_df["timestamp"] >= start_cutoff].copy()
latest = df.sort_values("timestamp").groupby("zone_name").tail(1).copy()

# Rules: transparent score used for demo explanation.
latest["risk_score"] = (
    latest["leakage_probability"] * 100
    + np.where(latest["pressure_bar"] < 4.2, 15, 0)
    + np.where(latest["flow_rate_m3h"] > latest["flow_rate_m3h"].median() * 1.25, 10, 0)
).clip(0, 100)

critical_alerts = df[df["system_status"] == "Critical"].copy()
warning_alerts = df[df["system_status"] == "Warning"].copy()
alert_rows = df[df["system_status"].isin(["Critical", "Warning"])].sort_values("timestamp", ascending=False).head(8)

nrw = df["nrw_loss_pct"].mean()
alerts_count = len(df[df["anomaly_flag"] == 1])
response_hrs = df.loc[df["system_status"].isin(["Critical", "Warning"]), "response_time_min"].mean() / 60
if np.isnan(response_hrs):
    response_hrs = df["response_time_min"].mean() / 60
efficiency = df["system_efficiency_pct"].mean()
cost_savings = max(0, (28.6 - nrw) / 100 * df["consumption_m3"].sum() * 2.75)

# -----------------------------
# Operational intelligence helpers
# -----------------------------
ASSET_REGISTER = {
    "Zubara": {"pipe_material": "HDPE / DI", "diameter_mm": "160–300", "pipe_age": "8 years", "critical_customers": "Schools, residential blocks", "nearby_assets": "Zubara PRV chamber, local distribution main"},
    "Mussala": {"pipe_material": "DI / uPVC", "diameter_mm": "200–400", "pipe_age": "12 years", "critical_customers": "Market area, commercial shops", "nearby_assets": "Mussala control valve, coastal supply line"},
    "Hayawa": {"pipe_material": "DI / HDPE", "diameter_mm": "200–350", "pipe_age": "10 years", "critical_customers": "Residential clusters, mosque area", "nearby_assets": "Hayawa distribution loop"},
    "Al Luluyah": {"pipe_material": "HDPE", "diameter_mm": "160–250", "pipe_age": "6 years", "critical_customers": "Coastal community, villas", "nearby_assets": "Luluyah local network branch"},
    "Al Wurrayah": {"pipe_material": "DI / Steel transmission", "diameter_mm": "300–600", "pipe_age": "15 years", "critical_customers": "Storage station, high-level zones", "nearby_assets": "Al Wurrayah tank / pumping interface"},
}
SUPPLY_PROFILE = {
    "Zubara": {"supply_pressure_bar": 5.6, "supply_flow_m3h": 135, "suggested_pressure_bar": "5.2–5.8", "suggested_flow_m3h": "110–145"},
    "Mussala": {"supply_pressure_bar": 5.0, "supply_flow_m3h": 225, "suggested_pressure_bar": "4.7–5.4", "suggested_flow_m3h": "180–230"},
    "Hayawa": {"supply_pressure_bar": 4.8, "supply_flow_m3h": 205, "suggested_pressure_bar": "4.6–5.2", "suggested_flow_m3h": "160–215"},
    "Al Luluyah": {"supply_pressure_bar": 5.3, "supply_flow_m3h": 120, "suggested_pressure_bar": "5.0–5.6", "suggested_flow_m3h": "90–125"},
    "Al Wurrayah": {"supply_pressure_bar": 4.4, "supply_flow_m3h": 315, "suggested_pressure_bar": "4.8–5.5", "suggested_flow_m3h": "220–280"},
}
AED_PER_M3 = 2.75
def recommended_actions(row: pd.Series) -> list[str]:
    actions = []
    if row["system_status"] == "Critical" or row["leakage_probability"] >= 0.62:
        actions.append(f"Dispatch leak detection team to {row['zone_name']} and verify suspected section.")
    if row["pressure_bar"] < 4.2:
        actions.append("Check PRV setting and compare inlet/supply pressure with downstream pressure.")
    if row["flow_rate_m3h"] > latest["flow_rate_m3h"].median() * 1.25:
        actions.append("Investigate abnormal high flow and confirm whether demand is planned or leakage-related.")
    if row["anomaly_flag"] == 1 or row["event_type"] != "Normal":
        actions.append("Verify SCADA sensor reading, meter health, and recent maintenance activity.")
    if not actions:
        actions.append("Continue normal monitoring and keep trend under observation.")
    return actions
def estimate_losses(row: pd.Series) -> tuple[float, float]:
    baseline_loss_factor = max(0.05, row["leakage_probability"] * 0.18)
    water_loss_m3_day = row["flow_rate_m3h"] * 24 * baseline_loss_factor
    return water_loss_m3_day, water_loss_m3_day * AED_PER_M3
def make_zone_report(zone_row: pd.Series) -> pd.DataFrame:
    loss_m3_day, loss_aed_day = estimate_losses(zone_row)
    supply = SUPPLY_PROFILE.get(zone_row["zone_name"], {})
    return pd.DataFrame({"Item": ["Zone", "Status", "Pressure (bar)", "Suggested pressure", "Flow (m³/h)", "Suggested supply flow", "Consumption (m³)", "Leak probability", "Estimated water loss (m³/day)", "Estimated financial impact (AED/day)", "Last alert", "Recommended action"], "Value": [zone_row["zone_name"], zone_row["system_status"], f"{zone_row['pressure_bar']:.2f}", supply.get("suggested_pressure_bar", "N/A"), f"{zone_row['flow_rate_m3h']:.1f}", supply.get("suggested_flow_m3h", "N/A"), f"{zone_row['consumption_m3']:,.0f}", f"{zone_row['leakage_probability']:.0%}", f"{loss_m3_day:,.0f}", f"{loss_aed_day:,.0f}", zone_row["event_type"], recommended_actions(zone_row)[0]]})

# -----------------------------
# Header
# -----------------------------
now_label = datetime.now().strftime("%I:%M:%S %p")
date_label = datetime.now().strftime("%d %b %Y")
st.markdown(
    f"""
<div class="topbar">
  <div class="logo-card"><img src="data:image/png;base64,{logo_b64}"></div>
  <div class="brand">
    <div class="water-icon">💧</div>
    <div><h1>AquaSmart SEWA</h1><p>Smart Water Monitoring System</p></div>
  </div>
  <div class="status-card"><b>SYSTEM STATUS</b><span class="online-pill">ONLINE</span><br><br>🕘 <b>{now_label}</b><br><span class="small-muted">{date_label}</span></div>
  <div class="alert-summary">🚨 <b>ALERTS ACTIVE</b><span class="alert-big">{len(alert_rows)}</span><br><span style="margin-left:42px;">Critical / Warning</span></div>
</div>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Executive summary
# -----------------------------
top_risk = latest.sort_values("risk_score", ascending=False).iloc[0]
top_reason = "low pressure and abnormal flow increase" if top_risk["pressure_bar"] < 4.2 or top_risk["event_type"] != "Normal" else "higher leakage probability compared with other zones"
st.markdown(f"""
<div class="summary-card">
  <b>Executive Summary:</b> Today’s highest risk zone is <b>{top_risk.zone_name}</b> due to <b>{top_reason}</b>. Recommended immediate action: <b>{recommended_actions(top_risk)[0]}</b>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Mobile field view
# -----------------------------
if mobile_mode:
    st.markdown("## 📱 Field Team View")
    st.caption("Simplified operational screen for field response teams.")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Active Alerts", len(alert_rows))
    with c2:
        st.metric("Avg Response", f"{response_hrs:.1f} hrs")

    for _, r in latest.sort_values("risk_score", ascending=False).iterrows():
        status_class = "critical" if r.system_status == "Critical" else "warning-text" if r.system_status == "Warning" else "normal"
        st.markdown(
            f"""
<div class="mobile-card">
  <div class="zone-name">{r.zone_name} <span class="{status_class}">● {r.system_status}</span></div>
  <div class="small-muted">{r.zone_profile}</div><br>
  <b>Leak probability:</b> {r.leakage_probability:.0%}<br>
  <b>Pressure:</b> {r.pressure_bar:.2f} bar<br>
  <b>Flow:</b> {r.flow_rate_m3h:.1f} m³/h<br>
  <b>Recommended action:</b> {'Dispatch field team and isolate section' if r.system_status == 'Critical' else 'Monitor trend and validate pressure' if r.system_status == 'Warning' else 'Continue normal monitoring'}
</div>
""",
            unsafe_allow_html=True,
        )
    st.stop()

# -----------------------------
# KPI Cards
# -----------------------------
k1, k2, k3, k4, k5 = st.columns(5)
kpis = [
    (k1, "💧", "NRW Loss %", f"{nrw:.1f}%", "↓ 4.6% vs Yesterday", "good"),
    (k2, "⚠️", "Leak Alerts", f"{alerts_count}", "↑ 2 vs Yesterday", "bad"),
    (k3, "🕘", "Avg Response Time", f"{response_hrs:.1f} hrs", "↓ 0.7 hr vs Yesterday", "good"),
    (k4, "⚙️", "System Efficiency", f"{efficiency:.1f}%", "↑ 3.4% vs Yesterday", "good"),
    (k5, "🪙", "Est. Cost Savings (AED)", f"{cost_savings:,.0f}", "This Month", "good"),
]
for col, icon, label, value, change, klass in kpis:
    with col:
        st.markdown(
            f"""
<div class="kpi-card">
  <span class="kpi-icon">{icon}</span><div class="kpi-label">{label}</div>
  <div class="kpi-value">{value}</div>
  <div class="kpi-change {klass}">{change}</div>
</div>
""",
            unsafe_allow_html=True,
        )

# -----------------------------
# Charts and map
# -----------------------------
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
left, center, right = st.columns([1.38, 1.42, .92])

with left:
    st.markdown('<div class="panel-title">Real-Time Trends</div>', unsafe_allow_html=True)
    metric = st.radio("Trend metric", ["Flow Rate", "Pressure", "Consumption"], horizontal=True, label_visibility="collapsed")
    y_col = {"Flow Rate": "flow_rate_m3h", "Pressure": "pressure_bar", "Consumption": "consumption_m3"}[metric]
    fig = go.Figure()
    colors = {"Zubara": "#1890ff", "Mussala": "#ffc226", "Hayawa": "#ff3434", "Al Luluyah": "#21e98a", "Al Wurrayah": "#b970ff"}
    for zone in selected_zones:
        temp = df[df["zone_name"] == zone]
        fig.add_trace(go.Scatter(x=temp["timestamp"], y=temp[y_col], mode="lines", name=zone, line=dict(width=2.5, color=colors.get(zone))))
    fig.update_layout(
        height=415,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(1,20,40,.55)",
        font=dict(color="#ffffff"), margin=dict(l=15, r=15, t=20, b=10),
        legend=dict(orientation="h", y=1.06, font=dict(color="#ffffff")),
        xaxis=dict(gridcolor="rgba(135,205,255,.18)", color="#ffffff", title_font=dict(color="#ffffff"), tickfont=dict(color="#ffffff")), yaxis=dict(gridcolor="rgba(135,205,255,.18)", title=metric, color="#ffffff", title_font=dict(color="#ffffff"), tickfont=dict(color="#ffffff")),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with center:
    st.markdown('<div class="panel-title">Khorfakkan GIS-Style Zone Map</div>', unsafe_allow_html=True)
    map_df = latest.copy()
    color_map = {"Normal": "#27e782", "Warning": "#ffc226", "Critical": "#ff3333"}
    fig_map = go.Figure()
    # Add soft polygon boundaries around each zone. Coordinates are approximate for demo only.
    for _, r in map_df.iterrows():
        lat, lon = float(r.latitude), float(r.longitude)
        dlat = 0.0065 if r.zone_name != "Al Wurrayah" else 0.011
        dlon = 0.0080 if r.zone_name != "Al Wurrayah" else 0.014
        poly_lats = [lat-dlat, lat-dlat/2, lat+dlat/2, lat+dlat, lat+dlat/3, lat-dlat]
        poly_lons = [lon-dlon, lon+dlon/2, lon+dlon, lon+dlon/3, lon-dlon, lon-dlon]
        fig_map.add_trace(go.Scattermapbox(
            lat=poly_lats, lon=poly_lons, mode="lines", fill="toself",
            fillcolor=hex_to_rgba(color_map.get(r.system_status, "#1890ff"), 0.24),
            line=dict(color=color_map.get(r.system_status, "#1890ff"), width=2),
            opacity=.55, hoverinfo="skip", showlegend=False,
        ))
    fig_map.add_trace(go.Scattermapbox(
        lat=map_df["latitude"], lon=map_df["longitude"], mode="markers+text",
        marker=dict(size=(map_df["risk_score"] / 2.5 + 18), color=[color_map[s] for s in map_df["system_status"]], opacity=.90),
        text=map_df["zone_name"], textposition="top center",
        hovertemplate="<b>%{text}</b><br>Status: %{customdata[0]}<br>Leak Probability: %{customdata[1]:.0%}<br>Pressure: %{customdata[2]:.2f} bar<extra></extra>",
        customdata=np.stack([map_df["system_status"], map_df["leakage_probability"], map_df["pressure_bar"]], axis=-1),
        showlegend=False,
    ))
    fig_map.update_layout(
        height=455,
        mapbox=dict(style="open-street-map", center=dict(lat=25.355, lon=56.355), zoom=10.6),
        margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})
    st.markdown("<span class='normal'>● Normal</span>&nbsp;&nbsp;&nbsp; <span class='warning-text'>● Warning</span>&nbsp;&nbsp;&nbsp; <span class='critical'>● Critical</span>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel-title">Alarm Panel</div>', unsafe_allow_html=True)
    if alert_rows.empty:
        st.success("No active alarms. System operating normally.")
    else:
        for _, r in alert_rows.head(3).iterrows():
            warning = r.system_status == "Warning"
            st.markdown(
                f"""
<div class="alarm-card {'warning' if warning else ''}">
  <div class="alarm-level">{'MEDIUM' if warning else 'HIGH'}</div>
  <div class="alarm-title">🚨 {'WARNING - HIGH CONSUMPTION' if warning else 'CRITICAL - POSSIBLE LEAK'}</div>
  <div class="alarm-zone">{r.zone_name}</div>
  <div class="alarm-desc">{r.event_type}: low pressure / high flow pattern</div>
  <div class="alarm-time">{pd.to_datetime(r.timestamp).strftime('%H:%M')}</div>
</div>
""",
                unsafe_allow_html=True,
            )
        st.button("View All Alerts ❯", use_container_width=True)

# -----------------------------
# Status, probability, business simulation
# -----------------------------
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
bottom1, bottom2, bottom3 = st.columns([1.5, .9, 1.35])

with bottom1:
    st.markdown('<div class="panel-title">Zone Status Overview</div>', unsafe_allow_html=True)
    z = latest.copy().sort_values("risk_score", ascending=False)
    rows_html = "".join(
        f"""
<div class="zone-card">
  <div class="zone-name">{r.zone_name}</div>
  <div class="{'critical' if r.system_status=='Critical' else 'warning-text' if r.system_status=='Warning' else 'normal'}">● {r.system_status.upper()}</div>
  <div class="small-muted">Pressure: <b>{r.pressure_bar:.2f} bar</b></div>
  <div class="small-muted">Flow: <b>{r.flow_rate_m3h:.1f} m³/h</b></div>
  <div class="small-muted">Leak Probability: <b>{r.leakage_probability:.0%}</b></div>
</div>
""" for _, r in z.iterrows()
    )
    st.markdown(f"<div class='zone-grid'>{rows_html}</div>", unsafe_allow_html=True)

with bottom2:
    st.markdown('<div class="panel-title">Leakage Probability (%)</div>', unsafe_allow_html=True)
    fig_pie = go.Figure(go.Pie(
        labels=latest["zone_name"], values=latest["leakage_probability"], hole=.55,
        marker=dict(colors=[colors.get(x, "#888") for x in latest["zone_name"]]),
        textinfo="label+percent",
    ))
    fig_pie.update_layout(height=295, paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8fbff"), margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

with bottom3:
    st.markdown('<div class="panel-title">Before vs After Simulation</div>', unsafe_allow_html=True)
    before_after = pd.DataFrame({
        "Metric": ["NRW Loss %", "Average Response Time", "System Efficiency", "Annual Cost (AED)", "Customer Complaints"],
        "Before": ["28.6%", "4.2 hrs", "68.1%", "4.8M", "125 / month"],
        "After": [f"{nrw:.1f}%", f"{response_hrs:.1f} hrs", f"{efficiency:.1f}%", "3.2M", "62 / month"],
        "Improvement": ["↓ 25-36%", "↓ 55-64%", "↑ 15-20%", "↓ 1.6M", "↓ 50%"],
    })
    st.dataframe(before_after, use_container_width=True, hide_index=True)

# -----------------------------
# Zone detail page and operational response
# -----------------------------
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
st.markdown('<div class="panel-title">Zone Detail Page, Recommended Actions & Financial Impact</div>', unsafe_allow_html=True)
zone_row_df = latest[latest["zone_name"] == selected_detail_zone]
if zone_row_df.empty:
    zone_row_df = latest.sort_values("risk_score", ascending=False).head(1)
zone_row = zone_row_df.iloc[0]
asset = ASSET_REGISTER.get(zone_row["zone_name"], {})
supply = SUPPLY_PROFILE.get(zone_row["zone_name"], {})
loss_m3_day, loss_aed_day = estimate_losses(zone_row)
zone_history = df[(df["zone_name"] == zone_row["zone_name"]) & (df["system_status"].isin(["Warning", "Critical"]))].sort_values("timestamp", ascending=False).head(6).copy()
zcol1, zcol2, zcol3 = st.columns([1.0, 1.05, 1.05])
with zcol1:
    st.markdown(f"""
<div class="detail-card">
  <h3 style="margin-top:0;color:white;">{zone_row.zone_name}</h3>
  <b>Status:</b> <span class="{'critical' if zone_row.system_status=='Critical' else 'warning-text' if zone_row.system_status=='Warning' else 'normal'}">● {zone_row.system_status}</span><br>
  <b>Pressure:</b> {zone_row.pressure_bar:.2f} bar &nbsp; <span class="small-muted">Suggested: {supply.get('suggested_pressure_bar','N/A')}</span><br>
  <b>Flow:</b> {zone_row.flow_rate_m3h:.1f} m³/h &nbsp; <span class="small-muted">Supply target: {supply.get('suggested_flow_m3h','N/A')}</span><br>
  <b>Supply pressure:</b> {supply.get('supply_pressure_bar','N/A')} bar<br>
  <b>Supply flow:</b> {supply.get('supply_flow_m3h','N/A')} m³/h<br>
  <b>Consumption:</b> {zone_row.consumption_m3:,.0f} m³<br>
  <b>Leak probability:</b> {zone_row.leakage_probability:.0%}<br>
  <b>Last alert:</b> {zone_row.event_type}
</div>
""", unsafe_allow_html=True)
with zcol2:
    st.markdown("<div class='detail-card'><b>Recommended Action Panel</b><br><br>", unsafe_allow_html=True)
    for action in recommended_actions(zone_row):
        st.markdown(f"<div class='action-card'>✅ {action}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
with zcol3:
    st.markdown(f"""
<div class="detail-card">
  <b>Asset Information</b><br><br>
  <b>Pipe material:</b> {asset.get('pipe_material','N/A')}<br>
  <b>Pipe diameter:</b> {asset.get('diameter_mm','N/A')} mm<br>
  <b>Estimated pipe age:</b> {asset.get('pipe_age','N/A')}<br>
  <b>Critical customers:</b> {asset.get('critical_customers','N/A')}<br>
  <b>Nearby tanks/stations:</b> {asset.get('nearby_assets','N/A')}
</div>
""", unsafe_allow_html=True)
hcol1, hcol2 = st.columns([1.15, .85])
with hcol1:
    st.markdown('<div class="panel-title">Leak History</div>', unsafe_allow_html=True)
    if zone_history.empty:
        st.info("No recent leak warnings for this zone.")
    else:
        hist = zone_history[["timestamp", "zone_name", "event_type", "system_status", "pressure_bar", "flow_rate_m3h"]].copy()
        hist["status"] = ["Open", "Assigned", "Site Inspection", "Closed", "Open", "Assigned"][:len(hist)]
        hist["timestamp"] = pd.to_datetime(hist["timestamp"]).dt.strftime("%d %b %Y %H:%M")
        hist = hist.rename(columns={"timestamp":"Date / Time", "zone_name":"Zone", "event_type":"Alert", "system_status":"Severity", "pressure_bar":"Pressure", "flow_rate_m3h":"Flow"})
        st.dataframe(hist, use_container_width=True, hide_index=True)
with hcol2:
    st.markdown('<div class="panel-title">Financial Impact</div>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="detail-card">
  <b>Estimated water loss:</b><br><span style="font-size:1.8rem;font-weight:900;color:white;">{loss_m3_day:,.0f} m³/day</span><br><br>
  <b>Estimated impact:</b><br><span style="font-size:1.8rem;font-weight:900;color:#35ccff;">AED {loss_aed_day:,.0f}/day</span><br>
  <span class="small-muted">Synthetic estimate based on flow and leak probability. Unit value assumed AED {AED_PER_M3:.2f}/m³.</span>
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="panel-title">Team Response Workflow</div>', unsafe_allow_html=True)
st.markdown("""
<div class="workflow">
  <div class="workflow-step">1. Alert Received</div><div class="workflow-arrow">→</div>
  <div class="workflow-step">2. Assigned Team</div><div class="workflow-arrow">→</div>
  <div class="workflow-step">3. Site Inspection</div><div class="workflow-arrow">→</div>
  <div class="workflow-step">4. Repair / PRV Check</div><div class="workflow-arrow">→</div>
  <div class="workflow-step">5. Closed & Verified</div>
</div>
""", unsafe_allow_html=True)
zone_report = make_zone_report(zone_row)

st.markdown("<div class='footer'>AquaSmart SEWA – Real-Time Water Network Intelligence &nbsp;&nbsp; | &nbsp;&nbsp; Building a Sustainable Water Future for Sharjah &nbsp;&nbsp; | &nbsp;&nbsp; © 2026 SEWA Demo</div>", unsafe_allow_html=True)

# -----------------------------
# Downloads
# -----------------------------
with st.expander("📦 Export demo files"):
    st.download_button("Download latest synthetic CSV", df.to_csv(index=False).encode("utf-8"), file_name="aquasmart_scada_snapshot.csv", mime="text/csv")
    st.download_button("Download selected zone daily summary report", zone_report.to_csv(index=False).encode("utf-8"), file_name=f"aquasmart_{zone_row.zone_name.replace(' ', '_')}_daily_summary.csv", mime="text/csv")
    if PPT_PATH.exists():
        st.download_button("Download executive PowerPoint", PPT_PATH.read_bytes(), file_name="AquaSmart_SEWA_Executive_Pitch.pptx", mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")
    st.caption("All values are synthetic and intended for prototype demonstration only.")
