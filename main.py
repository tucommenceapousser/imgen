import os
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st
from PIL import Image

# Load environment variables
load_dotenv()
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("No API key found. Please set API_KEY in your .env file.")

# Initialize the Generative Model
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-8b")

def get_gemini_response(input_prompt, image):
    response = model.generate_content(
        [input_prompt, image[0]]
    )
    return response.text

def get_image_content(uploaded_file):
    if uploaded_file is not None:
        image_byte_data = uploaded_file.getvalue()
        image_parts = [{
            "mime_type": uploaded_file.type,
            "data": image_byte_data
        }]
        return image_parts
    else:
        raise FileNotFoundError("File not uploaded")

# Set Streamlit page configuration FIRST
st.set_page_config(page_title="PhotoCritique", layout="centered")

# Add custom CSS for styling
st.markdown("""
    <style>
    /* Overall background */
    body {
        background-color: #1A1A1D;
        color: #D3D3D3;
    }

    /* Headings personalization */
    h1, h2, h3, h4 {
        color: #F0F;
        border-bottom: 2px solid #F0F;
        font-family: 'Comic Sans MS', cursive;
    }

    /* Container styling */
    .css-1d391kg {
        background-color: rgba(50, 50, 50, 0.8) !important;
        box-shadow: 0 0 10px #F0F, 0 0 20px #0FF;
        border-radius: 15px;
        border: 2px solid #F0F;
    }

    /* Button styling */
    button {
        background-color: #0F0;
        color: #000;
        border: none;
        font-size: 16px;
        border-radius: 5px;
        padding: 10px;
        box-shadow: 0 0 5px #F0F;
    }

    /* Alert styling */
    .stAlert {
        background-color: #333 !important;
        border-left: 5px solid #F0F;
    }
    </style>
    """, unsafe_allow_html=True)

# Streamlit interface setup
st.markdown("<h1 style='text-align: center;'>PhotoCritique App</h1>", unsafe_allow_html=True)

# Sidebar for critique options
st.sidebar.header("Critique Options")

# Allow users to select which aspects they want feedback on
aspects = st.sidebar.multiselect(
    "Select any 3 aspects to critique:",
    options=["Composition", "Lighting", "Focus and Sharpness", "Exposure", "Color Balance", "Creativity and Impact"],
    default=["Composition", "Lighting", "Focus and Sharpness"]
)

# Ensure the user selects exactly three aspects
if len(aspects) != 3:
    st.sidebar.warning("Please select exactly 3 aspects.")

# File uploader
uploaded_file = st.file_uploader("Upload a Photo for Critique", type=["jpg", "png", "jpeg"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Photo", use_column_width=True)

submit = st.button("Get Critique")

# Construct the input prompt based on selected aspects
if submit:
    if len(aspects) == 3:
        try:
            image_data = get_image_content(uploaded_file)

            # Create a formatted list of aspects
            aspects_list = "\n".join([f"- {aspect}" for aspect in aspects])

            # Instruction for feedback length
            feedback_length = 3
            feedback_instruction = f"Provide concise and actionable feedback for each selected aspect. Limit each section to {feedback_length} sentences."

            # Construct the prompt
            input_prompt = f"""
            You are an expert professional photographer. Please critique the uploaded photo focusing on the following aspects:
            {aspects_list}

            {feedback_instruction}

            Provide three critique areas and three areas for improvement based on the selected aspects.
            Format the response as follows:

            **Critique Areas:**
            1. 
            2. 
            3. 

            **Areas for Improvement:**
            1. 
            2. 
            3. 
            """

            # Get the response from Gemini
            response = get_gemini_response(input_prompt, image_data)

            # Display the response with formatting
            st.subheader("Photo Critique")
            st.write(response)

        except FileNotFoundError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please select exactly 3 aspects for the critique.")