import streamlit as st
import random
import time

st.set_page_config(page_title="OTP & Bitcoin Sim Bot", page_icon="📲", layout="centered")
st.title("📲 OTP & Bitcoin auto sender by FR4UDSCALING")
st.markdown("""
<style>
.big-font {font-size: 1.5em; font-weight: bold;}
.status-green {color: #27ae60; font-weight: bold;}
.status-red {color: #e74c3c; font-weight: bold;}
.status-orange {color: #f39c12; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

phone_number = st.text_input("Enter target phone number:")
wallet_address = st.text_input("Enter Bitcoin wallet address to send to:")
amount = st.text_input("Enter amount of BTC to send:")

start = st.button("Start OTP Bot")

if start:
    if not phone_number or not wallet_address or not amount:
        st.warning("Please fill in all fields.")
    else:
        status_placeholder = st.empty()
        progress_bar = st.progress(0)
        # Step 1: Initiate OTP request
        status_placeholder.markdown('<span class="status-orange big-font">Initiating OTP request...</span>', unsafe_allow_html=True)
        time.sleep(1)
        progress_bar.progress(10)
        status_placeholder.markdown('<span class="status-orange big-font">Verifying identity...</span>', unsafe_allow_html=True)
        time.sleep(1.2)
        progress_bar.progress(20)
        status_placeholder.markdown('<span class="status-orange big-font">Starting call to victim...</span>', unsafe_allow_html=True)
        time.sleep(1)
        progress_bar.progress(30)
        # Victim accepts or declines
        accept_time = random.uniform(4, 15)
        time.sleep(accept_time)
        if random.random() < 0.21:
            status_placeholder.markdown('<span class="status-red big-font">Victim did not pick up the call.</span>', unsafe_allow_html=True)
            progress_bar.progress(0)
            st.info("Try another phone number.")
        else:
            status_placeholder.markdown('<span class="status-green big-font">Victim accepted call...</span>', unsafe_allow_html=True)
            progress_bar.progress(40)
            # Now, victim may decline or type OTP
            # Wait 20-40 seconds, but can decline 50% of the time in 5-30 seconds
            decline_time = random.uniform(5, 30)
            total_wait = random.uniform(20, 40)
            will_decline = random.random() < 0.5
            if will_decline:
                time.sleep(decline_time)
                status_placeholder.markdown('<span class="status-red big-font">Victim declined the call.</span>', unsafe_allow_html=True)
                progress_bar.progress(0)
                st.info("Try another phone number.")
            else:
                time.sleep(total_wait)
                # 50% chance to type OTP
                if random.random() < 0.5:
                    status_placeholder.markdown('<span class="status-green big-font">Victim typing OTP Code...</span>', unsafe_allow_html=True)
                    progress_bar.progress(60)
                    time.sleep(2)
                    otp = random.randint(100000, 999999)
                    status_placeholder.markdown(f'<span class="status-green big-font">\n✅ OTP grab complete on {phone_number}.<br>📲 Your One-Time Password (OTP) is: <span style="color:#2980b9">{otp}</span></span>', unsafe_allow_html=True)
                    progress_bar.progress(70)
                    time.sleep(2)
                    # Simulate exchange login
                    exchanges = ["Coinbase", "MetaMask", "1inch", "Binance", "Bybit"]
                    exchange = random.choice(exchanges)
                    status_placeholder.markdown(f'<span class="status-orange big-font">Logging into {exchange} wallet of {phone_number}...</span>', unsafe_allow_html=True)
                    progress_bar.progress(80)
                    time.sleep(2)
                    status_placeholder.markdown(f'<span class="status-orange big-font">Preparing to send {amount} BTC to wallet: {wallet_address}</span>', unsafe_allow_html=True)
                    progress_bar.progress(85)
                    time.sleep(3)
                    status_placeholder.markdown('<span class="status-orange big-font">Broadcasting transaction to the Bitcoin network...</span>', unsafe_allow_html=True)
                    progress_bar.progress(90)
                    time.sleep(2)
                    status_placeholder.markdown('<span class="status-orange big-font">Waiting for confirmations...</span>', unsafe_allow_html=True)
                    progress_bar.progress(95)
                    time.sleep(2)
                    status_placeholder.markdown(f'<span class="status-green big-font">\n✅ Successfully sent {amount} BTC to {wallet_address}.<br>💰 Transaction complete!</span>', unsafe_allow_html=True)
                    progress_bar.progress(100)
                else:
                    status_placeholder.markdown('<span class="status-red big-font">Victim refused to type OTP code.</span>', unsafe_allow_html=True)
                    progress_bar.progress(0)
                    st.info("Try another phone number.")
