import hashlib
import streamlit as st

# --- Login credentials ---
CREDENTIALS = {
    "mtcarella": "Absolut98!",
    "admin": "testtest"
}

def login():
    st.title("🔒 Login Required")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        if username in CREDENTIALS and CREDENTIALS[username] == password:
            st.session_state["authenticated"] = True
        else:
            st.error("❌ Invalid credentials")

# --- Login Gate ---
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login()
    st.stop()


# Custom CSS to apply brand colors
st.markdown("""
    <style>
    .stApp {
        background-color: #f5f5f5;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #003366;
    }

    /* Light Blue Button Styling */
    .stButton>button {
        background-color: #cce6ff;  /* light blue */
        color: #003366;
        border: 1px solid #99ccff;
        padding: 0.5em 1em;
        border-radius: 6px;
        font-weight: bold;
    }

    .stButton>button:hover {
        background-color: #b3d9ff;
        color: #002244;
        border-color: #80bfff;
    }

    .stFileUploader {
        background-color: #e0f0ff;
        padding: 1em;
        border-radius: 5px;
    }

    .stSuccess {
        background-color: #dff0d8;
        color: #3c763d;
    }

    .stError {
        background-color: #f2dede;
        color: #a94442;
    }

    .stWarning {
        background-color: #fcf8e3;
        color: #8a6d3b;
    }

    .stInfo {
        background-color: #d9edf7;
        color: #31708f;
    }
    </style>
    """, unsafe_allow_html=True)


import pandas as pd
from thefuzz import fuzz
from PIL import Image

# Load and display logo
import base64
from PIL import Image

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

logo_base64 = get_base64_image("evident-logo.png")

st.markdown(
    f"""
    <div style='text-align: center; margin-bottom: 20px;'>
        <img src='data:image/png;base64,{logo_base64}' width='250'>
    </div>
    """,
    unsafe_allow_html=True
)



st.markdown("""
    <div style='text-align: center; line-height: 1.2; margin-bottom: 30px;'>
        <h1 style='font-size: 2.5em; color: #003366; margin: 0;'>Evident Edge's</h1>
        <h2 style='font-size: 1.5em; color: #003366; margin: 0;'>Sales Assignment Tool</h2>
    </div>
    """, unsafe_allow_html=True)


st.subheader("🔍 Enter Client Info (at least one group)")

with st.expander("Attorney"):
    a_first = st.text_input("Attorney First Name").strip().lower()
    a_last = st.text_input("Attorney Last Name").strip().lower()

with st.expander("Realtor"):
    r_first = st.text_input("Realtor First Name").strip().lower()
    r_last = st.text_input("Realtor Last Name").strip().lower()

with st.expander("Lender"):
    l_first = st.text_input("Lender First Name").strip().lower()
    l_last = st.text_input("Lender Last Name").strip().lower()

attorney_filled = a_first or a_last
realtor_filled = r_first or r_last
lender_filled = l_first or l_last

# This button appears immediately after input
if st.button("Find Match"):
    if not (attorney_filled or realtor_filled or lender_filled):
        st.warning("⚠️ Please fill out at least one group (Attorney, Realtor, or Lender).")
    else:
        matches = []

        for _, row in st.session_state["data"].iterrows():
            row_type = str(row.get("Type", "")).strip().lower()
            row_first = str(row.get("First Name", "")).lower()
            row_last = str(row.get("Last Name", "")).lower()
            score = 0

            if row_type == "realtor" and (r_first or r_last):
                if r_first:
                    score += fuzz.partial_ratio(r_first, row_first)
                if r_last:
                    score += fuzz.partial_ratio(r_last, row_last)
                matches.append((score / ((r_first != "") + (r_last != "")), row, "Realtor"))

            elif row_type == "attorney" and (a_first or a_last):
                if a_first:
                    score += fuzz.partial_ratio(a_first, row_first)
                if a_last:
                    score += fuzz.partial_ratio(a_last, row_last)
                matches.append((score / ((a_first != "") + (a_last != "")), row, "Attorney"))

            elif row_type == "lender" and (l_first or l_last):
                if l_first:
                    score += fuzz.partial_ratio(l_first, row_first)
                if l_last:
                    score += fuzz.partial_ratio(l_last, row_last)
                matches.append((score / ((l_first != "") + (l_last != "")), row, "Lender"))

        strong_matches = [(score, row, role) for score, row, role in matches if score >= 80]

        if not strong_matches:
            st.error("❌ No strong match found.")
        else:
            type_priority = {"realtor": 1, "attorney": 2, "lender": 3}
            strong_matches.sort(key=lambda x: type_priority[x[1]['Type'].lower()])

            main_match = strong_matches[0]
            primary_salesperson = main_match[1]['Salesperson']
            primary_role = main_match[2]

            st.success(f"🎯 Assigned Salesperson: {primary_salesperson} (matched as {primary_role})")

            if len(strong_matches) > 1:
                st.info("🔁 Possible Crossover Matches:")
                for score, row, role in strong_matches[1:]:
                    st.markdown(f"- **{row['Salesperson']}** (matched as {role} with {int(score)}% confidence)")

st.divider()
st.subheader("📁 Manage Spreadsheet")

import hashlib

@st.cache_data
def load_default_data():
    return pd.read_excel("clients.xlsx")

def get_file_hash(uploaded_file):
    return hashlib.md5(uploaded_file.read()).hexdigest()

# Set session defaults
if "data" not in st.session_state:
    st.session_state["data"] = load_default_data()
    st.session_state["file_label"] = "📁 Using default file: clients.xlsx"
    st.session_state["file_hash"] = None

uploaded_file = st.file_uploader("Upload updated Excel (optional)", type=["xlsx"])

if uploaded_file:
    file_hash = get_file_hash(uploaded_file)
    uploaded_file.seek(0)

    if file_hash != st.session_state.get("file_hash"):
        st.session_state["data"] = pd.read_excel(uploaded_file)
        st.session_state["file_label"] = f"📂 Using uploaded file: {uploaded_file.name}"
        st.session_state["file_hash"] = file_hash
        st.success("✅ New file detected and loaded.")
    else:
        st.info("ℹ️ Same file as before — no reload needed.")

if st.button("🔄 Reset to Default File"):
    st.session_state["data"] = load_default_data()
    st.session_state["file_label"] = "📁 Using default file: clients.xlsx"
    st.session_state["file_hash"] = None
    st.success("✅ Reset complete.")

st.markdown(f"**{st.session_state['file_label']}**")
