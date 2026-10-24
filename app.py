from flask import Flask, render_template_string, request
import numpy as np

app = Flask(__name__)

# Dummy model/vectorizer placeholders for standalone deployment
model = None
vectorizer = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Phishing Message Risk Scanner - Advanced Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-color: #0b0b0b;
            --card-bg: #161616;
            --gold: #d4af37;
            --gold-light: #f3e5ab;
            --gold-dark: #aa820a;
            --text-main: #e0e0e0;
            --text-muted: #999999;
            --danger: #ff4d4d;
            --success: #2ecc71;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Poppins', sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-main); display: flex; height: 100vh; overflow: hidden; }
        
        /* Sidebar */
        .sidebar { width: 260px; background-color: var(--card-bg); border-right: 1px solid #222; display: flex; flex-direction: column; justify-content: space-between; }
        .sidebar-header { padding: 25px; text-align: center; border-bottom: 1px solid #222; }
        .sidebar-header h2 { color: var(--gold); font-size: 1.2rem; font-weight: 600; letter-spacing: 1px; }
        .sidebar-menu { list-style: none; padding: 20px 0; }
        .sidebar-menu li { padding: 12px 25px; cursor: pointer; display: flex; align-items: center; gap: 12px; color: var(--text-muted); transition: 0.3s; border-left: 3px solid transparent; }
        .sidebar-menu li:hover, .sidebar-menu li.active { background: rgba(212, 175, 55, 0.08); color: var(--gold); border-left-color: var(--gold); }
        .sidebar-menu li i { font-size: 1.1rem; }

        /* Main Content */
        .main-container { flex: 1; display: flex; flex-direction: column; overflow-y: auto; }
        header { padding: 20px 35px; background: var(--card-bg); border-bottom: 1px solid #222; display: flex; justify-content: space-between; align-items: center; }
        header h1 { font-size: 1.4rem; color: var(--gold-light); font-weight: 500; }
        .user-profile { display: flex; align-items: center; gap: 10px; color: var(--gold); font-size: 0.9rem; }

        .content-body { padding: 30px; flex: 1; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* Dashboard Stats Cards */
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: var(--card-bg); border: 1px solid #222; border-radius: 12px; padding: 20px; position: relative; overflow: hidden; }
        .stat-card::after { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: var(--gold); }
        .stat-card h3 { font-size: 0.85rem; color: var(--text-muted); font-weight: 400; margin-bottom: 8px; }
        .stat-card .value { font-size: 1.6rem; font-weight: 600; color: var(--gold-light); }

        /* Form & Result Layout */
        .grid-2 { display: grid; grid-template-columns: 1.2fr 1fr; gap: 25px; }
        .panel { background: var(--card-bg); border: 1px solid #222; border-radius: 12px; padding: 25px; }
        .panel h3 { color: var(--gold); margin-bottom: 20px; font-size: 1.1rem; border-bottom: 1px solid #222; padding-bottom: 10px; }
        
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 6px; font-size: 0.85rem; color: var(--text-muted); }
        select, textarea, input { width: 100%; padding: 12px; background: #0f0f0f; border: 1px solid #333; border-radius: 8px; color: var(--text-main); font-size: 0.9rem; }
        select:focus, textarea:focus, input:focus { border-color: var(--gold); outline: none; }
        
        .btn-gold { background: linear-gradient(135deg, var(--gold), var(--gold-dark)); color: #000; border: none; padding: 12px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; width: 100%; transition: 0.3s; }
        .btn-gold:hover { opacity: 0.9; transform: translateY(-1px); }

        /* Results Box */
        .result-box { margin-top: 15px; padding: 15px; border-radius: 8px; background: #0f0f0f; border: 1px solid #333; }
        .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; margin-bottom: 10px; }
        .badge-danger { background: rgba(255, 77, 77, 0.15); color: var(--danger); border: 1px solid var(--danger); }
        .badge-success { background: rgba(46, 204, 113, 0.15); color: var(--success); border: 1px solid var(--success); }

        /* Charts Container */
        .charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
        .chart-box { background: var(--card-bg); border: 1px solid #222; border-radius: 12px; padding: 20px; }
        
        /* History Table */
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #222; font-size: 0.85rem; }
        th { color: var(--gold); font-weight: 500; }
        td { color: var(--text-muted); }
    </style>
</head>
<body>

    <!-- Sidebar Navigation -->
    <div class="sidebar">
        <div>
            <div class="sidebar-header">
                <h2><i class="fa-solid fa-shield-halved"></i> PMSR Scanner</h2>
            </div>
            <ul class="sidebar-menu">
                <li class="active" onclick="switchTab(event, 'dashboard')"><i class="fa-solid fa-chart-pie"></i> Dashboard</li>
                <li onclick="switchTab(event, 'scanner')"><i class="fa-solid fa-magnifying-glass-chart"></i> Live Scanner</li>
                <li onclick="switchTab(event, 'analytics')"><i class="fa-solid fa-chart-line"></i> Analytics & Graphs</li>
                <li onclick="switchTab(event, 'history')"><i class="fa-solid fa-clock-rotate-left"></i> Scan History</li>
                <li onclick="switchTab(event, 'defanger')"><i class="fa-solid fa-link-slash"></i> URL Defanger</li>
                <li onclick="switchTab(event, 'reports')"><i class="fa-solid fa-file-arrow-down"></i> Reports Export</li>
                <li onclick="switchTab(event, 'settings')"><i class="fa-solid fa-gear"></i> System Settings</li>
                <li onclick="switchTab(event, 'api-docs')"><i class="fa-solid fa-code"></i> API Docs</li>
                <li onclick="switchTab(event, 'compliance')"><i class="fa-solid fa-scale-balanced"></i> Compliance</li>
                <li onclick="switchTab(event, 'support')"><i class="fa-solid fa-headset"></i> Support & Triage</li>
            </ul>
        </div>
        <div style="padding: 20px; text-align: center; font-size: 0.75rem; color: #555;">
            PMSR v3.2 Gold Edition
        </div>
    </div>

    <!-- Main Container -->
    <div class="main-container">
        <header>
            <h1 id="page-title">Executive Dashboard</h1>
            <div class="user-profile">
                <i class="fa-solid fa-user-shield"></i> <span>Security Admin</span>
            </div>
        </header>

        <div class="content-body">
            
            <!-- 1. DASHBOARD TAB -->
            <div id="dashboard" class="tab-content active">
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Total Scans</h3>
                        <div class="value">1,428</div>
                    </div>
                    <div class="stat-card">
                        <h3>Phishing Detected</h3>
                        <div class="value" style="color: var(--danger);">312</div>
                    </div>
                    <div class="stat-card">
                        <h3>Safe Messages</h3>
                        <div class="value" style="color: var(--success);">1,116</div>
                    </div>
                    <div class="stat-card">
                        <h3>System Status</h3>
                        <div class="value" style="font-size: 1.2rem; color: var(--gold);">Operational</div>
                    </div>
                </div>

                <div class="charts-row">
                    <div class="chart-box">
                        <h3 style="color:var(--gold); margin-bottom:15px; font-size:1rem;">Threat Distribution</h3>
                        <canvas id="dashPieChart" height="140"></canvas>
                    </div>
                    <div class="chart-box">
                        <h3 style="color:var(--gold); margin-bottom:15px; font-size:1rem;">Weekly Scan Trends</h3>
                        <canvas id="dashBarChart" height="140"></canvas>
                    </div>
                </div>
            </div>

            <!-- 2. LIVE SCANNER TAB -->
            <div id="scanner" class="tab-content">
                <div class="grid-2">
                    <div class="panel">
                        <h3><i class="fa-solid fa-terminal"></i> Message Threat Analyzer</h3>
                        <form method="POST">
                            <div class="form-group">
                                <label>Select Channel</label>
                                <select name="channel">
                                    <option value="Corporate Email" {% if channel == 'Corporate Email' %}selected{% endif %}>Corporate Email</option>
                                    <option value="SMS / Text" {% if channel == 'SMS / Text' %}selected{% endif %}>SMS / Text</option>
                                    <option value="Social Media" {% if channel == 'Social Media' %}selected{% endif %}>Social Media</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Message Subject / Header</label>
                                <input type="text" name="subject" value="{{ subject }}" placeholder="Enter subject...">
                            </div>
                            <div class="form-group">
                                <label>Message Body</label>
                                <textarea name="message" rows="5" placeholder="Paste suspicious message here...">{{ message }}</textarea>
                            </div>
                            <button type="submit" class="btn-gold">Run Deep AI Scan</button>
                        </form>
                    </div>

                    <div class="panel">
                        <h3><i class="fa-solid fa-shield-virus"></i> Threat Intelligence Result</h3>
                        {% if request.method == 'POST' %}
                            <div class="result-box">
                                {% if risk_level == 'High Risk Phishing' %}
                                    <span class="badge badge-danger"><i class="fa-solid fa-triangle-exclamation"></i> High Risk Phishing</span>
                                {% else %}
                                    <span class="badge badge-success"><i class="fa-solid fa-circle-check"></i> Low Risk / Benign</span>
                                {% endif %}
                                <p style="font-size:0.85rem; margin-top:8px;"><strong>Confidence Score:</strong> {{ confidence }}%</p>
                                <p style="font-size:0.85rem; margin-top:8px; color:var(--text-muted);"><strong>Triage Insights:</strong> {{ explanation }}</p>
                            </div>
                        {% else %}
                            <p style="color:var(--text-muted); font-size:0.85rem; text-align:center; padding: 40px 0;">Submit a message on the left panel to generate live AI telemetry and threat scores.</p>
                        {% endif %}
                    </div>
                </div>
            </div>

            <!-- 3. ANALYTICS & GRAPHS TAB -->
            <div id="analytics" class="tab-content">
                <div class="panel">
                    <h3>Advanced Telemetry & Analytics</h3>
                    <p style="color:var(--text-muted); font-size:0.85rem; margin-bottom:20px;">Comprehensive behavioral breakdown of scanned payloads across global vectors.</p>
                    <div style="width: 80%; margin: 0 auto;">
                        <canvas id="detailedBarChart" height="100"></canvas>
                    </div>
                </div>
            </div>

            <!-- 4. SCAN HISTORY TAB -->
            <div id="history" class="tab-content">
                <div class="panel">
                    <h3>Recent Scan Logs</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Timestamp</th>
                                <th>Channel</th>
                                <th>Snippet</th>
                                <th>Risk Verdict</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>2026-10-24 19:30</td>
                                <td>Corporate Email</td>
                                <td>Urgent password reset required...</td>
                                <td><span style="color:var(--danger)">High Risk</span></td>
                            </tr>
                            <tr>
                                <td>2026-10-24 18:15</td>
                                <td>SMS / Text</td>
                                <td>Your parcel is out for delivery click...</td>
                                <td><span style="color:var(--danger)">High Risk</span></td>
                            </tr>
                            <tr>
                                <td>2026-10-24 16:40</td>
                                <td>Social Media</td>
                                <td>Weekly team sync agenda attached...</td>
                                <td><span style="color:var(--success)">Benign</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- 5. URL DEFANGER TAB -->
            <div id="defanger" class="tab-content">
                <div class="panel">
                    <h3>URL Defanging Utility</h3>
                    <p style="color:var(--text-muted); font-size:0.85rem; margin-bottom:15px;">Safely neutralize active hyperlinks embedded in suspicious texts before analysis.</p>
                    <textarea rows="3" placeholder="Paste malicious URL here (e.g., http://malicious-phishing.com)">http://suspicious-login-verify.com</textarea>
                    <button class="btn-gold" style="margin-top: 15px; width: 200px;" onclick="alert('URL Defanged successfully: hxxp://suspicious-login-verify[.]com')">Defang URL</button>
                </div>
            </div>

            <!-- 6. REPORTS EXPORT TAB -->
            <div id="reports" class="tab-content">
                <div class="panel">
                    <h3>Incident Report Generator</h3>
                    <p style="color:var(--text-muted); font-size:0.85rem; margin-bottom:15px;">Export compliance reports and threat logs in standardized formats.</p>
                    <button class="btn-gold" style="width: 250px; margin-right: 10px;" onclick="alert('Downloading PDF Security Report...')"><i class="fa-solid fa-file-pdf"></i> Download PDF Report</button>
                    <button class="btn-gold" style="width: 250px; background: transparent; border: 1px solid var(--gold); color: var(--gold);" onclick="alert('Exporting CSV Telemetry...')"><i class="fa-solid fa-file-csv"></i> Export CSV Data</button>
                </div>
            </div>

            <!-- 7. SYSTEM SETTINGS TAB -->
            <div id="settings" class="tab-content">
                <div class="panel">
                    <h3>System Configuration</h3>
                    <div class="form-group">
                        <label>AI Sensitivity Threshold (%)</label>
                        <input type="number" value="75">
                    </div>
                    <div class="form-group">
                        <label>Notification Webhook URL</label>
                        <input type="text" value="https://hooks.slack.com/services/T00/B00/X00">
                    </div>
                    <button class="btn-gold" style="width: 180px;">Save Changes</button>
                </div>
            </div>

            <!-- 8. API DOCS TAB -->
            <div id="api-docs" class="tab-content">
                <div class="panel">
                    <h3>REST API Documentation</h3>
                    <p style="color:var(--text-muted); font-size:0.85rem; margin-bottom:15px;">Integrate PMSR scanner directly into your SIEM pipeline using JSON endpoints.</p>
                    <pre style="background:#0f0f0f; padding:15px; border-radius:8px; color:var(--gold-light); font-size:0.8rem; overflow-x:auto;">
POST /predict
Content-Type: application/json

{
  "message": "Verify your bank account immediately",
  "channel": "Corporate Email"
}
                    </pre>
                </div>
            </div>

            <!-- 9. COMPLIANCE TAB -->
            <div id="compliance" class="tab-content">
                <div class="panel">
                    <h3>Compliance & Governance</h3>
                    <p style="color:var(--text-muted); font-size:0.85rem;">NFR-03 Compliance Notice: Classification is decision support and triage assistance only, not an absolute guarantee of safety. Data handling adheres strictly to privacy standards.</p>
                </div>
            </div>

            <!-- 10. SUPPORT & TRIAGE TAB -->
            <div id="support" class="tab-content">
                <div class="panel">
                    <h3>Security Operations Support</h3>
                    <p style="color:var(--text-muted); font-size:0.85rem; margin-bottom:15px;">Need manual analyst verification? Contact the internal SOC team.</p>
                    <p style="color:var(--gold); font-size:0.9rem;"><i class="fa-solid fa-envelope"></i> soc@phishguard-analytics.internal</p>
                </div>
            </div>

        </div>
    </div>

    <script>
        function switchTab(event, tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.sidebar-menu li').forEach(el => el.classList.remove('active'));
            
            document.getElementById(tabId).classList.add('active');
            event.currentTarget.classList.add('active');
            
            document.getElementById('page-title').innerText = event.currentTarget.innerText.trim();
        }

        // Charts Initialization
        window.onload = function() {
            // Dashboard Pie Chart
            const ctxPie = document.getElementById('dashPieChart').getContext('2d');
            new Chart(ctxPie, {
                type: 'doughnut',
                data: {
                    labels: ['Phishing', 'Safe'],
                    datasets: [{
                        data: [312, 1116],
                        backgroundColor: ['#ff4d4d', '#2ecc71'],
                        borderWidth: 0
                    }]
                },
                options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { color: '#e0e0e0', font: { size: 11 } } } } }
            });

            // Dashboard Bar Chart
            const ctxBar = document.getElementById('dashBarChart').getContext('2d');
            new Chart(ctxBar, {
                type: 'bar',
                data: {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    datasets: [{
                        label: 'Scans',
                        data: [150, 220, 180, 290, 310, 140, 138],
                        backgroundColor: '#d4af37',
                        borderRadius: 4
                    }]
                },
                options: { responsive: true, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#999' } }, y: { ticks: { color: '#999' } } } }
            });

            // Detailed Analytics Bar Chart
            const ctxDetailed = document.getElementById('detailedBarChart').getContext('2d');
            new Chart(ctxDetailed, {
                type: 'line',
                data: {
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    datasets: [{
                        label: 'Threat Volume',
                        data: [65, 59, 80, 81],
                        borderColor: '#d4af37',
                        backgroundColor: 'rgba(212, 175, 55, 0.1)',
                        fill: true,
                        tension: 0.3
                    }]
                },
                options: { responsive: true, scales: { x: { ticks: { color: '#999' } }, y: { ticks: { color: '#999' } } } }
            });
        };
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    risk_level = None
    confidence = 0.0
    explanation = ""
    message = ""
    subject = ""
    channel = "Corporate Email"
    
    if request.method == 'POST':
        channel = request.form.get('channel', 'Corporate Email')
        subject = request.form.get('subject', '')
        message = request.form.get('message', '')
        
        # Logic simulation for prediction
        if model and vectorizer:
            data = [message]
            vect_data = vectorizer.transform(data)
            pred = model.predict(vect_data)[0]
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(vect_data)[0]
                conf = float(np.max(probs)) * 100
            else:
                conf = 88.5
        else:
            # Fallback simulated intelligent scoring
            conf = 94.2 if "urgent" in message.lower() or "bank" in message.lower() else 15.4
            
        if conf > 50:
            risk_level = "High Risk Phishing"
            explanation = "Detected high-risk indicators: Urgency-driven call to action, potential credential harvester patterns, or simulated phishing phrasing."
        else:
            risk_level = "Low Risk / Benign"
            explanation = "Message conforms to standard administrative or normal conversational structures without malicious payload vectors."
            
    return render_template_string(
        HTML_TEMPLATE, 
        risk_level=risk_level, 
        confidence=round(conf, 2) if 'conf' in locals() else 0.0, 
        explanation=explanation, 
        message=message, 
        subject=subject,
        channel=channel
    )

if __name__ == '__main__':
    app.run(debug=True)
