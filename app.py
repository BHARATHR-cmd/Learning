import streamlit as st
import json
import time
import streamlit.components.v1 as components

# --- Constants and Configuration ---
PAGE_TITLE = "Backend Learning Hub"
PAGE_ICON = "🧠"
DATA_FILE_PATH = "sessions.json"
NOTIFICATION_INTERVAL_MINUTES = 2
NOTIFICATION_INTERVAL_SECONDS = NOTIFICATION_INTERVAL_MINUTES * 60

# --- Page Configuration ---
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for visual appeal ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem; padding-bottom: 2rem; padding-left: 5rem; padding-right: 5rem;
    }
    h1, h2 { font-weight: 700; color: #FF4B4B; }
    h2 { border-bottom: 2px solid #FF4B4B; padding-bottom: 8px; margin-top: 2rem; }
    .st-emotion-cache-1h9usn1 p { font-size: 1.1rem; }
    .tag {
        display: inline-block; padding: 0.25em 0.6em; font-size: 0.85em; font-weight: 700;
        line-height: 1; text-align: center; white-space: nowrap; vertical-align: baseline;
        border-radius: 0.25rem; margin: 0.1rem; color: #fff;
    }
    .difficulty-Easy { background-color: #28a745; }
    .difficulty-Medium { background-color: #ffc107; color: #212529; }
    .difficulty-Hard { background-color: #dc3545; }
    .tag-item { background-color: #007bff; }
    .concept-item { background-color: #6c757d; }
    .notification-button {
        background-color: #007bff; color: white; border: none; padding: 10px 20px;
        text-align: center; text-decoration: none; display: inline-block;
        font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 8px; width: 100%;
    }
</style>
""", unsafe_allow_html=True)


# --- Reusable Components & Helper Functions ---

@st.cache_data
def load_data(filepath):
    """Loads and validates the learning session data from a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            st.error(f"❌ **Error:** Expected a JSON list of sessions in `{filepath}`.", icon="🚨")
            return None
        return data
    except FileNotFoundError:
        st.error(f"❌ **Error:** The file `{filepath}` was not found. Please make sure it's in the same directory as `app.py`.", icon="🚨")
        return None
    except json.JSONDecodeError:
        st.error(f"❌ **Error:** The file `{filepath}` contains invalid JSON. Please check the file content.", icon="🚨")
        return None

def render_mermaid(mermaid_code: str):
    """Renders a Mermaid diagram from a code string using a CDN."""
    html_template = f"""
        <div style="display: flex; justify-content: center; margin-bottom: 20px;">
            <pre class="mermaid">{mermaid_code}</pre>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@8.8.0/dist/mermaid.min.js"></script>
        <script>
            mermaid.initialize({{startOnLoad:true}});
            mermaid.init(undefined, document.querySelectorAll('.mermaid'));
        </script>
    """
    components.html(html_template, height=400, scrolling=True)

def browser_notification_component():
    """Injects HTML and JavaScript to handle browser-based desktop notifications."""
    interval_ms = NOTIFICATION_INTERVAL_MINUTES * 60 * 1000
    components.html(f"""
        <button id="notifyBtn" class="notification-button">Enable Desktop Notifications</button>
        <p id="status" style="font-size: 0.9em; color: #6c757d; text-align: center;"></p>
        <script>
            const notifyBtn = document.getElementById('notifyBtn');
            const statusEl = document.getElementById('status');
            let intervalId = null;

            function showNotification() {{
                const notification = new Notification('Learning Hub Reminder 🚀', {{
                    body: 'Time for your {NOTIFICATION_INTERVAL_MINUTES}-minute learning break!',
                    icon: 'https://emojicdn.elk.sh/🧠'
                }});
            }}

            notifyBtn.onclick = function() {{
                if (!("Notification" in window)) {{
                    statusEl.textContent = 'This browser does not support desktop notification.';
                }} else if (Notification.permission === "granted") {{
                    if (intervalId) clearInterval(intervalId);
                    intervalId = setInterval(showNotification, {interval_ms});
                    statusEl.textContent = '✅ Notifications are enabled!';
                    notifyBtn.style.display = 'none';
                }} else if (Notification.permission !== "denied") {{
                    Notification.requestPermission().then(function (permission) {{
                        if (permission === "granted") {{
                            if (intervalId) clearInterval(intervalId);
                            intervalId = setInterval(showNotification, {interval_ms});
                            statusEl.textContent = '✅ Notifications enabled!';
                            notifyBtn.style.display = 'none';
                        }} else {{
                            statusEl.textContent = 'Notification permission denied.';
                        }}
                    }});
                }} else {{
                    statusEl.textContent = 'Permission denied. Please enable notifications in your browser settings.';
                }}
            }};
        </script>
    """, height=100)

# --- RE-ADDED: UI Helper Function ---
def display_tags(tags, concepts):
    """Renders tags and related concepts with custom styling."""
    tags_html = "".join([f'<span class="tag tag-item">{tag}</span>' for tag in tags])
    concepts_html = "".join([f'<span class="tag concept-item">{concept}</span>' for concept in concepts])
    st.markdown(f"**Tags:** {tags_html}", unsafe_allow_html=True)
    st.markdown(f"**Related Concepts:** {concepts_html}", unsafe_allow_html=True)


# --- Main Application ---
def main():
    sessions = load_data(DATA_FILE_PATH)
    if not sessions:
        st.stop()

    # --- Sidebar ---
    with st.sidebar:
        st.header("📚 Learning Hub")
        
        session_titles = [s['session_title'] for s in sessions]
        selected_session_title = st.selectbox("Choose a Learning Session:", session_titles)
        
        selected_session = next((s for s in sessions if s['session_title'] == selected_session_title), sessions[0])
        session_id = selected_session['session_id']
        topics = selected_session.get('topics', [])
        topic_titles = [t['topic_title'] for t in topics]

        st.markdown("---")
        
        if topic_titles:
            selected_topic_title = st.radio("Select a Topic:", topic_titles, key=f"topic_radio_{session_id}")
            selected_topic = next((t for t in topics if t['topic_title'] == selected_topic_title), topics[0])
        else:
            st.warning("This session has no topics.")
            selected_topic = None

        st.markdown("---")
        
        st.subheader("Your Progress")
        if f"completed_{session_id}" not in st.session_state:
            st.session_state[f"completed_{session_id}"] = {t['topic_id']: False for t in topics}

        completed_count = sum(st.session_state[f"completed_{session_id}"].values())
        progress = completed_count / len(topics) if topics else 0
        st.progress(progress, text=f"{completed_count} / {len(topics)} Topics Completed")

        if selected_topic:
            is_complete = st.checkbox(
                "Mark as Complete",
                value=st.session_state[f"completed_{session_id}"][selected_topic['topic_id']],
                key=f"complete_checkbox_{selected_topic['topic_id']}"
            )
            st.session_state[f"completed_{session_id}"][selected_topic['topic_id']] = is_complete
        
        st.markdown("---")
        st.subheader("Desktop Notifications 🔔")
        browser_notification_component()

    # --- Main Content Area ---
    if selected_topic:
        st.title(f" {selected_topic['topic_title']}")

        difficulty = selected_topic.get('difficulty', 'N/A')
        st.markdown(f"**Difficulty:** <span class='tag difficulty-{difficulty}'>{difficulty}</span>", unsafe_allow_html=True)
        
        # This line will now work correctly
        display_tags(selected_topic.get('tags', []), selected_topic.get('related_concepts', []))
        
        tab1, tab2, tab3 = st.tabs(["🧠 Core Concepts", "🎤 Interview Guidance", "📌 Real-World Example"])

        with tab1:
            content = selected_topic.get('content_markdown', 'No content available.')
            content_parts = content.split('```mermaid')
            for i, part in enumerate(content_parts):
                if i == 0:
                    st.markdown(part, unsafe_allow_html=True)
                else:
                    try:
                        mermaid_code, rest_of_content = part.split('```', 1)
                        render_mermaid(mermaid_code.strip())
                        st.markdown(rest_of_content, unsafe_allow_html=True)
                    except ValueError:
                        st.markdown(part, unsafe_allow_html=True)
        with tab2:
            st.info(selected_topic.get('interview_guidance', 'No guidance available.'), icon="💡")
        with tab3:
            st.success(selected_topic.get('example_usage', 'No example available.'), icon="✅")

if __name__ == "__main__":
    main()
