import streamlit as st
import json
import time
import datetime

# --- Constants and Configuration ---
PAGE_TITLE = "Backend Learning Hub"
PAGE_ICON = "🧠"
DATA_FILE_PATH = "sessions.json"
STUDY_DURATION_MINUTES = 2
STUDY_DURATION_SECONDS = STUDY_DURATION_MINUTES * 60

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
</style>
""", unsafe_allow_html=True)


# --- Timer and Notification Logic ---
def show_notification():
    st.toast(f'🧠 Time for a break! You have been studying for {STUDY_DURATION_MINUTES} minutes.', icon='🎉')
    st.balloons()
    st.session_state.notification_shown = True

def start_timer():
    st.session_state.timer_start_time = time.time()
    st.session_state.notification_shown = False
    st.toast(f"Timer started! We'll remind you to take a break in {STUDY_DURATION_MINUTES} minutes.", icon="⏱️")

def check_timer():
    if 'timer_start_time' in st.session_state and not st.session_state.get('notification_shown', False):
        if time.time() - st.session_state.timer_start_time >= STUDY_DURATION_SECONDS:
            st.session_state.show_notification_flag = True

# --- Data Loading with Error Handling ---
@st.cache_data
def load_data(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            st.error(f"❌ **Error:** Expected a JSON list of sessions in `{filepath}`.", icon="🚨")
            return None
        return data
    except FileNotFoundError:
        st.error(f"❌ **Error:** The file `{filepath}` was not found.", icon="🚨")
        return None
    except json.JSONDecodeError:
        st.error(f"❌ **Error:** The file `{filepath}` contains invalid JSON.", icon="🚨")
        return None

# --- UI Helper Functions ---
def display_tags(tags, concepts):
    tags_html = "".join([f'<span class="tag tag-item">{tag}</span>' for tag in tags])
    concepts_html = "".join([f'<span class="tag concept-item">{concept}</span>' for concept in concepts])
    st.markdown(f"**Tags:** {tags_html}", unsafe_allow_html=True)
    st.markdown(f"**Related Concepts:** {concepts_html}", unsafe_allow_html=True)

def get_difficulty_badge(difficulty):
    return f'<span class="tag difficulty-{difficulty}">{difficulty}</span>'

# --- Main Application ---
def main():
    sessions = load_data(DATA_FILE_PATH)
    if not sessions:
        st.stop()

    # --- Sidebar for Navigation and Controls ---
    with st.sidebar:
        st.header("📚 Learning Hub")
        
        session_titles = [s['session_title'] for s in sessions]
        selected_session_title = st.selectbox("Choose a Learning Session:", session_titles)
        
        selected_session = next(s for s in sessions if s['session_title'] == selected_session_title)
        session_id = selected_session['session_id']
        topics = selected_session['topics']
        topic_titles = [t['topic_title'] for t in topics]

        st.markdown("---")
        
        selected_topic_title = st.radio("Select a Topic:", topic_titles, key=f"topic_radio_{session_id}")
        selected_topic = next(t for t in topics if t['topic_title'] == selected_topic_title)
        
        st.markdown("---")
        
        st.subheader("Your Progress")
        if f"completed_{session_id}" not in st.session_state:
            st.session_state[f"completed_{session_id}"] = {t['topic_id']: False for t in topics}

        completed_count = sum(st.session_state[f"completed_{session_id}"].values())
        progress = completed_count / len(topics) if topics else 0
        st.progress(progress, text=f"{completed_count} / {len(topics)} Topics Completed")

        is_complete = st.checkbox(
            "Mark as Complete",
            value=st.session_state[f"completed_{session_id}"][selected_topic['topic_id']],
            key=f"complete_checkbox_{selected_topic['topic_id']}"
        )
        st.session_state[f"completed_{session_id}"][selected_topic['topic_id']] = is_complete
        
        st.markdown("---")
        st.subheader("Study Timer ⏱️")

        # --- NEW: Timer Indicator Logic ---
        if 'timer_start_time' in st.session_state:
            elapsed_time = time.time() - st.session_state.timer_start_time
            time_remaining = max(0, STUDY_DURATION_SECONDS - elapsed_time)
            
            # Calculate minutes and seconds for display
            mins, secs = divmod(int(time_remaining), 60)
            timer_text = f"Next break in: **{mins:02d}:{secs:02d}**"
            
            # Calculate progress for the progress bar
            timer_progress = elapsed_time / STUDY_DURATION_SECONDS
            
            st.markdown(timer_text)
            st.progress(min(1.0, timer_progress))
        
        if st.button(f"Reset {STUDY_DURATION_MINUTES}-Min Break Timer"):
            start_timer()

    # --- Main Content Area ---
    st.title(f" {selected_topic['topic_title']}")

    difficulty_badge = get_difficulty_badge(selected_topic['difficulty'])
    st.markdown(f"**Difficulty:** {difficulty_badge}", unsafe_allow_html=True)
    display_tags(selected_topic['tags'], selected_topic['related_concepts'])
    
    tab1, tab2, tab3 = st.tabs(["🧠 Core Concepts", "🎤 Interview Guidance", "📌 Real-World Example"])

    with tab1:
        st.markdown(selected_topic['content_markdown'], unsafe_allow_html=True)
    with tab2:
        st.info(selected_topic['interview_guidance'], icon="💡")
    with tab3:
        st.success(selected_topic['example_usage'], icon="✅")

    # --- Timer Check and Notification ---
    if 'timer_start_time' not in st.session_state:
        start_timer()
    if 'show_notification_flag' not in st.session_state:
        st.session_state.show_notification_flag = False
    
    check_timer()
    if st.session_state.show_notification_flag:
        show_notification()
        st.session_state.show_notification_flag = False

if __name__ == "__main__":
    main()
