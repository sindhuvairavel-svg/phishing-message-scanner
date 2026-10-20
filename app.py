flask_app_code = """
from flask import Flask, request, jsonify
import joblib
import os

app = Flask(__name__)

# Define paths to saved model artifacts
MODEL_PATH = 'exports/logistic_regression_model.pkl'
VECTORIZER_PATH = 'exports/tfidf_vectorizer.pkl'

# Load model and vectorizer once when server starts
if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    print("Model and Vectorizer loaded successfully!")
else:
    raise FileNotFoundError("Model files not found. Please ensure they are in the exports/ directory.")

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    
    if not data or 'email_text' not in data:
        return jsonify({'error': 'Please provide email_text in request body.'}), 400
        
    email_text = data['email_text']
    
    # Perform prediction
    text_tfidf = vectorizer.transform([email_text])
    prediction = model.predict(text_tfidf)[0]
    probabilities = model.predict_proba(text_tfidf)[0]
    
    category = "Phishing Email" if prediction == 1 else "Safe Email"
    confidence = float(probabilities[prediction])
    
    return jsonify({
        'email_text': email_text,
        'prediction': category,
        'confidence': confidence
    })

if __name__ == '__main__':
    # Run on port 5000
    app.run(host='0.0.0.0', port=5000)
"""

# Save the script to a python file
with open('app.py', 'w') as f:
    f.write(flask_app_code)
  if "__main__" == "__main__";
app.run(debug=True)

print("Flask API application code written successfully to app.py!")
