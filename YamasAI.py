import streamlit as st
from textwrap import dedent

st.set_page_config(page_title="Yamas Assistant", page_icon="🎣", layout="wide")

# Minimalistic styling for a clean, mobile-friendly look
st.markdown(
    """
    <style>
      .block-container {padding-top: 0.75rem; padding-bottom: 1rem;}
      header {visibility: hidden;} /* hide default Streamlit header */
      /* Give the widget plenty of room on iPhone */
      .widget-wrap {height: 80vh;}
      @media (max-width: 420px) {
        .widget-wrap {height: 82vh;}
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("# Codfather Assistant")
st.caption("Embedded Vapi widget running inside Streamlit. Optimized for iPhone.")

# You shared these exact values — placed here as variables so you can tweak later if needed.
ASSISTANT_ID = "fb332ae2-bf30-4bfe-a435-db8ceb966b1b"
PUBLIC_KEY = "09b432a0-3fb6-4462-b47d-e7a50c8bf38c"

# The raw HTML + script. Streamlit safely sandboxes this in an iframe.
html = f"""
<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\" />
    <style>
      body {{ margin: 0; font-family: -apple-system, system-ui, Segoe UI, Roboto, Helvetica, Arial, sans-serif; }}
      .wrap {{ display: flex; flex-direction: column; gap: 12px; padding: 12px; height: 100vh; box-sizing: border-box; }}
      .card {{ border: 1px solid #e5e7eb; border-radius: 16px; padding: 12px; box-shadow: 0 1px 2px rgba(0,0,0,.04); }}
      .widget {{ flex: 1; display: flex; align-items: stretch; justify-content: center; }}
    </style>
  </head>
  <body>
    <div class=\"wrap\">
      <div class=\"card\">
        <strong>Vapi Voice Widget</strong>
        <div style=\"font-size: 12px; color: #6b7280;\">Tap the mic to start talking.</div>
      </div>
      <div class=\"widget card\">
        <vapi-widget assistant-id=\"{ASSISTANT_ID}\" public-key=\"{PUBLIC_KEY}\"></vapi-widget>
      </div>
    </div>

    <script src=\"https://unpkg.com/@vapi-ai/client-sdk-react/dist/embed/widget.umd.js\" async type=\"text/javascript\"></script>
  </body>
</html>
"""

# Render the widget in Streamlit. Increase height if you want a taller embed.
st.components.v1.html(html, height=760, scrolling=True)

with st.expander("Tips for iPhone usage", expanded=False):
    st.markdown(
        """
        - For a more app-like feel, open your Streamlit URL in Safari and use **Share → Add to Home Screen**.
        - This page uses `viewport-fit=cover` to respect the iPhone notch/safe areas.
        - If the widget needs the full height on smaller phones, raise the `height` parameter in `st.components.v1.html(...)`.
        """
    )

st.info("If your widget requires additional permissions (mic access), Safari will prompt on first use.")
