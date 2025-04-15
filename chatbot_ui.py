import streamlit as st
import requests
import uuid
import json

# Generate a session ID for the user
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Initialize chat history in UI
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# For tracking active streaming
if "streaming_active" not in st.session_state:
    st.session_state.streaming_active = False

# For tracking if we need to process a new message
if "message_to_process" not in st.session_state:
    st.session_state.message_to_process = None

st.set_page_config(
    page_title="Creative Agency Chatbot", 
    layout="centered"
)

# Custom CSS to hide the "Running" indicator and improve styling
st.markdown("""
    <style>
        /* Hide the "Running..." indicator */
        div[data-testid="stStatusWidget"] {
            display: none !important;
        }
        
        /* Chat styling */
        body {
            background-color: #121212;
        }
        .chat-container {
            max-width: 700px;
            margin: auto;
            padding: 10px;
        }
        .bot-message {
            background-color: #1E1E1E;
            padding: 15px;
            border-radius: 10px;
            max-width: 75%;
            font-size: 16px;
            color: #FFFFFF;
            text-align: left;
            margin-bottom: 10px;
        }
        .user-message {
            background-color: #0084ff;
            color: white;
            padding: 15px;
            border-radius: 10px;
            max-width: 75%;
            font-size: 16px;
            text-align: left;
            margin-bottom: 10px;
            margin-left: auto;
        }
        .chatbox {
            height: 500px;
            overflow-y: auto;
            border: 1px solid #333;
            padding: 10px;
            border-radius: 10px;
            background-color: #181818;
        }
        
        /* Make the input area fixed at the bottom */
        .fixed-input {
            position: relative;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: #0E1117;
            padding: 10px;
            z-index: 100;
        }
        
        /* Add space at the bottom to prevent chat from being hidden behind input */
        .chat-bottom-spacer {
            height: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("💬 Steamhead Agency Chatbot")

# Create a container for the chat messages
chat_container = st.container()

# Function to handle new messages - this will be called on form submission
def handle_submit():
    # Store the message to be processed
    if st.session_state.user_input.strip():
        st.session_state.message_to_process = st.session_state.user_input
        st.session_state.user_input = ""  # Clear input immediately

# Display chat history in the chat container
with chat_container:
    # Process any pending message
    if st.session_state.message_to_process:
        user_message = st.session_state.message_to_process
        st.session_state.message_to_process = None  # Clear the pending message
        
        # Add user message to chat history
        st.session_state.chat_history.append({
            "user": user_message,
            "bot": ""  # We'll fill this in as we stream
        })
        
        # Set the streaming flag to true
        st.session_state.streaming_active = True

    # Display all chat messages
    for i, chat in enumerate(st.session_state.chat_history):
        # Display user message
        st.markdown(f'<div class="user-message">{chat["user"]}</div>', unsafe_allow_html=True)
        
        # Display bot message or stream it if it's the last one and streaming is active
        if i == len(st.session_state.chat_history) - 1 and st.session_state.streaming_active and not chat["bot"]:
            # This is the latest message and we're streaming
            bot_placeholder = st.empty()
            
            # Stream the response
            stream_url = "https://steamhead-getchat-812938288740.us-central1.run.app"

            headers = {
                "Content-Type": "application/json"
            }
            data = {
                "user_message": chat["user"],
                "session_id": st.session_state.session_id
            }

            try:
                current_response = ""
                with requests.post(stream_url, json=data, headers=headers, stream=True) as r:
                    r.raise_for_status()
                    for line in r.iter_lines(decode_unicode=True):
                        if line:
                            current_response += line
                            bot_placeholder.markdown(f'<div class="bot-message">\n{current_response}\n</div>', unsafe_allow_html=True)

                # Store the final response
                st.session_state.chat_history[-1]["bot"] = current_response
                st.session_state.streaming_active = False
                
            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")
                st.session_state.streaming_active = False
        
        elif chat["bot"]:
            # Display a completed bot message
            st.markdown(f'<div class="bot-message">{chat["bot"]}</div>', unsafe_allow_html=True)
    
    # Add space at the bottom to ensure content isn't hidden behind the fixed input
    st.markdown("<div class='chat-bottom-spacer'></div>", unsafe_allow_html=True)

# Create a fixed-position container for the input box at the bottom
st.markdown("<div class='fixed-input'>", unsafe_allow_html=True)
with st.form(key='chat_form', clear_on_submit=False):
    col1, col2 = st.columns([6, 1])
    with col1:
        user_input = st.text_input("Type your message...", key='user_input', label_visibility="collapsed")
    with col2:
        submit_button = st.form_submit_button("Send", on_click=handle_submit)
st.markdown("</div>", unsafe_allow_html=True)
