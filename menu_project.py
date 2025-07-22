import streamlit as st
import os
import time
import cv2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
import getpass
import tempfile
from linkedin_post_bot import run_linkedin_automation
# Page configuration
st.set_page_config(
    page_title="Digital Services Hub",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .main {
        padding-top: 0rem;
    }
    
    /* Enhanced main header */
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 3rem;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 100;
        bottom: 0;
        background: url('data:image/svg+xml,<svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"><g fill="none" fill-rule="evenodd"><g fill="%23ffffff" fill-opacity="0.1"><circle cx="30" cy="30" r="4"/></g></svg>');
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .main-header h1 {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        font-size: 1.3rem;
        font-weight: 300;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }
    
    /* Enhanced service cards grid */
    .services-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
        padding: 0 1rem;
    }
    
    /* Enhanced service card */
    .service-card {
        background: linear-gradient(145deg, #2d3748 0%, #4a5568 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 20px;
        border: 1px solid #4a5568;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        cursor: pointer;
    }
    
    .service-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        transition: height 0.3s ease;
    }
    
    .service-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 50px rgba(102, 126, 234, 0.15);
        border-color: #667eea;
    }
    
    .service-card:hover::before {
        height: 6px;
    }
    
    .service-card h3 {
        font-size: 1.5rem;
        font-weight: 600;
        color: white;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .service-card p {
        color: #e2e8f0;
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    
    .service-card .service-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    /* Features section */
    .features-section {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        padding: 4rem 2rem;
        border-radius: 20px;
        margin: 3rem 0;
        text-align: center;
    }
    
    .features-section h2 {
        font-size: 2.5rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 2rem;
    }
    
    .features-list {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 2rem;
        margin-top: 2rem;
    }
    
    .feature-item {
        background: transparent;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
        transition: transform 0.3s ease;
    }
    
    .feature-item:hover {
        transform: translateY(-5px);
    }
    
    .feature-item .icon {
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    
    /* Success and error messages */
    .success-message {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
        animation: slideIn 0.5s ease;
    }
    
    .error-message {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
        animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Enhanced buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar enhancements */
    .css-1d391kg {
        padding-top: 2rem;
    }
    
    /* Custom selectbox styling */
    .stSelectbox > div > div {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%);
        border: 2px solid #e1e5e9;
        border-radius: 10px;
        transition: border-color 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Welcome screen enhancements */
    .welcome-container {
        max-width: 800px;
        margin: 0 auto;
        text-align: center;
    }
    /* Push selectbox down */
    .css-1d391kg {
    padding-top: 5rem !important;
    }

    /* Alternative - target the selectbox specifically */
    div[data-testid="stSelectbox"] {
    margin-top: 10rem;
    }
    .welcome-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%);
        padding: 3rem;
        border-radius: 20px;
        border: 1px solid #e1e5e9;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        margin: 2rem 0;
    }
    
    .welcome-card h2 {
        font-size: 2.5rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 1.5rem;
    }
    
    .welcome-card ul {
        text-align: left;
        max-width: 400px;
        margin: 2rem auto;
        padding: 0;
        list-style: none;
    }
    
    .welcome-card li {
        padding: 0.8rem 0;
        font-size: 1.1rem;
        color: #4a5568;
        border-bottom: 1px solid #e2e8f0;
        transition: color 0.3s ease;
    }
    
    .welcome-card li:hover {
        color: #667eea;
    }
    
    .welcome-card li:last-child {
        border-bottom: none;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2.5rem;
        }
        
        .main-header p {
            font-size: 1.1rem;
        }
        
        .services-grid {
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }
        
        .service-card {
            padding: 2rem;
        }
        
        .features-section {
            padding: 3rem 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_service' not in st.session_state:
    st.session_state.selected_service = None

def main():
    # Header
    st.markdown("""
    <div class="main-header" style="background: transparent; padding: 2.5rem; border-radius: 20px; text-align: center;">
        <h1>Digital Services Hub</h1>
        <p>Your all-in-one platform for digital communication and automation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Services Menu")
    st.sidebar.markdown("---")
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    services = [
        "📱 Send SMS",
        "📞 Make Phone Call", 
        "💬 WhatsApp Message",
        "📧 Send Email",
        "🐦 Twitter Post",
        "📸 Capture Photo",
        "📄 PDF Summary Generator",
        "📢 LinkedIn Post Automation"
    ]
    
    selected_service = st.sidebar.selectbox("Choose a service:", ["Select a service..."] + services )
    
    if selected_service != "Select a service...":
        st.session_state.selected_service = selected_service
        
        # Main content area
        if selected_service == "📱 Send SMS":
            sms_service()
        elif selected_service == "📞 Make Phone Call":
            call_service()
        elif selected_service == "💬 WhatsApp Message":
            whatsapp_service()
        elif selected_service == "📧 Send Email":
            email_service()
        elif selected_service == "🐦 Twitter Post":
            twitter_service()
        elif selected_service == "📸 Capture Photo":
            photo_service()
        elif selected_service == "📄 PDF Summary Generator":
            pdf_service()
        elif selected_service == "📢 LinkedIn Post Automation":
            linkedin_service()
    else:
        # Welcome screen
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div class="service-card">
                <h2>Welcome to Digital Services Hub</h2>
                <p>Select a service from the sidebar to get started.</p>
                <br>
                <h3>Available Services:</h3>
                <ul>
                    <li>📱 Send SMS messages</li>
                    <li>📞 Make phone calls</li>
                    <li>💬 Send WhatsApp messages</li>
                    <li>📧 Send emails</li>
                    <li>🐦 Post on Twitter</li>
                    <li>📸 Capture photos</li>
                    <li>📄 Generate PDF summaries</li>
                    <li>📢 LinkedIn Post Automation</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    def show_homepage():
        """Enhanced homepage with better UI and service cards"""
        st.markdown("""
        <div class="welcome-container">
            <div class="welcome-card">
                <h2>Welcome to Your Digital Command Center</h2>
                <p style="font-size: 1.2rem; color: #4a5568; margin-bottom: 2rem;">
                    Streamline your digital communications and automate routine tasks with our integrated service platform.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Services grid
        st.markdown("""
        <div class="services-grid">
            <div class="service-card">
                <div class="service-icon">📱</div>
                <h3>SMS & Voice Services</h3>
                <p>Send instant text messages and initiate phone calls worldwide using Twilio's reliable infrastructure.</p>
                <div style="margin-top: auto;">
                    <small style="color: #667eea; font-weight: 500;">✨ Instant delivery</small>
                </div>
            </div>
            
            <div class="service-card">
                <div class="service-icon">💬</div>
                <h3>WhatsApp Integration</h3>
                <p>Connect with your audience through WhatsApp's business platform for personal and professional messaging.</p>
                <div style="margin-top: auto;">
                    <small style="color: #667eea; font-weight: 500;">✨ Business ready</small>
                </div>
            </div>
            
            <div class="service-card">
                <div class="service-icon">📧</div>
                <h3>Email & Social Media</h3>
                <p>Automate email campaigns and publish content on Twitter with secure, authenticated connections.</p>
                <div style="margin-top: auto;">
                    <small style="color: #667eea; font-weight: 500;">✨ Multi-platform</small>
                </div>
            </div>
            
            <div class="service-card">
                <div class="service-icon">🤖</div>
                <h3>AI-Powered Content</h3>
                <p>Generate intelligent summaries from PDFs and create engaging LinkedIn posts using advanced AI models.</p>
                <div style="margin-top: auto;">
                    <small style="color: #667eea; font-weight: 500;">✨ AI enhanced</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Features section
        st.markdown("""
        <div class="features-section">
            <h2>Why Choose Our Platform?</h2>
            <div class="features-list">
                <div class="feature-item">
                    <div class="icon">🔒</div>
                    <h4>Secure & Reliable</h4>
                    <p>Enterprise-grade security with encrypted communications</p>
                </div>
                <div class="feature-item">
                    <div class="icon">⚡</div>
                    <h4>Lightning Fast</h4>
                    <p>Optimized performance for instant message delivery</p>
                </div>
                <div class="feature-item">
                    <div class="icon">🎯</div>
                    <h4>Easy to Use</h4>
                    <p>Intuitive interface designed for all skill levels</p>
                </div>
                <div class="feature-item">
                    <div class="icon">📊</div>
                    <h4>Analytics Ready</h4>
                    <p>Track performance and engagement metrics</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Call to action
        st.markdown("""
        <div style="text-align: center; margin: 3rem 0;">
            <h3 style="color: #2d3748; margin-bottom: 1rem;">Ready to Get Started?</h3>
            <p style="color: #4a5568; margin-bottom: 2rem;">Select a service from the sidebar to begin your digital automation journey.</p>
        </div>
        """, unsafe_allow_html=True)
def linkedin_service():
    st.header("📢 LinkedIn Post Automation")
    st.markdown("**Generate and Post Content on LinkedIn Automatically using AI.**")

    prompt = st.text_area("Enter the topic for your LinkedIn post", placeholder="E.g. My journey learning Python automation...")
    image_file = st.file_uploader("Upload an image to attach (optional)", type=["png", "jpg", "jpeg"])

    if st.button("Generate and Post"):
        if prompt:
            with st.spinner("Generating content and posting to LinkedIn..."):
                img_path = None
                if image_file:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                        tmp_img.write(image_file.read())
                        img_path = tmp_img.name

                try:
                    post_content = run_linkedin_automation(prompt, img_path)
                    st.markdown(f"""
                    <div class="success-message">
                        ✅ LinkedIn post published successfully!
                    </div>
                    """, unsafe_allow_html=True)
                    st.text_area("Generated Post Content:", post_content, height=200)
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-message">
                        ❌ Failed to post on LinkedIn: {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Please enter a topic.")

def sms_service():
    st.header("📱 SMS Service")
    
    with st.form("sms_form"):
        st.markdown("**Send SMS Message**")
        
        phone_number = st.text_input("Recipient Phone Number", placeholder="+1234567890")
        message_body = st.text_area("Message", placeholder="Enter your message here...")
        
        submitted = st.form_submit_button("Send SMS")
        
        if submitted:
            if phone_number and message_body:
                try:
                    # Twilio SMS code
                    account_sid = "ACb8b1df65d79a7fb5bddb7c2ae9967636"
                    auth_token = "ef93d245d60f601622b3e50f14c8a8c8"
                    twilio_phone = "+14847490866"
                    
                    client = Client(account_sid, auth_token)
                    
                    message = client.messages.create(
                        body=message_body,
                        from_=twilio_phone,
                        to=phone_number
                    )
                    
                    st.markdown(f"""
                    <div class="success-message">
                        ✅ SMS sent successfully! Message SID: {message.sid}
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-message">
                        ❌ Error sending SMS: {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("Please fill in all fields")

def call_service():
    st.header("📞 Phone Call Service")
    
    with st.form("call_form"):
        st.markdown("**Make Phone Call**")
        
        phone_number = st.text_input("Recipient Phone Number", placeholder="+1234567890")
        call_message = st.text_area("Call Message", placeholder="Enter the message to be spoken...")
        
        submitted = st.form_submit_button("Make Call")
        
        if submitted:
            if phone_number and call_message:
                try:
                    # Twilio call code
                    account_sid = 'ACb8b1df65d79a7fb5bddb7c2ae9967636'
                    auth_token = 'ef93d245d60f601622b3e50f14c8a8c8'
                    twilio_number = '+14847490866'
                    
                    client = Client(account_sid, auth_token)
                    
                    call = client.calls.create(
                        to=phone_number,
                        from_=twilio_number,
                        twiml=f'<Response><Say>{call_message}<Q23332/Say></Response>'
                    )
                    
                    st.markdown(f"""
                    <div class="success-message">
                        ✅ Call initiated successfully! Call SID: {call.sid}
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-message">
                        ❌ Error making call: {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("Please fill in all fields")

def whatsapp_service():
    st.header("💬 WhatsApp Service")
    
    with st.form("whatsapp_form"):
        st.markdown("**Send WhatsApp Message**")
        
        phone_number = st.text_input("Recipient Phone Number", placeholder="+1234567890")
        message_body = st.text_area("Message", placeholder="Enter your WhatsApp message...")
        
        submitted = st.form_submit_button("Send WhatsApp")
        
        if submitted:
            if phone_number and message_body:
                try:
                    # Twilio WhatsApp code
                    account_sid = 'ACb8b1df65d79a7fb5bddb7c2ae9967636'
                    auth_token = 'ef93d245d60f601622b3e50f14c8a8c8'
                    twilio_whatsapp_number = 'whatsapp:+14155238886'
                    recipient_number = f'whatsapp:{phone_number}'
                    
                    client = Client(account_sid, auth_token)
                    
                    message = client.messages.create(
                        from_=twilio_whatsapp_number,
                        body=message_body,
                        to=recipient_number
                    )
                    
                    st.markdown(f"""
                    <div class="success-message">
                        ✅ WhatsApp message sent successfully! Message SID: {message.sid}
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-message">
                        ❌ Error sending WhatsApp message: {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("Please fill in all fields")

def email_service():
    st.header("📧 Email Service")
    
    with st.form("email_form"):
        st.markdown("**Send Email**")
        
        sender_email = st.text_input("Your Email", value="krishsharma1037@gmail.com")
        sender_password = st.text_input("App Password", type="password", value="bvgkpvaqlqavzpuz")
        receiver_email = st.text_input("Recipient Email", placeholder="recipient@example.com")
        subject = st.text_input("Subject", placeholder="Enter email subject")
        body = st.text_area("Message", placeholder="Enter your email message...")
        
        submitted = st.form_submit_button("Send Email")
        
        if submitted:
            if sender_email and sender_password and receiver_email and subject and body:
                try:
                    # Email sending code
                    message = MIMEMultipart()
                    message["From"] = sender_email
                    message["To"] = receiver_email
                    message["Subject"] = subject
                    
                    message.attach(MIMEText(body, "plain"))
                    
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, receiver_email, message.as_string())
                    server.quit()
                    
                    st.markdown("""
                    <div class="success-message">
                        ✅ Email sent successfully!
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-message">
                        ❌ Error sending email: {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("Please fill in all fields")

def twitter_service():
    st.header("🐦 Twitter Service")
    
    with st.form("twitter_form"):
        st.markdown("**Post on Twitter**")
        
        username = st.text_input("Twitter Username/Email", value="krishsharma1037@gmail.com")
        password = st.text_input("Twitter Password", type="password")
        tweet_content = st.text_area("Tweet Content", placeholder="What's happening?")
        
        submitted = st.form_submit_button("Post Tweet")
        
        if submitted:
            if username and password and tweet_content:
                try:
                    # Twitter posting code (simplified for demo)
                    with st.spinner("Posting tweet..."):
                        driver = webdriver.Chrome()
                        driver.get("https://twitter.com/login")
                        
                        wait = WebDriverWait(driver, 20)
                        
                        # Login
                        username_field = wait.until(EC.presence_of_element_located((By.NAME, "text")))
                        username_field.send_keys(username)
                        username_field.send_keys(Keys.RETURN)
                        time.sleep(3)
                        
                        password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
                        password_field.send_keys(password)
                        password_field.send_keys(Keys.RETURN)
                        time.sleep(5)
                        
                        # Tweet
                        tweet_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Tweet text']")))
                        tweet_box.click()
                        tweet_box.send_keys(tweet_content)
                        
                        tweet_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='tweetButtonInline']")))
                        tweet_button.click()
                        
                        time.sleep(5)
                        driver.quit()
                    
                    st.markdown("""
                    <div class="success-message">
                        ✅ Tweet posted successfully!
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-message">
                        ❌ Error posting tweet: {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("Please fill in all fields")

def photo_service():
    st.header("📸 Photo Capture Service")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Capture Photo"):
            try:
                camera = cv2.VideoCapture(0)
                if not camera.isOpened():
                    st.error("Error: Camera cannot be opened")
                    return
                
                ret, frame = camera.read()
                if ret:
                    image_name = "captured_image.jpg"
                    cv2.imwrite(image_name, frame)
                    camera.release()
                    cv2.destroyAllWindows()
                    
                    st.markdown("""
                    <div class="success-message">
                        ✅ Photo captured successfully!
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display captured image
                    st.image(image_name, caption="Captured Photo", use_column_width=True)
                else:
                    st.error("Error reading frame from camera")
                    
            except Exception as e:
                st.markdown(f"""
                <div class="error-message">
                    ❌ Error capturing photo: {str(e)}
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        **Instructions:**
        1. Click the "Capture Photo" button
        2. Allow camera permissions if prompted
        3. The photo will be automatically captured and saved
        4. The captured image will be displayed below
        """)

def pdf_service():
    st.header("📄 PDF Summary Generator")
    
    # Set up Google API key
    os.environ["GOOGLE_API_KEY"] = "AIzaSyDZjyc-P0o1BBdEJXUNmoUDubQDWKyUfCI"
    
    uploaded_file = st.file_uploader("Upload PDF file", type="pdf")
    
    if uploaded_file is not None:
        query = st.text_input("Enter your question about the PDF", 
                             value="Give me a summary of the pdf in bullet points.")
        
        if st.button("Generate Summary"):
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_file_path = tmp_file.name
                
                with st.spinner("Processing PDF..."):
                    # Load and process PDF
                    loader = PyPDFLoader(tmp_file_path)
                    documents = loader.load()
                    
                    # Split text
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=1000, 
                        chunk_overlap=200
                    )
                    docs = text_splitter.split_documents(documents)
                    
                    # Initialize LLM
                    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
                    
                    # Create QA chain
                    chain = load_qa_chain(llm, chain_type="stuff")
                    
                    # Generate response
                    response = chain.run(input_documents=docs, question=query)
                    
                    st.markdown("### Summary:")
                    st.markdown(response)
                
                # Clean up temporary file
                os.unlink(tmp_file_path)
                
            except Exception as e:
                st.markdown(f"""
                <div class="error-message">
                    ❌ Error processing PDF: {str(e)}
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()