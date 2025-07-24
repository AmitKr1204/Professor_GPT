import google.generativeai as genai
import streamlit as st
import requests
from streamlit_lottie import st_lottie
from fpdf import FPDF
import tempfile
import os
from dotenv import load_dotenv
load_dotenv()

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

# Use API key in both places
headers = {
    "authorization": api_key,
    "Content-Type": "application/json"
}

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")
pre_prompt = "Teach me the following concept: "

if "show_translator" not in st.session_state:
    st.session_state.show_translator = False

# ========== STREAMLIT SETTINGS ==========
st.set_page_config(page_title="ProfessorGPT", page_icon="🎓", layout="centered")

# ========== LOAD ANIMATION ==========
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lecture_animation = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_kkflmtur.json")

# ========== STYLING ==========
st.markdown("""
    <style>
    /* Global app styling */
    .stApp {
        background: linear-gradient(to bottom right, #e3f2fd, #fdf6e3);
        padding-bottom: 50px;
        font-family: 'Segoe UI', sans-serif;
    }

    .title-container {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(90deg, #3f87a6, #ebf8e1, #f69d3c);
        border-radius: 12px;
        color: black;
        box-shadow: 0 0 15px rgba(0,0,0,0.15);
    }

    .lecture-box {
        background: linear-gradient(to right, #fff9e6, #ffe9a1);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.2);
        margin-top: 25px;
        font-size: 1.1rem;
        line-height: 1.7;
        font-family: 'Georgia', serif;
        color: #222;
        border-left: 8px solid #ff9800;
        transition: all 0.3s ease-in-out;
    }

    .stTextInput > div > div > input {
        border: 2px solid #3f87a6 !important;
        border-radius: 12px !important;
        padding: 12px !important;
        box-shadow: 0 0 5px rgba(0,0,0,0.1);
        background-color: #ffffffcc;
    }

    textarea {
        background-color: #f5faff !important;
        color: #111111 !important;
        border-radius: 10px !important;
        padding: 10px;
        font-family: 'Segoe UI', sans-serif;
        font-size: 16px;
        border: 1px solid #3f87a6 !important;
    }

    label {
        color: #333333 !important;
        font-weight: 600;
        font-size: 16px;
    }

    .stButton button {
        background-color: #3f87a6;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .stButton button:hover {
        background-color: #2f6a8b;
    }

    .stDownloadButton button {
        background-color: #4caf50;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 16px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }

    .stDownloadButton button:hover {
        background-color: #45a049;
    }

    /* Dark Mode Support */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background: linear-gradient(to bottom right, #121212, #1e1e1e);
        }

        .title-container {
            background: linear-gradient(90deg, #1f1f1f, #2a2a2a, #3a3a3a);
            color: #f5f5f5;
        }

        .lecture-box {
            background: #2c2c2c;
            color: #f5f5f5;
            border-left: 8px solid #ff9800;
        }

        label {
            color: #f5f5f5 !important;
        }

        textarea {
            background-color: #1e1e1e !important;
            color: #f5f5f5 !important;
            border: 1px solid #888 !important;
        }

        .stTextInput > div > div > input {
            background-color: #2a2a2a !important;
            color: white !important;
            border: 2px solid #888 !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# ========== HEADER ==========
st.markdown('<div class="title-container"><h1>🎓 ProfessorGPT</h1><p>Your personal AI lecturer</p></div>', unsafe_allow_html=True)
st.divider()

# ========== INPUT SECTION==========
with st.form("lecture_form"):
    prompt = st.text_input("🔍 What topic would you like to learn?")
    submitted = st.form_submit_button("📘 Teach Me!")

# ========== PDF HELPER ==========
import unicodedata

def clean_text(text):
    replacements = {
        '\u2013': '-',  
        '\u2014': '-',  
        '\u2018': "'",  
        '\u2019': "'",  
        '\u201c': '"',  
        '\u201d': '"',  
        '\u2022': '*',  
        '\u00a0': ' ',  
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def generate_pdf(text, topic):
    text = clean_text(text)
    topic = clean_text(topic)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Topic: {topic}\n\n{text}")
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name


# ========== MAIN FUNCTION ==========
if submitted and prompt:
    with st.spinner("Preparing your lecture..."):
        try:
            response = model.generate_content(pre_prompt + prompt)

            if response and response.candidates:
                parts = response.candidates[0].content.parts
                if parts:
                    lecture_text = parts[0].text
                    st_lottie(lecture_animation, height=200, key="teaching")
                    st.markdown('<div class="lecture-box">' + lecture_text + '</div>', unsafe_allow_html=True)

                    # Generate and download PDF
                    pdf_path = generate_pdf(lecture_text, prompt)
                    with open(pdf_path, "rb") as file:
                        st.download_button(
                            label="📥 Download Lecture as PDF",
                            data=file,
                            file_name=f"{prompt.replace(' ', '_')}_lecture.pdf",
                            mime="application/pdf"
                        )
                        
                else:
                    st.warning("⚠️ The response was empty.")
            else:
                st.error("❌ No response received from Gemini.")
        except Exception as e:
            st.error(f"Error: {e}")
    st.snow()



# ================= TRANSLATOR SECTION =================
st.divider()
if st.button("🌐 Use Translator Tool"):
    st.session_state.show_translator = True

if st.session_state.show_translator:
    st.markdown('<div class="title-container"><h2>🌐 Language Translator</h2><p>Translate text between languages using AI</p></div>', unsafe_allow_html=True)

    # Language options
    languages = ["English", "Hindi", "French", "Spanish", "German", "Chinese", "Japanese", "Tamil", "Telugu", "Bengali"]

    col1, col2 = st.columns(2)
    with col1:
        source_lang = st.selectbox("From Language", languages, index=0)
    with col2:
        target_lang = st.selectbox("To Language", languages, index=1)

    text_to_translate = st.text_area("🔤 Enter text to translate")

    if st.button("🌍 Translate"):
        if not text_to_translate.strip():
            st.warning("Please enter some text.")
        elif source_lang == target_lang:
            st.info("Source and target languages are the same.")
        else:
            with st.spinner("Translating..."):
                try:
                    translate_prompt = f"Translate the following text from {source_lang} to {target_lang}:\n\n{text_to_translate}"
                    response = model.generate_content(translate_prompt)
                    if response and response.candidates:
                        translated_text = response.candidates[0].content.parts[0].text
                        st.markdown('<div class="lecture-box">' + translated_text + '</div>', unsafe_allow_html=True)
                    else:
                        st.error("❌ No translation result.")
                except Exception as e:
                    st.error(f"Error: {e}")


