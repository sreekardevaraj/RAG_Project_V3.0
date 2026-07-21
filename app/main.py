import streamlit as st
import sys, os, tempfile
import Data

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.rag_pipeline import build_rag_pipeline, ask_question
from backend.export import export_chat_to_pdf
from config.settings import RAW_PDF_DIR

st.set_page_config(page_title="RAG Chatbot V2", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #f0f4ff 0%, #fafafa 100%); color: #1e1e2e; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%); box-shadow: 4px 0 20px rgba(0,0,0,0.15); }
    [data-testid="stSidebar"] * { color: #e0e7ff !important; }
    [data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 { color: #ffffff !important; }
    [data-testid="stChatMessage"] { background:#ffffff; border-radius:16px; border:1px solid #e5e7eb; padding:6px 10px; margin-bottom:10px; box-shadow:0 2px 8px rgba(0,0,0,0.06); }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { background:linear-gradient(135deg,#ede9fe,#ddd6fe); border:1px solid #c4b5fd; }
    .badge-pdf     { background:linear-gradient(135deg,#059669,#10b981); color:white; padding:4px 14px; border-radius:20px; font-size:12px; font-weight:600; display:inline-block; margin-bottom:8px; }
    .badge-web     { background:linear-gradient(135deg,#2563eb,#3b82f6); color:white; padding:4px 14px; border-radius:20px; font-size:12px; font-weight:600; display:inline-block; margin-bottom:8px; }
    .badge-chat    { background:linear-gradient(135deg,#d97706,#f59e0b); color:white; padding:4px 14px; border-radius:20px; font-size:12px; font-weight:600; display:inline-block; margin-bottom:8px; }
    .badge-analyst { background:linear-gradient(135deg,#7c3aed,#8b5cf6); color:white; padding:4px 14px; border-radius:20px; font-size:12px; font-weight:600; display:inline-block; margin-bottom:8px; }
    .status-ready     { background:linear-gradient(135deg,#059669,#10b981); color:white; padding:6px 16px; border-radius:20px; font-size:13px; font-weight:600; display:inline-block; }
    .status-not-ready { background:linear-gradient(135deg,#dc2626,#ef4444); color:white; padding:6px 16px; border-radius:20px; font-size:13px; font-weight:600; display:inline-block; }
    [data-testid="stSidebar"] .stButton button { background:linear-gradient(135deg,#6366f1,#818cf8) !important; color:white !important; border:none; border-radius:10px; font-weight:600; width:100%; box-shadow:0 4px 12px rgba(99,102,241,0.4); }
    .ref-box { background:#f8fafc; border-left:3px solid #6366f1; padding:8px 14px; border-radius:6px; font-size:12px; color:#475569; margin-top:6px; }
    .followup-box { background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:14px; margin-top:10px; }
    .followup-title { font-size:13px; font-weight:600; color:#475569; margin-bottom:8px; }
    .info-card { background:rgba(255,255,255,0.1); border-radius:10px; padding:12px 14px; margin-top:8px; border:1px solid rgba(255,255,255,0.15); }
    .step { background:rgba(255,255,255,0.08); border-radius:8px; padding:8px 12px; margin:4px 0; font-size:13px; border-left:3px solid #818cf8; }
    .welcome-card { background:white; border-radius:20px; padding:50px 30px; text-align:center; border:1px solid #e5e7eb; box-shadow:0 4px 20px rgba(0,0,0,0.06); margin:40px auto; max-width:560px; }
    hr { border-color:#e5e7eb; margin:12px 0; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────
for key, val in {"messages": [], "pipeline": None, "pipeline_ready": False, "pending_followup": None}.items():
    if key not in st.session_state:
        st.session_state[key] = val

def render_badge(source):
    badges = {
        "PDF":     '<span class="badge-pdf">📄 PDF Source</span>',
        "Web":     '<span class="badge-web">🌐 Web Source</span>',
        "Chat":    '<span class="badge-chat">💬 Chat</span>',
        "Analyst": '<span class="badge-analyst">🧠 Analyst</span>',
    }
    html = badges.get(source, "")
    if html:
        st.markdown(html, unsafe_allow_html=True)

def render_references(details, source):
    if not details:
        return
    with st.expander("📎 References"):
        for item in details:
            if source == "PDF":
                st.markdown(f'<div class="ref-box">📄 Page {item.get("page","?")} | {os.path.basename(str(item.get("source","?")))}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ref-box">🌐 <a href="{item.get("url","")}" target="_blank" style="color:#4f46e5;text-decoration:none;">{item.get("title","Link")}</a></div>', unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 RAG Chatbot V2")
    st.markdown("*LangGraph · Multi-Agent · Groq*")
    st.markdown("---")

    st.markdown("### 📊 Status")
    if st.session_state["pipeline_ready"]:
        st.markdown('<span class="status-ready">✅ Pipeline Ready</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-not-ready">❌ Not Loaded</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📄 Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"], label_visibility="collapsed")
    if uploaded_file:
        os.makedirs(RAW_PDF_DIR, exist_ok=True)
        save_path = os.path.join(RAW_PDF_DIR, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ {uploaded_file.name} uploaded!")

    st.markdown("---")
    st.markdown("### ⚙️ Controls")
    force_rebuild = st.toggle("🔄 Force Rebuild Index", value=False)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Load Pipeline", use_container_width=True):
        with st.spinner("Building LangGraph pipeline..."):
            try:
                pipeline = build_rag_pipeline(force_rebuild=force_rebuild)
                st.session_state["pipeline"]       = pipeline
                st.session_state["pipeline_ready"] = True
                st.success("✅ LangGraph Ready!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state["messages"] = []
        if st.session_state.get("pipeline"):
            st.session_state["pipeline"]["memory"].clear()
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state["messages"]:
        if st.button("📥 Export Chat as PDF", use_container_width=True):
            with st.spinner("Exporting..."):
                try:
                    tmp_path = os.path.join(tempfile.gettempdir(), "chat_export.pdf")
                    export_chat_to_pdf(st.session_state["messages"], tmp_path)
                    with open(tmp_path, "rb") as f:
                        st.download_button("⬇️ Download Chat PDF", data=f.read(), file_name="rag_chat_export.pdf", mime="application/pdf", use_container_width=True)
                except Exception as e:
                    st.error(f"Export error: {e}")

    st.markdown("---")
    st.markdown("### 🤖 LangGraph Agents")
    st.markdown("""
    <div class="info-card">
        <p>🎯 <b>Supervisor Node</b> — Routes query</p>
        <p>📄 <b>RAG Node</b> — Answers from PDF</p>
        <p>🌐 <b>Web Node</b> — Live web search</p>
        <p>🧠 <b>Analyst Node</b> — Deep analysis</p>
        <p>💬 <b>Casual Node</b> — Small talk</p>
        <p>💡 <b>Followup Node</b> — Suggests questions</p>
        <p>🧠 <b>Memory Node</b> — Saves history</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 💡 Try These")
    st.markdown("""
    <div class="step">Summarize the document</div>
    <div class="step">Compare RAG vs Fine-tuning</div>
    <div class="step">Generate 5 quiz questions</div>
    <div class="step">Latest news about OpenAI</div>
    <div class="step">What is LangChain?</div>
    <div class="step">Who won IPL 2024?</div>
    """, unsafe_allow_html=True)

# ── Main Area ─────────────────────────────────────────────────────────
st.markdown("# 🤖 RAG Chatbot V2")
st.markdown("##### LangGraph Multi-Agent AI — PDF · Web · Analyst · Memory · Follow-ups")
st.markdown("---")

if not st.session_state["messages"]:
    st.markdown("""
    <div class="welcome-card">
        <div style="font-size:56px;margin-bottom:16px;">🤖</div>
        <div style="font-size:22px;font-weight:700;color:#1e1e2e;margin-bottom:8px;">RAG Chatbot V2</div>
        <div style="font-size:14px;color:#6b7280;margin-bottom:8px;">Powered by LangGraph Multi-Agent Architecture</div>
        <div style="font-size:13px;color:#9ca3af;margin-bottom:24px;line-height:1.8;">
            Ask about your PDF · Search the web · Analyze documents<br>
            Chat memory · Follow-up suggestions · Export chat
        </div>
        <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;">
            <span style="background:#ecfdf5;color:#059669;padding:5px 12px;border-radius:20px;font-size:12px;font-weight:600;">📄 RAG</span>
            <span style="background:#eff6ff;color:#2563eb;padding:5px 12px;border-radius:20px;font-size:12px;font-weight:600;">🌐 Web</span>
            <span style="background:#faf5ff;color:#7c3aed;padding:5px 12px;border-radius:20px;font-size:12px;font-weight:600;">🧠 Analyst</span>
            <span style="background:#fffbeb;color:#d97706;padding:5px 12px;border-radius:20px;font-size:12px;font-weight:600;">💬 Memory</span>
            <span style="background:#fdf2f8;color:#db2777;padding:5px 12px;border-radius:20px;font-size:12px;font-weight:600;">💡 Follow-ups</span>
        </div>
    </div>""", unsafe_allow_html=True)

# ── Chat History ──────────────────────────────────────────────────────
for i, msg in enumerate(st.session_state["messages"]):
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            render_badge(msg.get("source", ""))
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            render_references(msg.get("details", []), msg.get("source", ""))
            if msg.get("followups"):
                st.markdown('<div class="followup-box"><div class="followup-title">💡 Suggested follow-up questions:</div>', unsafe_allow_html=True)
                for fq in msg["followups"]:
                    if st.button(f"➤ {fq}", key=f"fq_{i}_{fq[:25]}"):
                        st.session_state["pending_followup"] = fq
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

# ── Process follow-up click ───────────────────────────────────────────
if st.session_state["pending_followup"]:
    pending = st.session_state["pending_followup"]
    st.session_state["pending_followup"] = None
    st.session_state["messages"].append({"role": "user", "content": pending})
    with st.chat_message("user"):
        st.markdown(pending)
    with st.chat_message("assistant"):
        with st.spinner("🧠 Thinking..."):
            try:
                resp = ask_question(st.session_state["pipeline"], pending)
                render_badge(resp["source"])
                st.markdown(resp["answer"])
                render_references(resp["details"], resp["source"])
                st.session_state["messages"].append({"role": "assistant", "content": resp["answer"], "source": resp["source"], "details": resp["details"], "followups": resp["followups"]})
            except Exception as e:
                st.error(f"❌ {e}")

# ── Chat Input ────────────────────────────────────────────────────────
user_input = st.chat_input("💬 Ask about your PDF, request analysis, or anything else...")

if user_input:
    if not st.session_state["pipeline_ready"]:
        st.warning("⚠️ Click **Load Pipeline** in the sidebar first!")
        st.stop()

    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("🧠 LangGraph thinking..."):
            try:
                resp = ask_question(st.session_state["pipeline"], user_input)
                render_badge(resp["source"])
                st.markdown(resp["answer"])
                render_references(resp["details"], resp["source"])
                if resp.get("followups"):
                    st.markdown('<div class="followup-box"><div class="followup-title">💡 Suggested follow-up questions:</div>', unsafe_allow_html=True)
                    for fq in resp["followups"]:
                        if st.button(f"➤ {fq}", key=f"inp_{fq[:25]}"):
                            st.session_state["pending_followup"] = fq
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                st.session_state["messages"].append({"role": "assistant", "content": resp["answer"], "source": resp["source"], "details": resp["details"], "followups": resp["followups"]})
            except Exception as e:
                err = f"❌ Error: {str(e)}"
                st.error(err)
                st.session_state["messages"].append({"role": "assistant", "content": err, "source": "", "details": [], "followups": []})