import streamlit as st
import time
from engine import SynthosEngine
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Synthos - AI Boardroom", layout="wide")
st.title("🎙️ Synthos: AI Boardroom Debate")
st.caption("Real‑time multi‑expert debate with mediator consensus")

# Sidebar for API key and model
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("GROQ API Key", type="password", value=os.getenv("GROQ_API_KEY", ""))
    model = st.selectbox("Model", ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"])
    if st.button("Reset Debate", key="reset"):
        st.session_state.messages = []
        st.session_state.debate_complete = False
        st.rerun()

# Main input
topic = st.text_input("Topic", placeholder="e.g., Implement AI Agent Calling for customer support")
constraints = st.text_area("Constraints (optional)", placeholder="GDPR compliance, budget under $50k")

# Container for live debate
debate_container = st.container()

# Store messages in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "debate_complete" not in st.session_state:
    st.session_state.debate_complete = False

def on_message(speaker, round_num, text):
    """Callback to add message to session state and update UI."""
    st.session_state.messages.append({
        "speaker": speaker,
        "round": round_num,
        "text": text,
        "timestamp": time.time()
    })
    # Force UI update
    with debate_container:
        for msg in st.session_state.messages:
            round_name = {0: "System", 1: "Opening", 2: "Cross‑exam", 3: "Refinement", 4: "Mediator"}.get(msg["round"], "")
            st.markdown(f"**{msg['speaker']}** ({round_name})")
            st.write(msg["text"])
            st.divider()
    time.sleep(0.5)  # slight pause to simulate real-time

# Single Start Debate button with key
if st.button("Start Debate", type="primary", key="start"):
    if not topic:
        st.warning("Please enter a topic.")
    elif not api_key:
        st.warning("Please enter your GROQ API key in the sidebar.")
    else:
        st.session_state.messages = []
        st.session_state.debate_complete = False
        engine = SynthosEngine(api_key=api_key, model=model, provider="groq")
        with st.spinner("Debate in progress..."):
            result_md = engine.run(topic, constraints, on_message=on_message)
        st.session_state.debate_complete = True
        st.success("Debate concluded!")
        st.markdown("## Final Consensus")
        st.markdown(result_md)
        # Option to download transcript
        st.download_button("Download Transcript (Markdown)", result_md, file_name="synthos_debate.md", key="download")