import streamlit as st
import random
import time
from pymongo import MongoClient
import hashlib
from datetime import datetime, timedelta
import requests

# Initialize MongoDB connection
@st.cache_resource
def init_mongodb():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        # Test the connection
        client.admin.command('ping')
        return db
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}")
        return None

# KeyAuth functions
def hash_key(key):
    return hashlib.sha256(key.encode()).hexdigest()

def verify_key(key):
    db = init_mongodb()
    if db is None:
        return False
    try:
        hashed_key = hash_key(key)
        key_doc = db[COLLECTION_KEYS].find_one({"hashed_key": hashed_key, "active": True})
        if not key_doc:
            return False
        # Check expiration
        expires_at = key_doc.get("expires_at")
        if expires_at and datetime.now() > expires_at:
            return False
        # Log IP and timestamp
        log_key_login(key)
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

def add_key_to_db(key, duration):
    db = init_mongodb()
    if db is None:
        return False
    try:
        hashed_key = hash_key(key)
        now = datetime.now()
        if duration == "1 day":
            expires_at = now + timedelta(days=1)
        elif duration == "1 week":
            expires_at = now + timedelta(weeks=1)
        elif duration == "1 month":
            expires_at = now + timedelta(days=30)
        elif duration == "lifetime":
            expires_at = None
        else:
            expires_at = None
        db[COLLECTION_KEYS].insert_one({
            "hashed_key": hashed_key,
            "plain_key": key,  # Store the plain key for admin viewing
            "active": True,
            "created_at": now,
            "expires_at": expires_at
        })
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

# Number tracking functions
def is_number_called(phone_number):
    db = init_mongodb()
    if db is None:
        return False
    
    try:
        return db[COLLECTION_NUMBERS].find_one({"phone_number": phone_number}) is not None
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

def mark_number_called(phone_number, status):
    db = init_mongodb()
    if db is None:
        return False
    
    try:
        db[COLLECTION_NUMBERS].insert_one({
            "phone_number": phone_number,
            "status": status,  # "accepted", "declined", "no_pickup", "no_otp"
            "called_at": datetime.now()
        })
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

def get_all_keys():
    db = init_mongodb()
    if db is None:
        return []
    try:
        return list(db[COLLECTION_KEYS].find())
    except Exception as e:
        st.error(f"Database error: {e}")
        return []

def delete_key_by_id(key_id):
    db = init_mongodb()
    if db is None:
        return False
    try:
        db[COLLECTION_KEYS].delete_one({'_id': key_id})
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

def log_key_login(key):
    db = init_mongodb()
    if db is None:
        return
    try:
        # Get IP address
        ip = None
        try:
            ip = requests.get('https://api.ipify.org').text
        except Exception:
            ip = 'unknown'
        now = datetime.now()
        hashed_key = hash_key(key)
        db[COLLECTION_KEYS].update_one(
            {"hashed_key": hashed_key},
            {"$push": {"login_history": {"ip": ip, "timestamp": now}}}
        )
    except Exception as e:
        st.error(f"Database error: {e}")

# Page configuration
st.set_page_config(
    page_title="OTP & Bitcoin Sim Bot", 
    page_icon="📲", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-green {color: #27ae60; font-weight: bold; font-size: 1.2em;}
    .status-red {color: #e74c3c; font-weight: bold; font-size: 1.2em;}
    .status-orange {color: #f39c12; font-weight: bold; font-size: 1.2em;}
    .error-box {
        background: #fee;
        border: 1px solid #fcc;
        border-radius: 5px;
        padding: 1rem;
        color: #c33;
        margin: 1rem 0;
    }
    .success-box {
        background: #efe;
        border: 1px solid #cfc;
        border-radius: 5px;
        padding: 1rem;
        color: #3c3;
        margin: 1rem 0;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #5a6fd8 0%, #6a4190 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
# Add session state for admin panel visibility and password
if 'show_admin_panel' not in st.session_state:
    st.session_state.show_admin_panel = False
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False

# --- ADMIN BUTTON AND INLINE ADMIN PANEL (only show if not logged in) ---
if not st.session_state.get('authenticated', False):
    admin_btn_placeholder = st.empty()
    if admin_btn_placeholder.button("🔧 Admin Panel", key="admin_panel_btn"):
        st.session_state.show_admin_panel = True
        st.session_state.admin_authenticated = False

if st.session_state.show_admin_panel:
    # Hide Streamlit sidebar and hamburger menu when admin panel is open
    st.markdown('''
        <style>
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"] {
            display: none !important;
        }
        header {visibility: hidden;}
        </style>
    ''', unsafe_allow_html=True)
    st.markdown('---')
    x_col, content_col = st.columns([1, 8])
    with x_col:
        if st.button("✖", key="close_admin_panel", help="Close admin panel"):
            st.session_state.show_admin_panel = False
            st.session_state.admin_authenticated = False
    with content_col:
        if not st.session_state.admin_authenticated:
            st.markdown('<h4>Admin Password</h4>', unsafe_allow_html=True)
            admin_pw = st.text_input("Admin Password:", type="password", key="admin_pw_modal")
            if st.button("Unlock Admin Panel"):
                if admin_pw == ADMIN_PASSWORD:
                    st.session_state.admin_authenticated = True
                else:
                    st.error("❌ Incorrect admin password!")
        else:
            st.markdown('<h4>Key Management</h4>', unsafe_allow_html=True)
            new_key = st.text_input("New License Key:", type="password", key="admin_new_key")
            duration = st.selectbox("Key Duration:", ["1 day", "1 week", "1 month", "lifetime"], key="admin_duration")
            if st.button("Add Key", key="admin_add_key_btn"):
                if not new_key:
                    st.warning("⚠️ Please enter a key!")
                else:
                    if add_key_to_db(new_key, duration):
                        st.success(f"✅ Key added successfully! Duration: {duration}")
                    else:
                        st.error("❌ Failed to add key!")
            st.markdown("---")
            st.markdown('<h5>All Keys</h5>', unsafe_allow_html=True)
            keys = get_all_keys()
            for key in keys:
                key_label = f"Key: {key.get('plain_key', 'N/A')} | Expires: {key.get('expires_at').strftime('%Y-%m-%d %H:%M') if key.get('expires_at') else 'Lifetime'} | Active: {'✅' if key.get('active') else '❌'} | Created: {key.get('created_at').strftime('%Y-%m-%d')}"
                with st.expander(key_label, expanded=False):
                    login_history = key.get('login_history', [])
                    if login_history:
                        st.markdown('**Login History:**')
                        for event in login_history:
                            st.write(f"- {event.get('ip', 'unknown')} at {event.get('timestamp').strftime('%Y-%m-%d %H:%M:%S') if event.get('timestamp') else ''}")
                    else:
                        st.write("No login history.")
                    if st.button("🗑️ Delete", key=f"delete_{key['_id']}"):
                        if delete_key_by_id(key['_id']):
                            st.success("Key deleted!")
                            st.rerun()
    st.markdown('---')

# Login page
if not st.session_state.authenticated:
    st.markdown('<div class="main-header"><h1>🔐 Login</h1><p>Enter your license key to access the OTP & Bitcoin Sim Bot</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    key = st.text_input("License Key:", type="password", placeholder="Enter your license key here...")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔑 Login", use_container_width=True):
            if key:
                if verify_key(key):
                    st.session_state.authenticated = True
                    st.success("✅ Authentication successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid license key!")
            else:
                st.warning("⚠️ Please enter a license key!")
    # Admin section for adding keys (now with password protection)
    # The new admin modal/panel UI is already implemented above with session state and should be the only admin UI present.
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# Main application (only accessible after authentication)
st.markdown('<div class="main-header"><h1>📲 OTP & Bitcoin Sim Bot by FR4UDSCALING</h1></div>', unsafe_allow_html=True)

# Logout button
if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.rerun()

# Main form
with st.container():
    phone_number = st.text_input("📞 Enter target phone number:")
    wallet_address = st.text_input("💳 Enter Bitcoin wallet address to send to:")
    amount = st.text_input("💰 Enter amount of BTC to send:")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        start = st.button("🚀 Start OTP Bot", use_container_width=True)

if start:
    if not phone_number or not wallet_address or not amount:
        st.warning("⚠️ Please fill in all fields.")
    else:
        # Check if number was already called
        if is_number_called(phone_number):
            st.markdown('<div class="error-box">❌ This number has already been called and cannot be used again!</div>', unsafe_allow_html=True)
        else:
            status_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            # Step 1: Initiate OTP request
            status_placeholder.markdown('<span class="status-orange">🔄 Initiating OTP request...</span>', unsafe_allow_html=True)
            time.sleep(1)
            progress_bar.progress(10)
            
            status_placeholder.markdown('<span class="status-orange">🔍 Verifying identity...</span>', unsafe_allow_html=True)
            time.sleep(1.2)
            progress_bar.progress(20)
            
            status_placeholder.markdown('<span class="status-orange">📞 Starting call to victim...</span>', unsafe_allow_html=True)
            time.sleep(1)
            progress_bar.progress(30)
            
            # Victim accepts or declines
            accept_time = random.uniform(4, 15)
            time.sleep(accept_time)
            
            if random.random() < 0.21:
                status_placeholder.markdown('<span class="status-red">❌ Victim did not pick up the call.</span>', unsafe_allow_html=True)
                mark_number_called(phone_number, "no_pickup")
                progress_bar.progress(0)
                st.info("💡 Try another phone number.")
            else:
                status_placeholder.markdown('<span class="status-green">✅ Victim accepted call...</span>', unsafe_allow_html=True)
                progress_bar.progress(40)
                
                # Now, victim may decline or type OTP
                decline_time = random.uniform(5, 30)
                total_wait = random.uniform(20, 40)
                will_decline = random.random() < 0.5
                
                if will_decline:
                    time.sleep(decline_time)
                    status_placeholder.markdown('<span class="status-red">❌ Victim declined the call.</span>', unsafe_allow_html=True)
                    mark_number_called(phone_number, "declined")
                    progress_bar.progress(0)
                    st.info("💡 Try another phone number.")
                else:
                    time.sleep(total_wait)
                    
                    # 50% chance to type OTP
                    if random.random() < 0.5:
                        status_placeholder.markdown('<span class="status-green">⌨️ Victim typing OTP Code...</span>', unsafe_allow_html=True)
                        progress_bar.progress(60)
                        time.sleep(2)
                        
                        otp = random.randint(100000, 999999)
                        status_placeholder.markdown(f'<span class="status-green">✅ OTP grab complete on {phone_number}<br>📲 Your One-Time Password (OTP) is: <span style="color:#2980b9; font-size: 1.5em;">{otp}</span></span>', unsafe_allow_html=True)
                        mark_number_called(phone_number, "accepted")
                        progress_bar.progress(70)
                        time.sleep(2)
                        
                        # Simulate exchange login
                        exchanges = ["Coinbase", "MetaMask", "1inch", "Binance", "Bybit"]
                        exchange = random.choice(exchanges)
                        status_placeholder.markdown(f'<span class="status-orange">🔐 Logging into {exchange} wallet of {phone_number}...</span>', unsafe_allow_html=True)
                        progress_bar.progress(80)
                        time.sleep(2)
                        
                        status_placeholder.markdown(f'<span class="status-orange">💸 Preparing to send {amount} BTC to wallet: {wallet_address}</span>', unsafe_allow_html=True)
                        progress_bar.progress(85)
                        time.sleep(3)
                        
                        status_placeholder.markdown('<span class="status-orange">🌐 Broadcasting transaction to the Bitcoin network...</span>', unsafe_allow_html=True)
                        progress_bar.progress(90)
                        time.sleep(2)
                        
                        status_placeholder.markdown('<span class="status-orange">⏳ Waiting for confirmations...</span>', unsafe_allow_html=True)
                        progress_bar.progress(95)
                        time.sleep(2)
                        
                        status_placeholder.markdown(f'<span class="status-green">✅ Successfully sent {amount} BTC to {wallet_address}<br>💰 Transaction complete!</span>', unsafe_allow_html=True)
                        progress_bar.progress(100)
                        
                        st.markdown('<div class="success-box">🎉 Successfully grabbed that nigga!</div>', unsafe_allow_html=True)
                    else:
                        status_placeholder.markdown('<span class="status-red">❌ Victim refused to type OTP code.</span>', unsafe_allow_html=True)
                        mark_number_called(phone_number, "no_otp")
                        progress_bar.progress(0)
                        st.info("💡 Try another phone number.")
