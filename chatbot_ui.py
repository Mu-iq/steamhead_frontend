import streamlit as st
import requests
import uuid

# Generate a session ID for the user
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())  # Unique ID per session

# For managing form submission and clearing
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

st.set_page_config(page_title="Creative Agency Chatbot", layout="centered")

# Custom CSS for better chat UI
st.markdown("""
    <style>
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
    </style>
""", unsafe_allow_html=True)

st.title("💬 Creative Agency Chatbot")

# Initialize chat history in UI
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

import streamlit as st
import requests

# Function to handle form submission
def handle_submit():
    if st.session_state.user_input.strip():
        # Store the current input value
        current_input = st.session_state.user_input

        try:
            response = requests.post(
                "https://steamhead-getchats-cf-812938288740.us-central1.run.app",
                json={  # Sending JSON payload
                    "user_message": current_input, 
                    "session_id": st.session_state.session_id
                },
                headers={"Content-Type": "application/json"}  # Ensuring proper request format
            )

            if response.status_code != 200:
                st.error(f"Error: Backend returned {response.status_code}. Please check the server.")
            else:
                data = response.json()
                
                # Store user input and bot response
                st.session_state.chat_history.append({
                    "user": current_input, 
                    "bot": data.get("response", "No response received")
                })
                
                # Clear the input field after submission
                st.session_state.user_input = ""
        
        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to backend: {e}")
        except ValueError:
            st.error("Received an invalid response from the backend. Please check if the API is running.")


# Display chat history
for chat in st.session_state.chat_history:
    st.markdown(f'<div class="user-message">{chat["user"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bot-message">{chat["bot"]}</div>', unsafe_allow_html=True)

# Reset the input field if needed
if st.session_state.clear_input:
    st.session_state.user_input = ""
    st.session_state.clear_input = False

# User input box with form to allow Enter key submission
with st.form(key='chat_form'):
    user_input = st.text_input("Type your message...", key='user_input')
    submit_button = st.form_submit_button("Send", on_click=handle_submit)