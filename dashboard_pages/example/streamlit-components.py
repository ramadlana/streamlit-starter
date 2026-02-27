import plotly.express as px
import altair as alt
import streamlit as st
import pandas as pd
import numpy as np
import time

st.set_page_config(layout="wide")
st.title("Streamlit All-in-One Playground")

# ---- UI SAFETY: show toast once per session ----
if "boot_toast" not in st.session_state:
    st.toast("Welcome to the Playground")
    st.session_state.boot_toast = True

# ---- UI SAFETY: force scroll to top on first paint (optional) ----
st.markdown("""
<script>
document.addEventListener("DOMContentLoaded", () => window.scrollTo(0, 0));
</script>
""", unsafe_allow_html=True)

# =========================
# TEXT & MARKDOWN
# =========================
st.header("Text & Markdown")
st.write("st.write / magic markdown")
st.markdown("**Bold**, _italic_, `code`")
st.caption("Caption text")
st.code("print('hello world')", language="python")
st.latex(r"\int_0^\infty e^{-x} dx = 1")

# =========================
# STATUS & FEEDBACK (on-demand)
# =========================
st.header("Status & Feedback")
st.success("Success")
st.warning("Warning")
st.error("Error")
st.info("Info")

if st.button("Run Status Demo"):
    with st.spinner("Loading..."):
        time.sleep(0.3)
    with st.status("Running job...", expanded=False):
        time.sleep(0.3)

# =========================
# LAYOUT
# =========================
st.header("Layout")
c1, c2, c3 = st.columns(3)
c1.write("Column 1")
c2.write("Column 2")
c3.write("Column 3")

t1, t2 = st.tabs(["Tab A", "Tab B"])
with t1:
    st.write("Tab A content")
    st.write("Lorem ipsum dolor sit amet...")
with t2:
    st.write("Tab B content")
    st.write("Lorem ipsum dolor sit amet...")

with st.expander("Expander"):
    st.write("Hidden content")

with st.popover("Popover"):
    st.button("Quick action")

with st.container(border=True):
    st.write("Bordered container")

# =========================
# INPUT WIDGETS
# =========================
st.header("Input Widgets")
st.text_input("Text input")
st.text_area("Text area")
st.number_input("Number input", 0, 100, 10)
st.slider("Slider", 0, 100, 20)
st.checkbox("Checkbox")
st.toggle("Toggle")
st.radio("Radio", ["A", "B", "C"], horizontal=True)
st.selectbox("Selectbox", ["One", "Two", "Three"])
st.multiselect("Multiselect", ["infra", "network", "linux", "cloud"])
st.date_input("Date input")
st.time_input("Time input")
st.button("Button")

# =========================
# FORMS
# =========================
st.header("Forms")
with st.form("demo_form", clear_on_submit=True):
    f_name = st.text_input("Name")
    f_email = st.text_input("Email")
    f_role = st.selectbox("Role", ["Admin", "User", "Viewer"])
    submitted = st.form_submit_button("Submit")
if submitted:
    st.success({"name": f_name, "email": f_email, "role": f_role})

# =========================
# DATAFRAME & TABLE
# =========================
st.header("DataFrame & Table")
df = pd.DataFrame(
    {"a": [1, 2, 3, 4], "b": [10, 20, 30, 40], "c": [1, 2, 3, 4]})
st.dataframe(df, use_container_width=True)
st.table(df)
sty = pd.DataFrame(np.random.randn(10, 5), columns=list("abcde"))
st.dataframe(sty.style.highlight_max(axis=0))

# =========================
# METRICS
# =========================
st.header("Metrics")
m1, m2, m3 = st.columns(3)
m1.metric("CPU", "42%", "+3%")
m2.metric("RAM", "6.2 GB", "-0.4 GB")
m3.metric("Disk", "71%", "+1%")

# =========================
# CHARTS (on-demand)
# =========================
st.header("Charts")

if st.toggle("Show Charts"):
    chart_data = pd.DataFrame(np.random.randn(30, 4), columns=list("abcd"))
    st.line_chart(chart_data)
    st.bar_chart(chart_data)
    st.area_chart(chart_data)
    st.scatter_chart(chart_data)

    pie_df = pd.DataFrame({
        "label": ["Network", "Infra", "Cloud", "Linux"],
        "value": [40, 25, 20, 15],
    })

    pie = alt.Chart(pie_df).mark_arc().encode(
        theta=alt.Theta(field="value", type="quantitative"),
        color=alt.Color(field="label", type="nominal"),
        tooltip=["label", "value"]
    )

    donut = alt.Chart(pie_df).mark_arc(innerRadius=70).encode(
        theta=alt.Theta(field="value", type="quantitative"),
        color=alt.Color(field="label", type="nominal"),
        tooltip=["label", "value"]
    )

    st.subheader("Pie Chart")
    st.altair_chart(pie, use_container_width=True)

    st.subheader("Donut Chart")
    st.altair_chart(donut, use_container_width=True)

    radar_df = pd.DataFrame({
        "metric": ["CPU", "RAM", "Disk", "IO", "Net"],
        "value": [70, 55, 80, 60, 65],
    })
    radar = px.line_polar(radar_df, r="value", theta="metric", line_close=True)
    st.subheader("Radar Chart")
    st.plotly_chart(radar, use_container_width=True)

    heat_df = pd.DataFrame(np.random.randn(10, 10))
    heat = px.imshow(heat_df)
    st.subheader("Heatmap")
    st.plotly_chart(heat, use_container_width=True)

# =========================
# MAP (on-demand)
# =========================
st.header("Map")
if st.toggle("Show Map"):
    map_df = pd.DataFrame({"lat": [-6.2, -7.25], "lon": [106.8, 112.75]})
    st.map(map_df)

# =========================
# FILE UPLOAD / DOWNLOAD
# =========================
st.header("File Upload / Download")
up = st.file_uploader("Upload CSV", type=["csv"])
if up:
    udf = pd.read_csv(up)
    st.dataframe(udf, use_container_width=True)
st.download_button("Download sample CSV", df.to_csv(index=False), "sample.csv")

# =========================
# MEDIA (on-demand)
# =========================
st.header("Media")
if st.toggle("Show Media"):
    st.image("https://picsum.photos/600/200")
    st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
    st.camera_input("Camera input")

# =========================
# CHAT UI
# =========================
st.header("Chat UI")
if "msgs" not in st.session_state:
    st.session_state.msgs = []
for m in st.session_state.msgs:
    with st.chat_message(m["role"]):
        st.write(m["content"])
msg = st.chat_input("Type a message")
if msg:
    st.session_state.msgs.append({"role": "user", "content": msg})
    st.session_state.msgs.append(
        {"role": "assistant", "content": "Echo: " + msg})

# =========================
# PROGRESS (on-demand)
# =========================
st.header("Progress")
if st.button("Run Progress Demo"):
    ph = st.empty()
    p = st.progress(0)
    for i in range(1, 6):
        time.sleep(0.1)
        ph.write(f"Step {i}/5")
        p.progress(i * 20)

# =========================
# SESSION STATE
# =========================
st.header("Session State")
st.text_input("Your name", key="name")
st.write("Hello", st.session_state.get("name"))
if st.button("Reset name"):
    st.session_state.pop("name", None)
    st.rerun()

# =========================
# HTML / EXCEPTION
# =========================
# st.header("HTML & Exception")
# st.html("<b>Custom HTML (limited)</b>")
# try:
#     1 / 0
# except Exception as e:
#     st.exception(e)

# =========================
# DEBUG
# =========================
st.header("Debug display")
st.json(st.session_state)
