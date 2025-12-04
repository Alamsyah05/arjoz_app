import streamlit as st

# Page config
st.set_page_config(page_title="ARIOGET Login", layout="wide")

# Custom CSS untuk styling
st.markdown("""
<style>
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Background styling */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)),
                    url('https://images.unsplash.com/photo-1626224583764-f87db24ac4ea') center/cover no-repeat;
        background-attachment: fixed;
    }
    
    /* Login container */
    .login-container {
        background: rgba(46, 125, 50, 0.95);
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        max-width: 400px;
        margin: 100px auto;
    }
    
    /* Logo and title */
    .logo-title {
        text-align: center;
        color: white;
        margin-bottom: 30px;
    }
    
    .logo-title h1 {
        font-size: 2.5em;
        font-weight: bold;
        margin: 0;
        letter-spacing: 2px;
    }
    
    .welcome-text {
        text-align: center;
        color: #e8f5e9;
        font-size: 0.9em;
        margin-top: 10px;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-size: 1em !important;
    }
    
    /* Labels */
    .stTextInput > label {
        color: white !important;
        font-weight: 500 !important;
        font-size: 0.95em !important;
    }
    
    /* Button */
    .stButton > button {
        background-color: rgba(56, 142, 60, 1) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px !important;
        width: 100% !important;
        font-size: 1.1em !important;
        font-weight: 600 !important;
        margin-top: 20px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: rgba(67, 160, 71, 1) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    }
    
    /* Forgot password link */
    .forgot-password {
        text-align: right;
        margin-top: -10px;
        margin-bottom: 10px;
    }
    
    .forgot-password a {
        color: #e8f5e9;
        text-decoration: none;
        font-size: 0.85em;
    }
    
    .forgot-password a:hover {
        color: white;
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# Create centered container
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Logo and title
    st.markdown("""
    <div class="logo-title">
        <h1>🎾 ARIOGET</h1>
        <p class="welcome-text">Hey Buddy,<br>Welcome to ARIOGET</p>
    </div>
    """, unsafe_allow_html=True)

    # Login form
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input(
            "Password", type="password", placeholder="Enter your password")

        st.markdown("""
        <div class="forgot-password">
            <a href="#" onclick="alert('Please contact admin to reset password')">Forgot your password?</a>
        </div>
        """, unsafe_allow_html=True)

        submit = st.form_submit_button("Log in")

        if submit:
            if username and password:
                # Tambahkan logika autentikasi di sini
                if username == "admin" and password == "admin123":
                    st.success("✅ Login successful!")
                    st.balloons()
                    # Redirect atau set session state di sini
                else:
                    st.error("❌ Invalid username or password")
            else:
                st.warning("⚠️ Please fill in all fields")

# Footer
st.markdown("""
<div style="position: fixed; bottom: 20px; left: 0; right: 0; text-align: center; color: white; font-size: 0.8em;">
    <p>© 2024 ARIOGET. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
