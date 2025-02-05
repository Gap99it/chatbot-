import streamlit as st
import requests
import os
import pytesseract
import PyPDF2
import pyttsx3
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY") or "00XplKyfg6UcGfNZqqFbQ8WwOzOGBAj6"
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MODEL_NAME = "mistral-medium"

# Function to Extract Text from Image
def extract_text_from_image(image):
    return pytesseract.image_to_string(image).strip()

# Function to Extract Text from URL
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except Exception as e:
        return f"Error extracting data from URL: {str(e)}"

# Function to Extract Text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return text.strip()

# Function to Generate AI Response
def generate_ai_response(profile, message, mode, tone):
    prompt_template = """
    You are a {tone} AI designed to help users write dating messages.
    
    {mode}: {profile}
    {message}
    
    Generate a response with 4-5 sentences summarizing the profile and up to 5 thoughtful questions.
    """
    prompt = prompt_template.format(profile=profile, message=message, mode=mode, tone=tone)
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": MODEL_NAME, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
    
    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=payload)
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Function to Convert Text to Speech
def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Streamlit UI Setup
st.set_page_config(page_title="💖 Dating Chatbot", layout="wide")
st.title("💖 Dating Chatbot")
st.write("Create personalized and engaging dating messages with AI!")

# Select Interaction Mode
option = st.radio("Select Mode:", [
    "Initial Send Message",
    "Followup Reply Message",
    "Profile Analysis",
    "Conversation Starters",
    "Chatbot Help"
])

# Select Tone
tone = st.selectbox("Select Message Tone:", ["Friendly 😊", "Professional 👔", "Funny 😆"])

# Upload Profile (Image, PDF, or Text File)
uploaded_profile = st.file_uploader("Upload Profile (Image, PDF, or Text File)", type=["png", "jpg", "jpeg", "txt", "pdf"])
profile_url = st.text_input("Or enter a profile URL:")

user_message = ""
if option in ["Followup Reply Message", "Chatbot Help"]:
    user_message = st.text_area("Enter your message:")

# Generate Response Button
if st.button("Generate Response"):
    profile_text = ""
    if uploaded_profile:
        if uploaded_profile.type.endswith("pdf"):
            profile_text = extract_text_from_pdf(uploaded_profile)
        elif uploaded_profile.type.startswith("image"):
            profile_text = extract_text_from_image(Image.open(uploaded_profile))
        else:
            profile_text = uploaded_profile.getvalue().decode("utf-8")
    elif profile_url:
        profile_text = extract_text_from_url(profile_url)

    if profile_text or user_message:
        response = generate_ai_response(profile_text, user_message, option, tone)
        st.subheader("💌 AI Generated Response:")
        st.write(response)
        
        # Copy Button
        st.button("📋 Copy Response", on_click=lambda: st.session_state.update({"clipboard": response}))
        
        # Voice Output
        if st.button("🔊 Hear Response"):
            text_to_speech(response)
    else:
        st.warning("⚠ Please upload a profile, enter a URL, or provide a message.")
