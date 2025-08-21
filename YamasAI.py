import os
import streamlit as st
from openai import OpenAI

# ---------------- Page setup (mobile friendly) ----------------
st.set_page_config(page_title="Yamas Chat", page_icon="🍣", layout="centered")
st.markdown(
    """
    <style>
      header {visibility: hidden;}                 /* hide default header */
      .block-container {padding-top: .5rem;}       /* tighter spacing on iPhone */
      .stChatFloatingInputContainer {bottom: env(safe-area-inset-bottom);} /* respect iOS safe area */
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💬 Yamas Assistant")
st.caption("Simple chat UI that calls your model. Optimized for iPhone.")

# ---------------- Model configuration ----------------
BACKEND = os.getenv("CHAT_BACKEND", "openai").lower()
MODEL = os.getenv("CHAT_MODEL", "gpt-5.1-mini")
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are the helpful Yamas restaurant assistant. Be concise, friendly, and action-oriented.",
)

# Allow user to paste their API key directly in the sidebar
if "OPENAI_API_KEY" not in st.session_state:
    st.session_state.OPENAI_API_KEY = ""

with st.sidebar:
    st.subheader("Settings")
    st.session_state.OPENAI_API_KEY = st.text_input(
        "OpenAI API Key",
        type="password",
        value=st.session_state.OPENAI_API_KEY,
        placeholder="sk-...",
    )
    st.write(f"Backend: **{BACKEND}**")
    if BACKEND == "openai":
        st.write(f"Model: **{MODEL}**")
    if st.button("Reset conversation"):
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": "Hi! I’m the Yamas assistant. How can I help today?"},
        ]
        st.rerun()

client = None
if BACKEND == "openai" and st.session_state.OPENAI_API_KEY:
    client = OpenAI(api_key=st.session_state.OPENAI_API_KEY)

# ---------------- Chat state ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "Hi! I’m the Yamas assistant. How can I help today?"},
    ]

# Render history (skip system)
for m in st.session_state.messages:
    if m["role"] == "system":
        continue
    with st.chat_message(m["role"]):
        st.markdown(m["content"])  # supports markdown

# Input
user_text = st.chat_input("Type a message…")
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        placeholder = st.empty()

        if BACKEND == "openai" and client:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                    if m["role"] != "system"
                ],
                stream=True,
            )
            full = ""
            for chunk in stream:
                delta = chunk.choices[0].delta if chunk.choices and chunk.choices[0].delta else None
                content = getattr(delta, "content", None) if delta else None
                if content:
                    full += content
                    placeholder.markdown(full)
            st.session_state.messages.append({"role": "assistant", "content": full})
        elif BACKEND == "custom":
            reply = "(Custom backend not configured yet.)"
            placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        else:
            placeholder.warning("No API key set, so I can't reach the model yet.")
