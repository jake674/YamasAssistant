import os
import requests
import streamlit as st

# ---------------- Page setup (mobile friendly) ----------------
st.set_page_config(page_title="Yamas Chat (Vapi)", page_icon="🍣", layout="centered")
st.markdown(
    """
    <style>
      header {visibility: hidden;}
      .block-container {padding-top: .5rem;}
      .stChatFloatingInputContainer {bottom: env(safe-area-inset-bottom);} /* iOS safe area */
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💬 Yamas Assistant (via Vapi)")
st.caption("Custom Streamlit chat that talks to your existing Vapi assistant — same model, same system prompts.")

# ---------------- Vapi config ----------------
VAPI_BASE_URL = os.getenv("VAPI_BASE_URL", "https://api.vapi.ai")
ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID", "fb332ae2-bf30-4bfe-a435-db8ceb966b1b")  # Your Yamas assistant
PUBLIC_KEY = os.getenv("VAPI_PUBLIC_KEY", "09b432a0-3fb6-4462-b47d-e7a50c8bf38c")     # not used for REST

# Ask for the **Vapi Private API key** (NOT OpenAI).
# Per Vapi docs, use a private API key for chat requests. Keep it server-side only.
# https://docs.vapi.ai/chat/quickstart
with st.sidebar:
    st.subheader("Vapi Settings")
    if "VAPI_PRIVATE_KEY" not in st.session_state:
       st.session_state.VAPI_PRIVATE_KEY = "e87fef95-50d3-4b1e-8825-cb998e8bcc19"
    st.session_state.VAPI_PRIVATE_KEY = st.text_input(
        "Vapi Private API Key",
        type="password",
        value=st.session_state.VAPI_PRIVATE_KEY,
        placeholder="vapi_...",
        help="Required for REST calls to your Vapi assistant. Stored only in this session.",
    )
    if st.button("Reset conversation"):
        st.session_state.chat_id = None
        st.session_state.messages = []
        st.rerun()

# ---------------- Chat state ----------------
if "messages" not in st.session_state or not st.session_state.get("messages"):
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I’m the Yamas assistant. How can I help today?"},
    ]
if "chat_id" not in st.session_state:
    st.session_state.chat_id = None  # we will pass this as previousChatId to maintain context

# Render transcript
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])  # markdown supported

# Helper: call Vapi Chat API (non-streaming)
# Endpoint per docs: POST {BASE}/chat with Authorization: Bearer <PRIVATE_KEY>
# Body: { assistantId, input, previousChatId? }
# Returns: { id: chatId, output: [{ role: 'assistant', content: '...' }, ...] }

def vapi_chat(private_key: str, assistant_id: str, user_text: str, prev_chat_id: str | None):
    url = f"{VAPI_BASE_URL}/chat"
    headers = {
        "Authorization": f"Bearer {private_key}",
        "Content-Type": "application/json",
    }
    payload = {"assistantId": assistant_id, "input": user_text}
    if prev_chat_id:
        payload["previousChatId"] = prev_chat_id
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()

# Input
user_text = st.chat_input("Type a message…")
if user_text:
    # Show user's message
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    # Assistant reply
    with st.chat_message("assistant"):
        placeholder = st.empty()
        if not st.session_state.VAPI_PRIVATE_KEY:
            placeholder.warning("Please paste your Vapi **Private API Key** in the sidebar.")
        else:
            try:
                resp = vapi_chat(
                    private_key=st.session_state.VAPI_PRIVATE_KEY,
                    assistant_id=ASSISTANT_ID,
                    user_text=user_text,
                    prev_chat_id=st.session_state.chat_id,
                )
                # Save chat id to maintain context in follow-ups
                st.session_state.chat_id = resp.get("id", st.session_state.chat_id)

                # Output can be an array of assistant messages; join them
                output = resp.get("output") or []
                text_chunks = []
                for msg in output:
                    if isinstance(msg, dict) and msg.get("role") == "assistant":
                        text_chunks.append(str(msg.get("content", "")))
                    elif isinstance(msg, str):
                        text_chunks.append(msg)
                reply = "\n\n".join([t for t in text_chunks if t]) or "(Empty response)"
                placeholder.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except requests.HTTPError as e:
                try:
                    err_json = e.response.json()
                    placeholder.error(f"Vapi error: {err_json}")
                except Exception:
                    placeholder.error(f"HTTP {e.response.status_code}: {e.response.text}")
            except Exception as e:
                placeholder.error(f"Error contacting Vapi: {e}")

# ---------------- Footer ----------------
with st.expander("Notes", expanded=False):
    st.markdown(
        """
- This chat hits **Vapi Chat API** so you keep the same model, system prompts, and tools configured for your Yamas assistant. 
- We use `previousChatId` to preserve context between turns (returned as `id` in the response). 
- You can theme or brand this UI however you like.
        """
    )
