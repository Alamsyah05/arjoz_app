import streamlit as st
# --- PAGE CONFIG (MUST BE FIRST) ---

st.set_page_config(
    page_title="Dashboard Inventory",
    page_icon=":material/inventory:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INITIALIZE SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''

# --- LOGIN FUNCTION ---


def login(username, password):
    # Ganti dengan logika autentikasi Anda
    # Contoh sederhana:
    users = {
        "admin": "admin123",
        "user": "user123"
    }

    if username in users and users[username] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        return True
    return False

# --- LOGOUT FUNCTION ---


def logout():
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.rerun()

# --- LOGIN PAGE ---


def show_login_page():

    # Custom CSS untuk login page
    st.markdown("""
    <style>
        /* Hide ALL streamlit elements for login page */
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        header {visibility: hidden !important;}
        [data-testid="stSidebar"] {display: none !important;}
        [data-testid="collapsedControl"] {display: none !important;}
        .stDeployButton {display: none !important;}
        
        /* Background styling - Lapangan Bulu Tangkis */
        .stApp {
            background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), 
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
    </style>
    """, unsafe_allow_html=True)

    # Create centered container
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Logo and title
        st.markdown("""
        <div class="logo-title">
            <h1>ARJOZZ</h1>
            <p class="welcome-text"><br>SISTEM INFORMASI PENCATATAN PERSEDIAAN</p>
        </div>
        """, unsafe_allow_html=True)

        # Login form
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "Username", placeholder="Enter your username")
            password = st.text_input(
                "Password", type="password", placeholder="Enter your password")

            submit = st.form_submit_button("Log in")

            if submit:
                if username and password:
                    if login(username, password):
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please fill in all fields")

        # Info credentials
        st.markdown("""
        <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin-top: 20px;">
            <p style="color: #e8f5e9; font-size: 0.85em; text-align: center; margin: 0;">
                <strong>Demo Credentials:</strong><br>
                Username: admin | Password: admin123<br>
                Username: user | Password: user123
            </p>
        </div>
        """, unsafe_allow_html=True)

# --- MAIN APPLICATION ---


def show_main_app():
    # Custom CSS for sidebar
    st.markdown("""
        <style>
            /* Sidebar gradient background */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #54744B 0%, #9EDA8D 100%);
            }
            
            /* Sidebar text color */
            [data-testid="stSidebar"] * {
                color: white !important;
            }
            
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
                color: white !important;
            }
            
            /* Logout button styling */
            [data-testid="stSidebar"] .stButton > button {
                background-color: #d32f2f !important;
                color: white !important;
                border: none !important;
                border-radius: 8px !important;
                padding: 10px 20px !important;
                font-size: 1em !important;
                font-weight: 600 !important;
                width: 100% !important;
                transition: all 0.3s ease !important;
                margin-top: 5px !important;
            }
            
            [data-testid="stSidebar"] .stButton > button:hover {
                background-color: #b71c1c !important;
                box-shadow: 0 4px 12px rgba(211, 47, 47, 0.4) !important;
                transform: translateY(-2px);
            }
            
            [data-testid="stSidebar"] .stButton > button:active {
                transform: translateY(0px);
            }
            
            /* User info styling */
            .user-info {
                background: rgba(255, 255, 255, 0.15);
                padding: 12px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 8px;
                margin-top: 8px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .user-info p {
                margin: 0;
                font-size: 0.95em;
                font-weight: 500;
                line-height: 1.4;
            }
            
            /* Reduce spacing in sidebar */
            [data-testid="stSidebar"] hr {
                margin-top: 0.5rem !important;
                margin-bottom: 0.5rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("<hr style='margin: 0.3rem 0;'>", unsafe_allow_html=True)

        # User info dengan styling yang bagus
        st.markdown(f"""
            <div class="user-info">
                <p>👤 <strong>Logged in as:</strong><br>{st.session_state.username}</p>
            </div>
        """, unsafe_allow_html=True)

        # Logout button
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            logout()

    # --- PAGE SETUP ---
    page1_dashboard = st.Page(
        "pages/page1_dashboard.py",
        title="Dashboard",
        icon=":material/bar_chart:",
        default=True,
    )

    page21_stokbahanbaku = st.Page(
        "pages/page21_stokbahanbaku.py",
        title="Stok Bahan Baku",
        icon=":material/box:",
    )

    page22_stokbarangjadi = st.Page(
        "pages/page22_stokbarangjadi.py",
        title="Stok Barang Jadi",
        icon=":material/box:",
    )

    page31_bahanbakumasuk = st.Page(
        "pages/page31_bahanbakumasuk.py",
        title="Bahan Baku Masuk",
        icon=":material/smart_toy:",
    )

    page32_bahanbakukeluar = st.Page(
        "pages/page32_bahanbakukeluar.py",
        title="Bahan Baku Keluar",
        icon=":material/smart_toy:",
    )

    page41_produkjadimasuk = st.Page(
        "pages/page41_produkjadimasuk.py",
        title="Produk Jadi Masuk",
        icon=":material/smart_toy:",
    )

    page42_produkjadikeluar = st.Page(
        "pages/page42_produkjadikeluar.py",
        title="Produk Jadi Keluar",
        icon=":material/smart_toy:",
    )

    page61_ss_rop_eoq = st.Page(
        "pages/page61_ss_rop_eoq.py",
        title="Safety Stock, ROP, & EOQ",
        icon=":material/smart_toy:",
    )

    # --- NAVIGATION SETUP [WITH SECTIONS]---
    pg = st.navigation(
        {
            "Dashboard": [page1_dashboard],
            "Pengendalian Persediaan": [page61_ss_rop_eoq],
            "Stok": [page21_stokbahanbaku, page22_stokbarangjadi],
            "Bahan Baku": [page31_bahanbakumasuk, page32_bahanbakukeluar],
            "Produk Jadi": [page41_produkjadimasuk, page42_produkjadikeluar],
        }
    )

    # --- RUN NAVIGATION ---
    pg.run()


# --- MAIN LOGIC ---
if st.session_state.logged_in:
    show_main_app()
else:
    show_login_page()
