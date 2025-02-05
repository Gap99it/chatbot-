import streamlit as st
import requests
import os
from langchain.prompts import PromptTemplate
from PIL import Image
import pytesseract
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Function to call Mistral AI API
def generate_response(profile, message, mode):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = f"""
    You are a friendly and engaging AI designed to help users write dating messages.

    {mode}: {profile}
    {message}

    Generate a warm, friendly, and engaging response with 4-5 sentences summarizing the profile and up to 5 thoughtful questions.
    """
    data = {
        "model": "mistral-medium",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code} - {response.text}"

# OCR Function to Extract Text from Image
def extract_text_from_image(image):
    text = pytesseract.image_to_string(image)
    return text.strip()

# Function to Extract Text from URL
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except Exception as e:
        return f"Error extracting data from URL: {str(e)}"

# Streamlit UI
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

# Upload Profile Image, Text File, or URL
uploaded_profile = st.file_uploader("Upload Profile Image or Text File", type=["png", "jpg", "jpeg", "txt"])
profile_url = st.text_input("Or enter a profile URL:")

user_message = ""
if option in ["Followup Reply Message", "Chatbot Help"]:
    user_message = st.text_area("Enter your message:")

# Generate Response Button
if st.button("Generate Response"):
    profile_text = ""

    if uploaded_profile:
        if uploaded_profile.type.startswith("image"):
            profile_text = extract_text_from_image(Image.open(uploaded_profile))
        else:
            profile_text = uploaded_profile.getvalue().decode("utf-8")
    elif profile_url:
        profile_text = extract_text_from_url(profile_url)

    if profile_text or user_message:
        response = generate_response(profile_text, user_message, option)
        st.subheader("💌 AI Generated Response:")
        st.write(response)
    else:
        st.warning("⚠ Please upload a profile, enter a URL, or provide a message.")
