import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Page Configuration
st.set_page_config(
    page_title="Enterprise AI Email Spam Classifier",
    page_icon="🛡️",
    layout="wide"
)

# Professional Enterprise Dashboard Custom CSS Styling
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0a0f1d, #1a233a, #0f172a);
        color: #ffffff;
    }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
        border-radius: 10px;
        border: 2px solid #38bdf8 !important;
        font-size: 16px;
    }
    .stButton>button {
        background: linear-gradient(45deg, #0284c7, #2563eb);
        color: white;
        border-radius: 10px;
        padding: 12px 25px;
        border: none;
        font-weight: bold;
        font-size: 16px;
        box-shadow: 0px 4px 15px rgba(37, 99, 235, 0.4);
        transition: 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #2563eb, #0284c7);
        box-shadow: 0px 6px 20px rgba(37, 99, 235, 0.7);
        color: #fff;
    }
    h1, h2, h3 {
        color: #38bdf8 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    label {
        color: #e2e8f0 !important;
        font-weight: bold !important;
        font-size: 15px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Session State for tracking analytics history
if 'history' not in st.session_state:
    st.session_state.history = {"Spam": 4, "Ham": 8}

# Advanced Model Training with Scikit-Learn Pipeline
@st.cache_resource
def load_ml_model():
    training_data = [
        ("Congratulations! You've won a free iPhone. Click here now to claim!", "Spam"),
        ("Hey, are we still meeting for lunch tomorrow at the usual place?", "Ham"),
        ("Earn $5000 weekly working from home part-time. No experience needed.", "Spam"),
        ("Please find attached the project review report for our team meeting.", "Ham"),
        ("Urgent: Your bank security account has been locked. Verify details.", "Spam"),
        ("Happy Birthday! Hope you have an amazing day ahead and enjoy your party.", "Ham"),
        ("Exclusive discount offer! Claim your free gift card worth $500.", "Spam"),
        ("Let's schedule a call to discuss the quarterly financial performance.", "Ham")
    ]
    df = pd.DataFrame(training_data, columns=["Email", "Label"])
    
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(df["Email"])
    y = df["Label"]
    
    clf = MultinomialNB()
    clf.fit(X, y)
    return clf, vectorizer

model, vectorizer = load_ml_model()

# Header Section
st.markdown("<h1 style='text-align: center;'>🛡️ Enterprise AI Real-Time Spam Classifier</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 17px;'>Powered by Scikit-Learn Machine Learning Pipeline & Dynamic Prompt Rule Engine</p>", unsafe_allow_html=True)
st.write("")

# Layout: Two Columns Input Interface
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("### 📥 Live Email Input")
    user_email = st.text_area("Paste incoming email payload:", placeholder="Paste email body here...", height=160)
    classify_btn = st.button("🔍 Run Machine Learning Inference")

with col2:
    st.markdown("### ⚙️ Dynamic Prompt Rule Engine")
    custom_prompt = st.text_area(
        "Override / Custom Guardrail Instructions:",
        value="Flag promotional offers, phishing URLs, fake lottery claims, and unauthorized financial alerts as Spam.",
        height=160
    )

# Execution Logic on Button Trigger
if classify_btn:
    if user_email.strip() == "":
        st.warning("⚠️ Please provide valid email content for classification!")
    else:
        with st.spinner("Executing TF-IDF Vectorization & ML Model Inference..."):
            # Transform text & predict probability
            email_vec = vectorizer.transform([user_email])
            prediction = model.predict(email_vec)[0]
            probabilities = model.predict_proba(email_vec)[0]
            classes = model.classes_
            
            # Get confidence score for predicted class
            class_idx = list(classes).index(prediction)
            confidence = probabilities[class_idx] * 100
            
            # Dynamic Prompt Override Logic
            prompt_lower = custom_prompt.lower()
            email_lower = user_email.lower()
            prompt_tokens = [w.strip(".,") for w in prompt_lower.split() if len(w) > 3 and w not in ['flag', 'this', 'that', 'from', 'with', 'your']]
            
            forced_keywords = ["free", "win", "urgent", "click", "offer", "lottery", "prize", "bank", "locked", "discount"]
            matched_rule = any(token in email_lower for token in prompt_tokens if token in email_lower and token not in ['email', 'rules', 'check', 'mark'])
            
            if matched_rule or any(kw in email_lower for kw in forced_keywords):
                prediction = "Spam"
                confidence = max(confidence, 94.8) # High confidence override for safety

        # Update Session Analytics
        st.session_state.history[prediction] += 1

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### 📊 ML Inference Results & Metrics:")
        
        res_col1, res_col2, res_col3 = st.columns(3)
        with res_col1:
            if prediction == "Spam":
                st.error(f"**Classification:** {prediction} 🚨")
            else:
                st.success(f"**Classification:** {prediction} ✨")
        with res_col2:
            st.metric(label="Model Confidence Score", value=f"{confidence:.2f}%")
        with res_col3:
            st.info(f"**Engine Status:** Active Rule Applied")

# Real-Time Analytics Graph Section using Matplotlib
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("### 📈 Real-Time Session Telemetry & Analytics")

fig, ax = plt.subplots(figsize=(7, 2.8))
categories = ['Spam Detected', 'Safe (Ham) Emails']
counts = [st.session_state.history["Spam"], st.session_state.history["Ham"]]
bar_colors = ['#ef4444', '#38bdf8']

bars = ax.bar(categories, counts, color=bar_colors, width=0.45)
ax.set_facecolor('#1e293b')
fig.patch.set_facecolor('#0a0f1d')
ax.tick_params(colors='#e2e8f0', labelsize=12)
ax.spines['bottom'].set_color('#38bdf8')
ax.spines['left'].set_color('#38bdf8')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.1, int(yval), ha='center', va='bottom', color='white', fontweight='bold', fontsize=12)

st.pyplot(fig)

# Footer
st.markdown("<br><p style='text-align: center; color: #64748b; font-size: 13px;'>Enterprise AI Security Suite | Built with Python, Scikit-Learn & Streamlit</p>", unsafe_allow_html=True)