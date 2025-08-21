import streamlit as st
import streamlit.components.v1 as components

# Title
st.set_page_config(page_title="QuickList + Vapi Widget", page_icon="✅", layout="centered")
st.title("📋 QuickList with Voice Assistant")

st.markdown("""
This is a demo web app for **Yamas** that works on iPhones. It includes:
- A simple to-do list (QuickList)
- The Vapi AI widget for text chat only (no voice button)

You can also add this app to your iPhone's home screen via Safari.
""")

# QuickList implementation (basic Streamlit version)
if "items" not in st.session_state:
    st.session_state.items = []

new_item = st.text_input("Add a new item:", key="new_item")
if st.button("➕ Add"):
    if new_item.strip():
        st.session_state.items.append({"text": new_item.strip(), "done": False})
        st.session_state.new_item = ""  # clear field

# Render list
for idx, item in enumerate(st.session_state.items):
    cols = st.columns([0.1, 0.7, 0.2])
    with cols[0]:
        done = st.checkbox("", value=item["done"], key=f"done_{idx}")
        st.session_state.items[idx]["done"] = done
    with cols[1]:
        st.write("~~" + item["text"] + "~~" if item["done"] else item["text"])
    with cols[2]:
        if st.button("🗑️", key=f"del_{idx}"):
            st.session_state.items.pop(idx)
            st.experimental_rerun()

if st.button("🧹 Clear completed"):
    st.session_state.items = [i for i in st.session_state.items if not i["done"]]

# Spacer
st.markdown("---")

# Embed Vapi widget (text chat only, no button)
st.subheader("💬 Text Chat Assistant")
components.html(
    """
    <style>
      vapi-widget button { display: none !important; }
    </style>
    <vapi-widget assistant-id="fb332ae2-bf30-4bfe-a435-db8ceb966b1b" public-key="09b432a0-3fb6-4462-b47d-e7a50c8bf38c"></vapi-widget>

    <script
      src="https://unpkg.com/@vapi-ai/client-sdk-react/dist/embed/widget.umd.js"
      async
      type="text/javascript"
    ></script>
    """,
    height=400,
)
