import os
import re
import html
import requests
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from streamlit_mic_recorder import speech_to_text

# =========================================================
# CONFIGURATION
# =========================================================
load_dotenv()

MODEL_NAME = "gemma-4-26b-a4b-it"
ELEVENLABS_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
ELEVENLABS_MODEL = "eleven_multilingual_v2"

st.set_page_config(
    page_title="SolarSentry",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# SESSION STATE
# =========================================================
DEFAULTS = {
    "solarsentry_theme": "Dark",
    "solarsentry_report": "",
    "solarsentry_audio": None,
    "solarsentry_audio_error": "",
    "solarsentry_service": {},
    "solarsentry_chat": [],
    "solarsentry_transcription": "",
    "solarsentry_notes": "",
    "solarsentry_error": "",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# THEME
# =========================================================
dark_mode = st.session_state.solarsentry_theme == "Dark"

if dark_mode:
    BG, BG_SECONDARY, CARD, CARD_ALT = "#071510", "#0b2018", "#10271d", "#142e22"
    TEXT, MUTED, BORDER, INPUT_BG = "#eff8f0", "#a4b9a9", "#244735", "#0b1b13"
    GREEN, GREEN_DARK, REPORT_TEXT = "#65e6a3", "#0e8f5a", "#e4eee6"
else:
    BG, BG_SECONDARY, CARD, CARD_ALT = "#f0f7f1", "#e3f1e6", "#ffffff", "#f5fbf6"
    TEXT, MUTED, BORDER, INPUT_BG = "#14291c", "#536b5b", "#cfe2d3", "#ffffff"
    GREEN, GREEN_DARK, REPORT_TEXT = "#087d4b", "#0c9b61", "#21392a"

# =========================================================
# STYLING
# =========================================================
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');
    :root {{
      --page-bg:{BG}; --page-bg-secondary:{BG_SECONDARY}; --card-bg:{CARD};
      --card-alt:{CARD_ALT}; --text-color:{TEXT}; --muted-color:{MUTED};
      --border-color:{BORDER}; --input-bg:{INPUT_BG}; --green:{GREEN};
      --green-dark:{GREEN_DARK}; --report-text:{REPORT_TEXT};
    }}
    html, body, [class*="css"] {{font-family:'DM Sans',sans-serif;}}
    .stApp {{
      color:var(--text-color);
      background:radial-gradient(ellipse at 5% 0%,rgba(30,125,76,.18),transparent 38%),
      radial-gradient(ellipse at 95% 40%,rgba(24,100,64,.13),transparent 36%),
      linear-gradient(145deg,var(--page-bg),var(--page-bg-secondary),var(--page-bg));
      background-attachment:fixed;
    }}
    [data-testid="stSidebar"] {{background:linear-gradient(180deg,var(--card-bg),var(--page-bg));border-right:1px solid var(--border-color);}}
    [data-testid="stSidebar"]>div:first-child {{padding-top:1.3rem;}}
    h1,h2,h3,h4,p,label {{color:var(--text-color);}}
    .brand {{font-family:'Playfair Display',serif;font-size:clamp(2rem,4vw,3rem);font-weight:700;letter-spacing:-1.4px;line-height:1.15;background:linear-gradient(100deg,#a5f3c7,#54d995 45%,#d7ffe6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:0;}}
    .brand-subtitle {{color:var(--muted-color);font-size:.78rem;margin:4px 0 12px;letter-spacing:.3px;}}
    .hero {{padding:24px 27px;margin-bottom:22px;border-radius:20px;border:1px solid rgba(142,235,180,.24);background:radial-gradient(ellipse at 80% 0%,rgba(93,230,155,.2),transparent 48%),linear-gradient(115deg,#0a281a,#104b30 47%,#102d21);box-shadow:0 12px 38px rgba(0,0,0,.13);}}
    .hero-kicker {{color:#9ce9bb;font-size:.72rem;letter-spacing:2.2px;text-transform:uppercase;font-weight:700;margin-bottom:9px;}}
    .hero-title {{font-family:'Playfair Display',serif;color:#f0fff4;font-size:clamp(1.8rem,3vw,2.55rem);font-weight:600;line-height:1.18;margin:0;}}
    .hero-copy {{color:#c3e4ce;margin-top:9px;font-size:.93rem;line-height:1.65;max-width:650px;}}
    .section-heading {{font-family:'Playfair Display',serif;font-size:1.45rem;font-weight:600;margin-bottom:3px;}}
    .section-subtitle {{color:var(--muted-color);font-size:.86rem;line-height:1.55;margin-bottom:16px;}}
    .panel-card {{background:var(--card-bg);border:1px solid var(--border-color);border-radius:16px;padding:17px;margin-bottom:14px;box-shadow:0 8px 25px rgba(0,0,0,.06);}}
    .maintenance-bar {{background:linear-gradient(115deg,var(--card-bg),var(--card-alt));border:1px solid var(--border-color);border-left:4px solid var(--green);border-radius:13px;padding:16px 18px;margin:8px 0 18px;}}
    .maintenance-title {{font-family:'Playfair Display',serif;font-size:1.15rem;font-weight:600;margin-bottom:10px;color:var(--text-color);}}
    .maintenance-reason {{font-size:.88rem;line-height:1.65;color:var(--muted-color);margin-top:10px;}}
    .status-pill {{display:inline-block;padding:5px 9px;margin:3px 5px 3px 0;border-radius:7px;font-size:.76rem;font-weight:700;background:rgba(80,190,120,.12);color:var(--text-color);border:1px solid var(--border-color);}}
    .report-content {{color:var(--report-text);line-height:1.85;font-size:.97rem;}}
    [data-testid="stMarkdownContainer"] h1,[data-testid="stMarkdownContainer"] h2,[data-testid="stMarkdownContainer"] h3 {{font-family:'Playfair Display',serif;letter-spacing:-.25px;}}
    [data-testid="stMarkdownContainer"] h2 {{font-size:1.36rem;padding-bottom:7px;margin-top:23px;border-bottom:1px solid var(--border-color);}}
    [data-testid="stMarkdownContainer"] h3 {{font-size:1.12rem;margin-top:18px;}}
    [data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] li {{line-height:1.8;}}
    [data-testid="stMetric"] {{background:var(--card-bg);border:1px solid var(--border-color);border-radius:12px;padding:12px;}}
    div.stButton>button,div.stFormSubmitButton>button {{border-radius:10px;min-height:42px;font-weight:600;transition:all .2s ease;}}
    div.stButton>button[kind="primary"],div.stFormSubmitButton>button[kind="primary"] {{background:linear-gradient(105deg,#138451,#28ad6d);color:white;border:1px solid #48c486;}}
    div.stButton>button:hover {{border-color:var(--green);transform:translateY(-1px);}}
    [data-testid="stFileUploaderDropzone"] {{background:var(--card-bg);border:1px dashed var(--border-color);border-radius:12px;}}
    [data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stNumberInput"] input {{background-color:var(--input-bg);color:var(--text-color);border-color:var(--border-color);border-radius:9px;}}
    [data-testid="stAudio"] {{width:100%;}}
    [data-testid="stChatMessage"] {{background:var(--card-bg);border:1px solid var(--border-color);border-radius:12px;padding:10px;}}
    hr {{border-color:var(--border-color);}}
    .footer {{text-align:center;color:var(--muted-color);font-size:.8rem;padding:24px 0 10px;}}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# API HELPERS
# =========================================================
def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file.")
    return genai.Client(api_key=api_key)


def clean_report_for_audio(report):
    text = re.sub(r"```.*?```", "Code block omitted.", report, flags=re.S)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.M)
    text = text.replace("**", "").replace("__", "").replace("*", "")
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\n{2,}", ". ", text)
    return re.sub(r"\s+", " ", text).strip()


def generate_report_audio(report):
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ElevenLabs API key is not configured.")

    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        json={
            "text": clean_report_for_audio(report)[:12000],
            "model_id": ELEVENLABS_MODEL,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        },
        timeout=120,
    )
    if not response.ok:
        raise RuntimeError(f"ElevenLabs returned HTTP {response.status_code}.")
    return response.content


def build_prompt(voltage, current, rated_power, irradiance, notes, transcription):
    calculated_power = voltage * current
    return f"""
You are SolarSentry, a careful solar panel inspection assistant.
Analyse the uploaded panel image together with the measurements and notes.

MEASUREMENTS
- Voltage: {voltage} V
- Current: {current} A
- Rated panel power: {rated_power} W
- Irradiance: {irradiance} W/m²
- Calculated electrical power (voltage × current): {calculated_power:.2f} W

ADDITIONAL NOTES
{notes.strip() or "None provided."}

VOICE NOTES
{transcription.strip() or "None provided."}

Write a professional, readable report with these headings:

## Executive Summary
Briefly summarise likely condition and key findings.

## Visual Inspection
Describe only details supported by the image. If dirt, shading, cracks,
discolouration, corrosion, or damaged wiring cannot be clearly identified,
say so instead of inventing observations.

## Electrical Performance
Explain readings. Compare calculated power with rated power cautiously.
Do not claim definitive efficiency loss from one reading without test conditions.

## Potential Issues
Separate visible evidence from possible explanations.

## Recommended Actions
Give practical, safe next steps. Recommend a qualified technician for
electrical faults, exposed conductors, suspected hot spots, cracked modules,
or other potentially dangerous conditions.

## Limitations
Explain what cannot be determined from the image and readings alone.

Rules: Do not invent measurements or image details. Do not claim visual
inspection proves electrical safety. Treat irradiance as user-provided.
Do not tell users to touch exposed conductors or live equipment.
Use polished Markdown, normal paragraphs, and avoid unnecessary repetition.
"""


def generate_service_recommendation(report):
    client = get_gemini_client()
    prompt = f"""
Assess maintenance needs using only this inspection report.

Return exactly four lines:
Cleaning: YES, NO, or UNCERTAIN
Servicing: YES, NO, or UNCERTAIN
Reason: one concise sentence
Urgency: ROUTINE, SOON, or URGENT

Cleaning YES only when removable contamination is supported by the report.
Servicing YES when a credible technical issue merits inspection. Use UNCERTAIN
when evidence is insufficient. URGENT only for a credible potentially dangerous
issue. Never infer electrical safety from an image alone.

REPORT:
{report}
"""
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    raw = response.text or ""
    cleaning = re.search(r"Cleaning:\s*(YES|NO|UNCERTAIN)", raw, re.I)
    servicing = re.search(r"Servicing:\s*(YES|NO|UNCERTAIN)", raw, re.I)
    reason = re.search(r"Reason:\s*(.+)", raw, re.I)
    urgency = re.search(r"Urgency:\s*(ROUTINE|SOON|URGENT)", raw, re.I)
    return {
        "cleaning": cleaning.group(1).upper() if cleaning else "UNCERTAIN",
        "servicing": servicing.group(1).upper() if servicing else "UNCERTAIN",
        "reason": reason.group(1).strip() if reason else
            "The available report does not support a confident assessment.",
        "urgency": urgency.group(1).upper() if urgency else "ROUTINE",
    }


def answer_followup_question(report, question, chat_history, voltage, current, rated_power, irradiance):
    client = get_gemini_client()
    history = "\n".join(
        f"{message['role'].capitalize()}: {message['content']}"
        for message in chat_history[-8:]
    )
    prompt = f"""
You are SolarSentry, answering a question about a solar-panel inspection.

CURRENT INSPECTION REPORT:
{report}

READINGS:
- Voltage: {voltage} V
- Current: {current} A
- Rated power: {rated_power} W
- Irradiance: {irradiance} W/m²
- Calculated electrical power: {voltage * current:.2f} W

RECENT CHAT:
{history or "No earlier questions."}

USER QUESTION:
{question}

Answer clearly and directly. Do not invent observations or measurements.
Explain uncertainty. A visual inspection cannot prove electrical safety.
Recommend a qualified technician for potentially dangerous electrical faults.
"""
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return response.text or "I couldn't generate an answer. Please try again."


def render_maintenance_bar():
    service = st.session_state.solarsentry_service
    st.markdown("### Maintenance assessment")
    if not service:
        st.info("The maintenance assessment is not available.")
        return
    if service.get("error"):
        st.warning("The report is ready, but the maintenance assessment failed.")
        return

    cleaning = service.get("cleaning", "UNCERTAIN")
    servicing = service.get("servicing", "UNCERTAIN")
    urgency = service.get("urgency", "ROUTINE")
    reason = service.get("reason", "No reason provided.")

    if cleaning == "YES" and servicing == "YES":
        recommendation = "Cleaning and servicing may be needed"
    elif cleaning == "YES":
        recommendation = "Cleaning may be needed"
    elif servicing == "YES":
        recommendation = "Professional servicing may be needed"
    elif cleaning == "NO" and servicing == "NO":
        recommendation = "No maintenance need identified in this report"
    else:
        recommendation = "Further inspection may be needed"

    st.markdown(
        f"""
        <div class="maintenance-bar">
          <div class="maintenance-title">{html.escape(recommendation)}</div>
          <span class="status-pill">Cleaning: {html.escape(cleaning)}</span>
          <span class="status-pill">Servicing: {html.escape(servicing)}</span>
          <span class="status-pill">Urgency: {html.escape(urgency)}</span>
          <div class="maintenance-reason">{html.escape(reason)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("AI-assisted guidance only. This is not a certified diagnosis or proof of electrical safety.")


# =========================================================
# HEADER
# =========================================================
header_left, header_right = st.columns([5, 1])
with header_left:
    st.markdown(
        """<div style="padding-top:7px"><div class="brand">SolarSentry</div>
        <div class="brand-subtitle">Solar intelligence. Clearer decisions.</div></div>""",
        unsafe_allow_html=True,
    )
with header_right:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    theme_choice = st.toggle("Light mode", value=not dark_mode, key="solarsentry_theme_toggle")
    new_theme = "Light" if theme_choice else "Dark"
    if new_theme != st.session_state.solarsentry_theme:
        st.session_state.solarsentry_theme = new_theme
        st.rerun()

st.markdown(
    """<div class="hero"><div class="hero-kicker">Inspection workspace</div>
    <div class="hero-title">Understand your panel's condition.</div>
    <div class="hero-copy">Upload an image, add available readings, and generate a
    structured inspection report with maintenance guidance.</div></div>""",
    unsafe_allow_html=True,
)

# =========================================================
# SIDEBAR: MEASUREMENTS
# =========================================================
with st.sidebar:
    st.markdown(
        """<div class="brand" style="font-size:1.8rem">SolarSentry</div>
        <div class="brand-subtitle">Electrical readings</div>""",
        unsafe_allow_html=True,
    )
    st.markdown("### Panel measurements")
    voltage = st.number_input("Voltage (V)", min_value=0.0, value=0.0, step=0.1, format="%.2f", key="panel_voltage")
    current = st.number_input("Current (A)", min_value=0.0, value=0.0, step=0.1, format="%.2f", key="panel_current")
    rated_power = st.number_input("Rated panel power (W)", min_value=0.0, value=0.0, step=10.0, format="%.1f", key="panel_rated_power")
    irradiance = st.number_input("Irradiance (W/m²)", min_value=0.0, value=0.0, step=10.0, format="%.1f", key="panel_irradiance")
    st.markdown("---")
    calculated_power = voltage * current
    st.metric("Calculated power", f"{calculated_power:.2f} W")
    if rated_power > 0 and calculated_power > 0:
        st.metric("Power vs rated power", f"{calculated_power / rated_power * 100:.1f}%",
                  help="A simple comparison, not a certified efficiency measurement. Output depends on operating conditions.")
    st.caption("Leave unknown readings at zero. Enter actual measurements where available.")

# =========================================================
# TWO-COLUMN WORKSPACE
# IMPORTANT: The streamed report is NOT displayed in the input column.
# It is rendered only once below in the report column.
# =========================================================
input_col, report_col = st.columns([0.9, 1.1], gap="large")

with input_col:
    st.markdown('<div class="section-heading">Panel inspection</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Start with an image, then add observations or voice notes.</div>', unsafe_allow_html=True)

    uploaded_image = st.file_uploader(
        "Upload panel image", type=["png", "jpg", "jpeg", "webp"],
        help="Choose a clear photo of the panel surface.", key="solarsentry_image_upload",
    )
    if uploaded_image:
        st.image(uploaded_image, use_container_width=True)

    st.markdown("#### Voice message")
    try:
        transcription = speech_to_text(
            language="en", use_container_width=True, just_once=True,
            key="solarsentry_voice_input",
        )
        if transcription:
            st.session_state.solarsentry_transcription = transcription
    except Exception:
        st.caption("Voice transcription is unavailable. You can type notes below.")

    voice_notes = st.text_area(
        "Voice transcription",
        value=st.session_state.solarsentry_transcription,
        placeholder="Your transcribed voice notes will appear here.",
        height=100, key="solarsentry_transcription_input",
        label_visibility="collapsed",
    )
    st.session_state.solarsentry_transcription = voice_notes

    st.markdown("#### Additional panel information")
    notes = st.text_area(
        "Additional information",
        value=st.session_state.solarsentry_notes,
        placeholder="Installation location, recent weather, visible dirt, unusual output, previous maintenance...",
        height=135, key="solarsentry_notes_input",
        label_visibility="collapsed",
    )
    st.session_state.solarsentry_notes = notes

    generate_clicked = st.button(
        "Generate inspection report", type="primary",
        use_container_width=True, key="solarsentry_generate",
    )

    if generate_clicked:
        if uploaded_image is None:
            st.warning("Upload a panel image before generating a report.")
        else:
            # Clear the previous inspection so stale results cannot be mistaken for new ones.
            st.session_state.solarsentry_report = ""
            st.session_state.solarsentry_audio = None
            st.session_state.solarsentry_audio_error = ""
            st.session_state.solarsentry_service = {}
            st.session_state.solarsentry_chat = []
            st.session_state.solarsentry_error = ""

            try:
                client = get_gemini_client()
                prompt = build_prompt(
                    voltage, current, rated_power, irradiance, notes, voice_notes
                )
                image_bytes = uploaded_image.getvalue()
                mime_type = uploaded_image.type or "image/jpeg"
                full_report = ""

                # Stream progress only; do not display report text here.
                with st.status("Analysing the panel image...", expanded=False) as status:
                    stream = client.models.generate_content_stream(
                        model=MODEL_NAME,
                        contents=[
                            prompt,
                            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                        ],
                    )
                    for chunk in stream:
                        chunk_text = getattr(chunk, "text", None)
                        if chunk_text:
                            full_report += chunk_text
                    if not full_report.strip():
                        raise RuntimeError("The AI returned an empty report. Please try again.")
                    status.update(label="Inspection report generated.", state="complete")

                # Save report first. Optional services cannot destroy it.
                st.session_state.solarsentry_report = full_report

                try:
                    with st.spinner("Preparing maintenance guidance..."):
                        st.session_state.solarsentry_service = generate_service_recommendation(full_report)
                except Exception as exc:
                    st.session_state.solarsentry_service = {"error": str(exc)}

                try:
                    with st.spinner("Preparing report narration..."):
                        st.session_state.solarsentry_audio = generate_report_audio(full_report)
                except Exception:
                    st.session_state.solarsentry_audio = None
                    st.session_state.solarsentry_audio_error = (
                        "Voice narration is temporarily unavailable. "
                        "Your written report is ready to read or download."
                    )

                st.success("Inspection report generated.")
            except Exception as exc:
                st.session_state.solarsentry_error = str(exc)
                st.error(f"Could not generate the report: {exc}")

# =========================================================
# REPORT COLUMN: SINGLE RENDER LOCATION
# =========================================================
with report_col:
    st.markdown('<div class="section-heading">Inspection report</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Your findings and recommended next steps.</div>', unsafe_allow_html=True)

    report = st.session_state.solarsentry_report

    if st.session_state.solarsentry_error and not report:
        st.error(f"Report generation failed: {st.session_state.solarsentry_error}")

    if not report:
        st.markdown(
            """<div class="panel-card"><div style="font-family:'Playfair Display',serif;font-size:1.2rem;margin-bottom:8px">
            Your report will appear here</div><div style="color:var(--muted-color);line-height:1.7">
            Add an image and available information on the left, then generate your inspection report.</div></div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("#### Report narration")
        if st.session_state.solarsentry_audio:
            st.audio(st.session_state.solarsentry_audio, format="audio/mpeg")
        else:
            st.info(st.session_state.solarsentry_audio_error or
                    "Voice narration is unavailable. Your written report is ready to read or download.")

        st.markdown("---")
        render_maintenance_bar()
        st.markdown("---")
        st.markdown('<div class="section-heading">Detailed findings</div>', unsafe_allow_html=True)

        # Render Markdown directly. Do not wrap it in a div with unsafe_allow_html=False.
        st.markdown(report)

        st.download_button(
            "Download report", data=report,
            file_name="solarsentry_inspection_report.md",
            mime="text/markdown", use_container_width=True,
            key="solarsentry_download",
        )

        st.markdown("---")
        st.markdown('<div class="section-heading">Ask SolarSentry</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Ask follow-up questions about this inspection.</div>', unsafe_allow_html=True)

        for message in st.session_state.solarsentry_chat:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        with st.form("solarsentry_followup_form", clear_on_submit=True):
            question = st.text_input(
                "Follow-up question", placeholder="What could cause reduced output?",
                label_visibility="collapsed",
            )
            ask_clicked = st.form_submit_button("Send question", use_container_width=True)

        if ask_clicked and question.strip():
            st.session_state.solarsentry_chat.append({"role": "user", "content": question.strip()})
            try:
                with st.spinner("Preparing an answer..."):
                    answer = answer_followup_question(
                        report=st.session_state.solarsentry_report,
                        question=question.strip(),
                        chat_history=st.session_state.solarsentry_chat[:-1],
                        voltage=voltage, current=current,
                        rated_power=rated_power, irradiance=irradiance,
                    )
                st.session_state.solarsentry_chat.append({"role": "assistant", "content": answer})
                st.rerun()
            except Exception as exc:
                st.error(f"Unable to answer that question: {exc}")

        if st.session_state.solarsentry_chat and st.button(
            "Clear conversation", key="solarsentry_clear_chat", use_container_width=True
        ):
            st.session_state.solarsentry_chat = []
            st.rerun()

# =========================================================
# FOOTER
# =========================================================
st.markdown(
    '<div class="footer">SolarSentry · Solar inspection and maintenance guidance</div>',
    unsafe_allow_html=True,
)

