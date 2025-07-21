import streamlit as st
import json
import time
import threading

# --- Page Configuration (ADHD-friendly: Clean layout, focused content) ---
st.set_page_config(
    page_title="Spring Boot Learning Hub",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for visual appeal ---
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    /* Larger, more engaging headers */
    h1, h2 {
        font-weight: 700;
        color: #FF4B4B; /* A vibrant color for headers */
    }
    h2 {
        border-bottom: 2px solid #FF4B4B;
        padding-bottom: 8px;
        margin-top: 2rem;
    }
    /* Style for expanders to make them pop */
    .st-emotion-cache-1h9usn1 p {
        font-size: 1.1rem;
    }
    /* Custom styling for tags */
    .tag {
        display: inline-block;
        padding: 0.25em 0.6em;
        font-size: 0.85em;
        font-weight: 700;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 0.25rem;
        margin: 0.1rem;
        color: #fff;
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
    """Displays a toast notification."""
    st.toast('🧠 Time for a break! You have been studying for 20 minutes.', icon='🎉')
    st.balloons()
    st.session_state.notification_shown = True

def start_timer():
    """Initializes or resets the study timer in the session state."""
    st.session_state.timer_start_time = time.time()
    st.session_state.notification_shown = False
    st.toast("Timer started! We'll remind you to take a break in 20 minutes.", icon="⏱️")

def check_timer():
    """Checks if 20 minutes have passed and triggers a notification."""
    if 'timer_start_time' in st.session_state and not st.session_state.get('notification_shown', False):
        elapsed_time = time.time() - st.session_state.timer_start_time
        if elapsed_time >= 1200:  # 20 minutes = 1200 seconds
            # This needs to be handled carefully in Streamlit's execution model
            # A simple flag is more reliable than trying to run a background thread that interacts with the UI
            st.session_state.show_notification_flag = True


# --- Data Loading ---
@st.cache_data
def load_data(filepath):
    """Loads the learning session data from a JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

# --- UI Helper Functions ---
def display_tags(tags, concepts):
    """Renders tags and related concepts with custom styling."""
    tags_html = "".join([f'<span class="tag tag-item">{tag}</span>' for tag in tags])
    concepts_html = "".join([f'<span class="tag concept-item">{concept}</span>' for concept in concepts])
    st.markdown(f"**Tags:** {tags_html}", unsafe_allow_html=True)
    st.markdown(f"**Related Concepts:** {concepts_html}", unsafe_allow_html=True)

def get_difficulty_badge(difficulty):
    """Returns a styled difficulty badge."""
    return f'<span class="tag difficulty-{difficulty}">{difficulty}</span>'

# --- Main Application ---
def main():
    # Load data into session state to persist it
    if 'data' not in st.session_state:
        st.session_state.data = load_data("springboot_session_01.json")
    
    data = st.session_state.data
    topics = data['topics']
    topic_titles = [t['topic_title'] for t in topics]

    # Initialize completion status and timer
    if 'completed' not in st.session_state:
        st.session_state.completed = {t['topic_id']: False for t in topics}
    if 'timer_start_time' not in st.session_state:
        start_timer()


    # --- Sidebar for Navigation and Controls (ADHD-friendly: Clear navigation) ---
    with st.sidebar:
        st.header(data['session_title'])
        st.markdown("---")
        
        # Topic selection
        selected_title = st.radio(
            "Select a Topic to Learn:",
            topic_titles,
            key="topic_selection"
        )
        
        # Find the selected topic object
        selected_topic_index = topic_titles.index(selected_title)
        topic = topics[selected_topic_index]
        
        st.markdown("---")
        
        # Progress and Completion
        st.subheader("Your Progress")
        completed_count = sum(st.session_state.completed.values())
        progress = completed_count / len(topics)
        st.progress(progress, text=f"{completed_count} / {len(topics)} Topics Completed")

        # Checkbox to mark the current topic as complete
        is_complete = st.checkbox(
            "Mark as Complete", 
            key=f"complete_{topic['topic_id']}", 
            value=st.session_state.completed[topic['topic_id']]
        )
        st.session_state.completed[topic['topic_id']] = is_complete
        
        st.markdown("---")

        # Timer controls
        st.subheader("Study Timer ⏱️")
        if st.button("Reset 20-Min Break Timer"):
            start_timer()


    # --- Main Content Area ---
    st.title(f"📚 {topic['topic_title']}")

    # Display difficulty and tags
    difficulty_badge = get_difficulty_badge(topic['difficulty'])
    st.markdown(f"**Difficulty:** {difficulty_badge}", unsafe_allow_html=True)
    display_tags(topic['tags'], topic['related_concepts'])
    
    # Use tabs for organized content (ADHD-friendly: Chunking information)
    tab1, tab2, tab3 = st.tabs(["🧠 Core Concepts", "🎤 Interview Guidance", "📌 Real-World Example"])

    with tab1:
        st.markdown(topic['content_markdown'], unsafe_allow_html=True)

    with tab2:
        st.info(topic['interview_guidance'], icon="💡")

    with tab3:
        st.success(topic['example_usage'], icon="✅")

    # --- Timer Check and Notification Display ---
    # A simple flag-based approach for notifications within Streamlit's execution model
    if 'show_notification_flag' not in st.session_state:
        st.session_state.show_notification_flag = False

    check_timer() # This function will set the flag if the timer is up

    if st.session_state.show_notification_flag:
        show_notification()
        st.session_state.show_notification_flag = False # Reset flag after showing


if __name__ == "__main__":
    main()
