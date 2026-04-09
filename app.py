import streamlit as st
import os
import google.generativeai as genai

# --- BACKEND CONFIGURATION (Hidden from Frontend) ---

# Securely load the API key from environment variables.
# This ensures the key stays on the server and is never exposed in the UI.
# Alternatively, you can use st.secrets["GEMINI_API_KEY"] if using Streamlit Community Cloud.
api_key = os.environ.get("GEMINI_API_KEY") 

if not api_key:
    st.error("Backend Configuration Error: GEMINI_API_KEY environment variable is missing. Please set it on the server.")
    st.stop()

# Configure the Gemini API
genai.configure(api_key=api_key)

# Initialize the model (using gemini-1.5-flash as it's fast and cost-effective for general chat)
model = genai.GenerativeModel('gemini-1.5-flash')


# --- FRONTEND UI SETUP ---

st.set_page_config(page_title="Streamlit Simple Chatbot", page_icon="🤖", layout="wide")

st.title("E-commerce Chatbot 🤖")
st.markdown("Welcome to our conversational interface! Type your questions or comments below to start chatting.")

with st.sidebar:
    st.header("Navigation")
    st.button("Settings")
    st.button("About")
    st.markdown("---")
    st.info("Built with Streamlit & Gemini API")

# --- SESSION STATE INITIALIZATION ---

# 1. Store UI messages for rendering the chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. Store the Gemini Chat Session object
# This allows Gemini to remember the context of the conversation automatically
if "gemini_chat" not in st.session_state:
    st.session_state.gemini_chat = model.start_chat(history=[])

# --- RENDER CHAT HISTORY ---

for message in st.session_state.messages:
    avatar_icon = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# --- HANDLE NEW USER INPUT ---

if prompt := st.chat_input("Type your message and press Enter..."):
    
    # 1. Display user message in UI immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 2. Send message to Gemini API and get response
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        
        try:
            # Send the prompt to the backend chat session
            response = st.session_state.gemini_chat.send_message(prompt)
            
            # Display the generated response
            message_placeholder.markdown(response.text)
            
            # 3. Save the assistant's response to the UI history
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            # Handle potential API errors gracefully
            message_placeholder.error(f"An error occurred while connecting to the backend: {e}")