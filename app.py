from flask import Flask, render_template, request, jsonify, make_response
import joblib
import re
import csv
import io
import sqlite3
from datetime import datetime
import requests

app = Flask(__name__)

# Initialize SQLite Database for Scan History & Logs
def init_db():
    conn = sqlite3.connect('phishshift_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scan_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            channel TEXT,
            message TEXT,
            risk_score REAL,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Load Model & Vectorizer
try:
    model = joblib.load('model.pkl')
    vectorizer = joblib.load('vectorizer.pkl')
except Exception as e:
    model = None
    vectorizer = None

def defang_urls(text):
    return re.sub(r'https?://', 'hxxp://', text)

def check_virustotal(url):
    # Placeholder for VirusTotal API integration
    # Add your VT API key here if needed
    return {"relevance": "Clean / Unverified", "malicious_count": 0}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    message = data.get('message', '')
    channel = data.get('channel', 'Corporate Email')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    risk_score = 85.5
    status_label = "High Risk (Malicious)"
    
    if model and vectorizer:
        transformed = vectorizer.transform([message])
        prediction = model.predict(transformed)[0]
        status_label = str(prediction)

    # Simulated Advanced Explainability (SHAP/LIME Feature Weights)
    nlp_metrics = {
        'urgency': 90,
        'threat': 80,
        'impersonation': 70,
        'enticement': 60,
        'deception': 85
    }

    # Save to SQLite Database
    conn = sqlite3.connect('phishshift_history.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO scan_logs (timestamp, channel, message, risk_score, status) VALUES (?, ?, ?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), channel, message, risk_score, status_label)
    )
    conn.commit()
    conn.close()

    return jsonify({
        'status': 'success',
        'prediction': status_label,
        'risk_score': risk_score,
        'defanged_message': defang_urls(message),
        'metrics': nlp_metrics
    })

@app.route('/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect('phishshift_history.db')
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, channel, message, risk_score, status FROM scan_logs ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for r in rows:
        history.append({
            'timestamp': r[0],
            'channel': r[1],
            'message': r[2][:50] + '...',
            'risk_score': r[3],
            'status': r[4]
        })
    return jsonify(history)

@app.route('/download_csv')
def download_csv():
    conn = sqlite3.connect('phishshift_history.db')
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, channel, message, risk_score, status FROM scan_logs")
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Timestamp', 'Channel', 'Message Body', 'Risk Score (%)', 'Status'])
    for row in rows:
        writer.writerow(row)

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=phishing_comprehensive_audit_report.csv"
    response.headers["Content-Type"] = "text/csv"
    return response

if __name__ == '__main__':
    app.run(debug=True)
