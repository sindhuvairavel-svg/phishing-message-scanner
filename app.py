import streamlit as st
import pickle

@st.cache_resource
def load_models():
    model = pickle.load(open('exports/logistic_regression_model.pkl', 'rb'))
    vectorizer = pickle.load(open('exports/tfidf_vectorizer.pkl', 'rb'))
    return model, vectorizer

model, vectorizer = load_models()

st.title("🛡️ PhishShift Message Risk Scanner")
st.markdown("**Educational Triage & Decision Support Tool**")

user_message = st.text_area("Enter Email or SMS Message to Scan:")

if st.button("Scan Message"):
    if user_message.strip() != "":
        transformed_text = vectorizer.transform([user_message])
        prediction = model.predict(transformed_text)[0]
        
        st.subheader("Scan Results")
        if prediction == 1 or str(prediction).lower() in ['phish', 'phishing', 'spam']:
            st.error("⚠️ **High Risk:** Potential Phishing or Suspicious Message Detected!")
        else:
            st.success("✅ **Low Risk / Legitimate Message**")
    else:
        st.error("Please enter a valid message text.")
