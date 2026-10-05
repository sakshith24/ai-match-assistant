import os
import sys
import streamlit as st

# Ensure the app directory is in the Python path for imports
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.agent.cricket_agent import run_cricket_agent

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="AI Cricket Match Assistant",
    page_icon="🏏",
    layout="centered"
)

st.title("AI Cricket Match Assistant")
st.markdown("Ask questions about recent cricket performances, player statistics, consistency, and player comparisons.")

# --- Environment Variable Check ---
if not os.getenv("OPENAI_API_KEY"):
    st.warning("`OPENAI_API_KEY` environment variable not set. Please set it to use the AI agent.", icon="⚠️")
if not os.getenv("RAPIDAPI_KEY") or not os.getenv("RAPIDAPI_HOST"):
    st.warning("`RAPIDAPI_KEY` or `RAPIDAPI_HOST` environment variables not set. API tools may not function correctly.", icon="⚠️")

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("About")
    st.markdown(
        """
        **AI Cricket Match Assistant**

        Ask questions about:
        - Recent player performances
        - Batting statistics
        - Bowling statistics
        - Player consistency
        - Player comparisons

        The assistant uses real cricket data and deterministic
        Python analysis before generating its response.
        """
    )

    st.header("Example Questions")
    example_questions = [
        "Show me Virat Kohli's recent performances",
        "How consistent is Virat Kohli?",
        "Compare Virat Kohli and Pat Cummins",
        "What is Pat Cummins' recent batting performance?",
        "How many wickets has Pat Cummins taken?",
        "Tell me about an unknown player."
    ]
    for q in example_questions:
        st.markdown(f"- {q}")

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- Chat History Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input and Agent Interaction ---
if prompt := st.chat_input("Ask a cricket question:"):
    # Add user message to chat history and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare conversation history for the agent call
    conversation_history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
        if m["role"] in ["user", "assistant"]
    ]

    with st.chat_message("assistant"):
        with st.spinner("Analyzing cricket data..."):
            try:
                # Call the existing AI agent without altering its core logic
                agent_response = run_cricket_agent(prompt, conversation_history)
                st.markdown(agent_response)
                # Add agent's response to chat history
                st.session_state.messages.append({"role": "assistant", "content": agent_response})
            except Exception as e:
                st.error("Sorry, I couldn't process that request right now. Please try again.")
                st.exception(e)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Sorry, I couldn't process that request right now. Please try again."
                })