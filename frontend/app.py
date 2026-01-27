import uuid
import time
import requests
import streamlit as st

# ---------------- CONFIG ----------------
BACKEND_URL = "http://127.0.0.1:8000"
API_KEY = st.secrets.get("API_KEY", "")

HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY,
}

METRICS_POLL_SEC = 5

# ---------------- HELPERS ----------------
def backend_health():
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=2)
        return r.status_code == 200
    except Exception:
        return False

def backend_ready():
    try:
        r = requests.get(f"{BACKEND_URL}/ready", timeout=2)
        return r.status_code == 200
    except Exception:
        return False

def send_chat(message: str):
    payload = {
        "message": message,
        "conversation_id": st.session_state.conversation_id,
        "user_mode": st.session_state.user_mode,
        "privacy_mode": st.session_state.privacy_mode,
        "metadata": {}
    }
    r = requests.post(
        f"{BACKEND_URL}/chat",
        json=payload,
        headers=HEADERS,
        timeout=300
    )
    return r

def fetch_metrics():
    try:
        r = requests.get(f"{BACKEND_URL}/metrics", timeout=2)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

# ---------------- SESSION STATE ----------------
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []  # UI-only

if "privacy_mode" not in st.session_state:
    st.session_state.privacy_mode = "strict"

if "user_mode" not in st.session_state:
    st.session_state.user_mode = "auto"

if "metrics_cache" not in st.session_state:
    st.session_state.metrics_cache = {}

if "last_metrics_ts" not in st.session_state:
    st.session_state.last_metrics_ts = 0.0


now = time.time()
if now - st.session_state.last_metrics_ts > METRICS_POLL_SEC:
    metrics = fetch_metrics()
    if metrics is not None:
        st.session_state.metrics_cache = metrics
        st.session_state.last_metrics_ts = now


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Hybrid AI Chatbot",
    layout="wide",
)

# ---------------- HEADER ----------------
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    st.title("🤖 CychoB0T - Hybrid AI Chatbot")

with col2:
    st.caption("Backend")
    if backend_health():
        st.success("Healthy")
    else:
        st.error("Down")

with col3:
    st.caption("Engine")
    if backend_ready():
        st.success("Ready")
    else:
        st.warning("Warming up")

st.divider()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Controls")

    st.subheader("Conversation")
    st.text_input(
        "Conversation ID",
        value=st.session_state.conversation_id,
        disabled=True
    )

    if st.button("New Conversation"):
        st.session_state.conversation_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.subheader("Modes")

    st.session_state.privacy_mode = st.radio(
        "Privacy Mode",
        ["strict", "standard", "off"],
        index=["strict", "standard", "off"].index(st.session_state.privacy_mode)
    )

    st.session_state.user_mode = st.radio(
        "User Mode",
        ["auto", "offline_only"],
        index=["auto", "offline_only"].index(st.session_state.user_mode)
    )

    st.divider()

    st.subheader("Metrics")


    m = requests.get(f"{BACKEND_URL}/metrics").json()

    gauges = m.get("gauges", {})
    counters = m.get("counters", {})

    backend_mode = gauges.get("offline_backend_mode", 0)
    mode = "emb" if backend_mode == 1 else "ser"

    c1, c2, c3 = st.columns(3)

    c1.metric("Backend", mode)

    c2.metric(
        "Concurrency",
        f'{gauges.get("offline_inflight", 0)}/'
        f'{gauges.get("offline_concurrency_limit", 0)}'
    )

    c3.metric(
        "Busy rejects",
        counters.get("offline_model_busy", 0)
    )

    st.caption(
        f'Requests: `{counters.get("offline_requests_total", 0)}` • '
        f'Rejected: `{counters.get("errors_total", 0)}`'
    )

    st.caption(
        f'Offline: `{counters.get("engine_offline", 0)}` • '
        f'Online: `{counters.get("engine_online", 0)}`'
    )

    metrics = st.session_state.metrics_cache

    if metrics:
        counters = metrics.get("counters", {})
        timers = metrics.get("timers", {})
        latency = timers.get("latency_ms", {})

        st.caption(
            f'p50: `{latency.get("p50", 0)}` • '
            f'p95: `{latency.get("p95", 0)}`'
        )
    else:
        st.caption("Metrics unavailable")

    st.caption("Metrics refresh every 5s")

    st.divider()

    st.subheader("System")
    st.caption("RAG: display-only (backend-controlled)")
    st.caption("Metrics refresh: every 5s")

# ---------------- MAIN CHAT PANEL ----------------
st.subheader("💬 Chat")

# Render existing UI messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("meta"):
            st.caption(f"{msg['meta']}")

# Chat input
user_input = st.chat_input(
    "Type your message...",
    disabled=st.session_state.get("generating", False)
)

if user_input is not None and user_input.strip():
    # Append user message (UI-only)
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Call backend
    with st.chat_message("assistant"):
        status = st.status("Generating response…", expanded=False)
        placeholder = st.empty()
        full_text = ""

        st.session_state.generating = True

        try:
            r = send_chat(user_input)

            if r.status_code != 200:
                if r.status_code == 503:
                    placeholder.warning(
                        "The offline model is currently unreachable. "
                        "Please wait a few seconds and try again."
                    )
                elif r.status_code == 429:
                    placeholder.warning("Too many requests. Slow down.")
                else:
                    placeholder.error(f"Error {r.status_code}")

                status.update(label="Generation failed", state="error")

            else:
                data = r.json()
                text = data.get("text", "")
                engine = data.get("engine", "unknown")
                latency = data.get("latency_ms", 0)

                #  Simulated streaming
                for token in text.split(" "):
                    full_text += token + " "
                    placeholder.markdown(full_text)
                    time.sleep(0.02)

                status.update(label="Response complete", state="complete")
                st.caption(f"engine: {engine} • latency: {latency} ms")

                # Persist assistant message (UI-only)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": text,
                    "meta": f"engine: {engine} • latency: {latency} ms"
                })

        except requests.exceptions.Timeout:
            placeholder.error("Request timed out")
        except Exception as e:
            placeholder.error("Unexpected error")

        finally:
            st.session_state.generating = False
