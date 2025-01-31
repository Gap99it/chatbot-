import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from PIL import Image
import pytesseract
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# OpenAI LLM
llm = ChatOpenAI(model="gpt-3.5-turbo")

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

# Define Prompt Template
prompt_template = PromptTemplate(
    input_variables=["profile", "message", "mode"],
    template="""
    You are a friendly and engaging AI designed to help users write dating messages.

    {mode}: {profile}
    {message}

    Generate a warm, friendly, and engaging response with 4-5 sentences summarizing the profile and up to 5 thoughtful questions.
    """
)

# Create LLM Chain
chain = LLMChain(llm=llm, prompt=prompt_template)

# Streamlit UI with Enhanced Design
st.set_page_config(page_title="💖 Dating Chatbot", layout="wide")
st.markdown("""
    <style>
        .main { background-color: #f7f7f7; }
        .stTextInput, .stTextArea, .stFileUploader, .stButton > button {
            border-radius: 10px; padding: 10px;
        }
        .stRadio { padding-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

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
if option == "Followup Reply Message" or option == "Chatbot Help":
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
        if option == "Chatbot Help":
            response = chain.run(profile="Dating advice chatbot", message=user_message, mode="Help")
        elif option == "Profile Analysis":
            response = chain.run(profile=f"Analyze this profile and suggest improvements: {profile_text}", message="", mode=option)
        elif option == "Conversation Starters":
            response = chain.run(profile=f"Generate creative conversation starters for this profile: {profile_text}", message="", mode=option)
        else:
            response = chain.run(profile=profile_text, message=user_message, mode=option)

        # Display Generated Response
        st.subheader("💌 AI Generated Response:")
        st.write(response)
    else:
        st.warning("⚠ Please upload a profile, enter a URL, or provide a message.")

