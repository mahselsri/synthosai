import streamlit as st
import time
import pandas as pd
from engine import SynthosEngine
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Synthos Boardroom", layout="wide", page_icon="🎙️")

# Hide default Streamlit elements
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp { margin-top: -50px; }
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 6rem;
        }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Professional theme CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #F5F7FA 0%, #F0F2F5 100%);
    }
    .speaker-container {
        background: #FFFFFF;
        border-radius: 28px;
        padding: 32px;
        margin: 20px 0;
        box-shadow: 0 12px 28px rgba(0,0,0,0.05);
        border: 1px solid rgba(0,0,0,0.05);
        height: 60vh;
        overflow-y: auto;
        scroll-behavior: smooth;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .round-tag {
        background: linear-gradient(135deg, #2C7DA0, #1F5E7E);
        color: white;
        border-radius: 40px;
        padding: 4px 16px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 16px;
    }
    .speaker-name {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1E2A3E;
    }
    .speaker-role {
        color: #5A6E8A;
        margin-bottom: 24px;
        font-size: 0.9rem;
        font-weight: 500;
        border-left: 3px solid #2C7DA0;
        padding-left: 12px;
    }
    .message-text {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #2C3E50;
        white-space: pre-wrap;
    }
    .sticky-participants {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(255,255,255,0.98);
        backdrop-filter: blur(8px);
        border-top: 1px solid rgba(0,0,0,0.08);
        padding: 12px 24px;
        z-index: 1000;
        box-shadow: 0 -4px 12px rgba(0,0,0,0.03);
        display: flex;
        justify-content: center;
        gap: 16px;
        flex-wrap: wrap;
    }
    .participant-card {
        text-align: center;
        background: #F8F9FC;
        border-radius: 48px;
        padding: 8px 12px;
        transition: all 0.2s ease;
        border: 1px solid transparent;
        min-width: 90px;
    }
    .participant-speaking {
        background: #E8F0FE;
        border: 1px solid #2C7DA0;
        box-shadow: 0 4px 12px rgba(44,125,160,0.15);
        transform: scale(1.02);
    }
    .participant-avatar {
        font-size: 2rem;
    }
    .participant-name {
        font-weight: 600;
        font-size: 0.85rem;
        color: #1E2A3E;
    }
    .participant-role {
        font-size: 0.7rem;
        color: #5A6E8A;
    }
    .speaking-badge {
        background: #E63946;
        color: white;
        border-radius: 20px;
        padding: 2px 6px;
        font-size: 0.65rem;
        font-weight: 600;
        margin-left: 6px;
        display: inline-block;
    }
    .stProgress > div > div {
        background-color: #2C7DA0 !important;
    }
    .stButton button {
        background: linear-gradient(135deg, #2C7DA0, #1F5E7E);
        color: white;
        border-radius: 40px;
        padding: 10px 28px;
        font-weight: 600;
        border: none;
        transition: all 0.2s;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(44,125,160,0.3);
    }
    .setup-container {
        max-width: 560px;
        margin: 100px auto;
        background: #FFFFFF;
        padding: 40px;
        border-radius: 32px;
        box-shadow: 0 20px 35px -12px rgba(0,0,0,0.1);
        text-align: center;
    }
    .guide-container {
        background: #FFFFFF;
        border-radius: 24px;
        padding: 20px;
        margin: 20px 0;
        text-align: center;
        font-weight: 500;
        color: #2C7DA0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
        border: 1px solid rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Session state
if "mode" not in st.session_state:
    st.session_state.mode = "setup"
if "debate_history" not in st.session_state:
    st.session_state.debate_history = []
if "participants" not in st.session_state:
    st.session_state.participants = []
if "current_speaker" not in st.session_state:
    st.session_state.current_speaker = None
if "final_consensus" not in st.session_state:
    st.session_state.final_consensus = {}
if "playback_index" not in st.session_state:
    st.session_state.playback_index = 0
if "playback_active" not in st.session_state:
    st.session_state.playback_active = False
if "meeting_ended" not in st.session_state:
    st.session_state.meeting_ended = False
if "topic" not in st.session_state:
    st.session_state.topic = ""
if "constraints" not in st.session_state:
    st.session_state.constraints = ""
if "debate_generated" not in st.session_state:
    st.session_state.debate_generated = False

# Auto-scroll JS
auto_scroll_js = """
<script>
function scrollSpeakerContainer() {
    const container = document.querySelector('.speaker-container');
    if (container) container.scrollTop = container.scrollHeight;
}
const observer = new MutationObserver(() => scrollSpeakerContainer());
setTimeout(() => {
    const container = document.querySelector('.speaker-container');
    if (container) {
        observer.observe(container, { childList: true, subtree: true, characterData: true });
        scrollSpeakerContainer();
    }
}, 500);
</script>
"""

# Setup screen
if st.session_state.mode == "setup":
    st.markdown('<div class="setup-container">', unsafe_allow_html=True)
    st.markdown("<h1 style='margin-bottom:0;'>🎙️ Synthos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#5A6E8A;'>AI‑powered boardroom debates</p>", unsafe_allow_html=True)
    with st.form("setup_form"):
        topic = st.text_input("Topic", placeholder="e.g., Implement AI Agent Calling for customer support")
        constraints = st.text_area("Constraints (optional)", placeholder="GDPR, budget under $50k")
        api_key = st.text_input("GROQ API Key", type="password", value=os.getenv("GROQ_API_KEY", ""))
        model = st.selectbox("Model", ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"])
        submitted = st.form_submit_button("🚀 Start Meeting")
        if submitted:
            if not topic or not api_key:
                st.warning("Please enter both topic and API key.")
            else:
                st.session_state.topic = topic
                st.session_state.constraints = constraints
                st.session_state.api_key = api_key
                st.session_state.model = model
                st.session_state.mode = "meeting"
                st.session_state.debate_history = []
                st.session_state.participants = []
                st.session_state.current_speaker = None
                st.session_state.playback_index = 0
                st.session_state.playback_active = True
                st.session_state.meeting_ended = False
                st.session_state.debate_generated = False
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Meeting mode
elif st.session_state.mode == "meeting":
    if "scroll_js_injected" not in st.session_state:
        st.components.v1.html(auto_scroll_js, height=0)
        st.session_state.scroll_js_injected = True

    # Single placeholder for participant bar
    if "participant_placeholder" not in st.session_state:
        st.session_state.participant_placeholder = st.empty()

    speaker_placeholder = st.empty()
    guide_placeholder = st.empty()

    def render_participant_bar():
        participants = st.session_state.participants
        current = st.session_state.current_speaker
        if not participants:
            st.session_state.participant_placeholder.empty()
            return
        # Build a compact, single‑line HTML string
        html_parts = ['<div class="sticky-participants">']
        for p in participants:
            is_speaking = (p["name"] == current)
            card_class = "participant-card participant-speaking" if is_speaking else "participant-card"
            badge = '<span class="speaking-badge">🔊</span>' if is_speaking else ""
            html_parts.append(
                f'<div class="{card_class}">'
                f'<div class="participant-avatar">{p.get("avatar", "👤")}</div>'
                f'<div class="participant-name">{p["name"]} {badge}</div>'
                f'<div class="participant-role">{p["role"][:15]}</div>'
                f'</div>'
            )
        html_parts.append('</div>')
        html = ''.join(html_parts)
        # Use markdown with unsafe_allow_html (this works)
        st.session_state.participant_placeholder.markdown(html, unsafe_allow_html=True)

    # Generate debate only once
    if st.session_state.playback_active and not st.session_state.debate_generated:
        steps = [
            "🧠 Generating expert personas...",
            "👥 Assembling boardroom participants...",
            "📝 Preparing opening statements...",
            "⚖️ Setting up debate rounds...",
            "🎤 Starting the meeting..."
        ]
        for step in steps:
            guide_placeholder.markdown(f'<div class="guide-container">⏳ {step}</div>', unsafe_allow_html=True)
            time.sleep(1.2)
        
        with st.spinner("Running AI debate (this may take a minute)..."):
            engine = SynthosEngine(api_key=st.session_state.api_key, model=st.session_state.model, provider="groq")
            engine.set_topic(st.session_state.topic, st.session_state.constraints)
            engine.generate_personas()
            participants = []
            for p in engine.personas:
                participants.append({
                    "name": p["name"],
                    "role": p["role"],
                    "avatar": "👩‍💼" if "female" in p["name"].lower() else "👨‍💼"
                })
            participants.append({"name": "Mediator", "role": "Neutral Mediator", "avatar": "⚖️"})
            st.session_state.participants = participants
            
            engine.round1_opening_statements()
            engine.round2_cross_examination()
            engine.round3_refinement()
            engine.mediate()
            st.session_state.debate_history = engine.debate_history
            st.session_state.final_consensus = engine.final_consensus
        
        guide_placeholder.empty()
        st.session_state.debate_generated = True
        st.session_state.playback_index = 0
        render_participant_bar()
        st.rerun()

    # Render participant bar on each rerun after generation
    if st.session_state.debate_generated:
        render_participant_bar()

    # Playback loop
    if st.session_state.playback_active and st.session_state.playback_index < len(st.session_state.debate_history):
        idx = st.session_state.playback_index
        msg = st.session_state.debate_history[idx]
        st.session_state.current_speaker = msg["speaker"]
        render_participant_bar()  # update highlight

        round_tag = {1: "Opening Statement", 2: "Cross‑examination", 3: "Refinement", 4: "Mediator Verdict"}.get(msg["round"], "")
        speaker_name = msg["speaker"]
        speaker_role = next((p["role"] for p in st.session_state.participants if p["name"] == msg["speaker"]), "")
        full_text = msg["text"]

        typed = ""
        for i, char in enumerate(full_text):
            typed += char
            cursor = "▌" if i < len(full_text)-1 else ""
            speaker_placeholder.markdown(f"""
            <div class="speaker-container">
                <div class="round-tag">{round_tag}</div>
                <div class="speaker-name">{speaker_name}</div>
                <div class="speaker-role">{speaker_role}</div>
                <div class="message-text">{typed}{cursor}</div>
            </div>
            """, unsafe_allow_html=True)
            if i % 5 == 0:
                st.components.v1.html("""
                <script>
                    const container = document.querySelector('.speaker-container');
                    if(container) container.scrollTop = container.scrollHeight;
                </script>
                """, height=0)
            time.sleep(0.02)

        speaker_placeholder.markdown(f"""
        <div class="speaker-container">
            <div class="round-tag">{round_tag}</div>
            <div class="speaker-name">{speaker_name}</div>
            <div class="speaker-role">{speaker_role}</div>
            <div class="message-text">{full_text}</div>
        </div>
        """, unsafe_allow_html=True)
        st.components.v1.html("""
        <script>
            const container = document.querySelector('.speaker-container');
            if(container) container.scrollTop = container.scrollHeight;
        </script>
        """, height=0)

        progress = (idx + 1) / len(st.session_state.debate_history)
        st.progress(progress)
        time.sleep(1.5)

        st.session_state.playback_index += 1
        if st.session_state.playback_index >= len(st.session_state.debate_history):
            st.session_state.playback_active = False
            st.session_state.current_speaker = None
            st.session_state.meeting_ended = True
            render_participant_bar()
        st.rerun()

    elif st.session_state.playback_active and st.session_state.playback_index >= len(st.session_state.debate_history):
        st.session_state.playback_active = False
        st.session_state.current_speaker = None
        st.session_state.meeting_ended = True
        render_participant_bar()
        st.rerun()

    # Final consensus
    if st.session_state.meeting_ended:
        st.markdown("## 📋 Final Consensus Summary")
        consensus = st.session_state.final_consensus
        verdict = consensus.get("verdict", "No verdict")
        impl_plan = consensus.get("implementation_plan", [])
        risks = consensus.get("risks_mitigations", [])
        dissent = consensus.get("dissent_note", "None")

        st.markdown(f"""
        <div style="background:#FFFFFF; padding:24px; border-radius:28px; border:1px solid rgba(0,0,0,0.05); margin:20px 0;">
            <h4 style="color:#1E2A3E;">Verdict</h4>
            <p style="color:#2C3E50;">{verdict}</p>
            <h4 style="color:#1E2A3E;">Implementation Plan</h4>
            <ul>{"".join(f"<li style='color:#2C3E50;'>{step}</li>" for step in impl_plan)}</ul>
            <h4 style="color:#1E2A3E;">Risks & Mitigations</h4>
            <ul>{"".join(f"<li style='color:#2C3E50;'>{risk}</li>" for risk in risks)}</ul>
            <h4 style="color:#1E2A3E;">Dissent</h4>
            <p style="color:#2C3E50;">{dissent}</p>
        </div>
        """, unsafe_allow_html=True)

        if "scorecard" in consensus:
            st.markdown("### 📊 Scorecard")
            df = pd.DataFrame(consensus["scorecard"])
            st.dataframe(df, use_container_width=True)

        full_transcript = f"# Synthos Debate: {st.session_state.topic}\n\n"
        for msg in st.session_state.debate_history:
            full_transcript += f"**Round {msg['round']} - {msg['speaker']}:** {msg['text']}\n\n"
        full_transcript += f"\n## Consensus\n{verdict}\n\n### Implementation Plan\n" + "\n".join(f"- {s}" for s in impl_plan) + "\n\n### Risks\n" + "\n".join(f"- {r}" for r in risks)
        st.download_button("📥 Download Full Transcript", full_transcript, file_name="synthos_meeting.md", key="download")

        if st.button("➕ New Meeting"):
            st.session_state.mode = "setup"
            st.rerun()