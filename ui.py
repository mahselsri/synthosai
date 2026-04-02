import streamlit as st
import time
from engine import SynthosEngine
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Synthos - AI Boardroom", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for elegant UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .subheader {
        color: #555;
        margin-top: 0;
        font-style: italic;
    }
    .message-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #2a5298;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .speaker-name {
        font-weight: bold;
        color: #1e3c72;
    }
    .round-badge {
        background-color: #2a5298;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.7rem;
        display: inline-block;
        margin-left: 10px;
    }
    .timestamp {
        color: #999;
        font-size: 0.7rem;
        margin-left: 10px;
    }
    .stButton button {
        background-color: #2a5298;
        color: white;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #1e3c72;
    }
    .scorecard-table {
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🎙️ Synthos</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">AI Boardroom Debate — Real‑time multi‑expert discussion with mediator consensus</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/meeting-room.png", width=80)
    st.header("⚙️ Configuration")
    api_key = st.text_input("GROQ API Key", type="password", value=os.getenv("GROQ_API_KEY", ""))
    model = st.selectbox("Model", ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"])
    debate_speed = st.slider("Debate Speed (seconds between messages)", 0.5, 3.0, 1.0, 0.5)
    if st.button("🔄 Reset Debate", key="reset", use_container_width=True):
        st.session_state.messages = []
        st.session_state.debate_complete = False
        st.session_state.current_placeholder = None
        st.rerun()

# Main input area
col1, col2 = st.columns([3, 1])
with col1:
    topic = st.text_input("📌 Topic", placeholder="e.g., Implement AI Agent Calling for customer support")
with col2:
    constraints = st.text_area("📋 Constraints (optional)", placeholder="GDPR compliance, budget under $50k", height=68)

# Placeholder for live debate stream
debate_placeholder = st.empty()
scorecard_placeholder = st.empty()

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "debate_complete" not in st.session_state:
    st.session_state.debate_complete = False
if "current_placeholder" not in st.session_state:
    st.session_state.current_placeholder = None

def on_message(speaker, round_num, text):
    """Callback to add message with streaming effect."""
    # Create a temporary placeholder for typing animation
    temp_placeholder = debate_placeholder.empty()
    # Show typing indicator
    with temp_placeholder.container():
        st.markdown(f"<div class='message-container'><span class='speaker-name'>{speaker}</span> <span class='round-badge'>Round {round_num if round_num>0 else 'System'}</span><span class='timestamp'>typing...</span><br><i>thinking...</i></div>", unsafe_allow_html=True)
    time.sleep(0.3)  # short pause to simulate typing
    
    # Append to session state
    st.session_state.messages.append({
        "speaker": speaker,
        "round": round_num,
        "text": text,
        "timestamp": time.time()
    })
    
    # Clear temporary placeholder
    temp_placeholder.empty()
    
    # Redraw all messages with new one
    with debate_placeholder.container():
        for msg in st.session_state.messages:
            round_label = {0: "System", 1: "Opening", 2: "Cross‑exam", 3: "Refinement", 4: "Mediator"}.get(msg["round"], "")
            st.markdown(f"""
            <div class='message-container'>
                <span class='speaker-name'>{msg['speaker']}</span>
                <span class='round-badge'>{round_label}</span>
                <span class='timestamp'>{time.strftime('%H:%M:%S', time.localtime(msg['timestamp']))}</span>
                <br>{msg['text']}
            </div>
            """, unsafe_allow_html=True)
    
    # After mediator, show scorecard if available
    if speaker == "Mediator" and "final_consensus" in st.session_state and st.session_state.final_consensus:
        consensus = st.session_state.final_consensus
        if "scorecard" in consensus and consensus["scorecard"]:
            df = pd.DataFrame(consensus["scorecard"])
            scorecard_placeholder.markdown("### 📊 Expert Scorecard")
            scorecard_placeholder.dataframe(df, use_container_width=True)
    
    time.sleep(debate_speed)

# Start debate button
if st.button("🚀 Start Debate", type="primary", key="start", use_container_width=False):
    if not topic:
        st.warning("Please enter a topic.")
    elif not api_key:
        st.warning("Please enter your GROQ API key in the sidebar.")
    else:
        # Reset state
        st.session_state.messages = []
        st.session_state.debate_complete = False
        debate_placeholder.empty()
        scorecard_placeholder.empty()
        
        # Run engine with callback
        engine = SynthosEngine(api_key=api_key, model=model, provider="groq")
        with st.spinner("Debate in progress..."):
            result_md = engine.run(topic, constraints, on_message=on_message)
        
        # Store final consensus for scorecard display
        st.session_state.final_consensus = engine.final_consensus
        st.session_state.debate_complete = True
        
        # Show final consensus section
        st.success("✅ Debate concluded!")
        with st.expander("📄 Final Consensus Report", expanded=True):
            st.markdown(result_md)
        
        # Download button
        st.download_button("💾 Download Transcript (Markdown)", result_md, file_name="synthos_debate.md", key="download")