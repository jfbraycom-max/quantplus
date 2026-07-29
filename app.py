from flask import Flask, render_template_string, jsonify
import threading

app = Flask(__name__)

# Server control state
server_status = {"running": True}

# Mock database rows for testing the UI display
mock_watchlist_data = [
    {"ticker": "AAPL", "name": "Apple Inc.", "score": 8.7, "rating": "BUY", "insight": "Strong cash-flow generation and resilient margins offset hardware headwinds.", "refresh": "2h ago"},
    {"ticker": "MSFT", "name": "Microsoft Corp.", "score": 6.2, "rating": "ALMOST BUY", "insight": "Cloud segment expansion holds steady, but valuation multiples demand tighter entry criteria.", "refresh": "2h ago"},
    {"ticker": "TSLA", "name": "Tesla Inc.", "score": 3.4, "rating": "SELL BEFORE FAILURE", "insight": "Margin compression and tightening liquidity trigger structural risk warnings.", "refresh": "2h ago"}
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Quant Engine — Test UI</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #334155; padding-bottom: 15px; }
        .controls { display: flex; gap: 10px; }
        button { padding: 10px 18px; font-weight: 600; border: none; border-radius: 6px; cursor: pointer; }
        .btn-start { background: #22c55e; color: white; }
        .btn-stop { background: #ef4444; color: white; }
        .status-badge { padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; }
        .status-running { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; }
        .status-stopped { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
        
        table { width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        th, td { padding: 14px 16px; text-align: left; border-bottom: 1px solid #334155; font-size: 0.95rem; }
        th { background: #0f172a; color: #94a3b8; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.05em; }
        tr:hover { background: #273548; cursor: pointer; }
        .badge-buy { color: #4ade80; font-weight: bold; }
        .badge-almost { color: #facc15; font-weight: bold; }
        .badge-sell { color: #f87171; font-weight: bold; }
    </style>
</head>
<body>
<div class="container">
    <header>
        <div>
            <h1>Quant Engine Control Panel</h1>
            <p>Server Status: <span id="status-badge" class="status-badge status-running">RUNNING</span></p>
        </div>
        <div class="controls">
            <button class="btn-start" onclick="toggleServer('start')">Start Server</button>
            <button class="btn-stop" onclick="toggleServer('stop')">Stop Server</button>
        </div>
    </header>

    <h2>Watchlist & Ticker Overview</h2>
    <table>
        <thead>
            <tr>
                <th>Ticker</th>
                <th>Company Name</th>
                <th>Final Score (1-10)</th>
                <th>Rating Classification</th>
                <th>AI Insight Summary (Preview)</th>
                <th>Last Refresh</th>
            </tr>
        </thead>
        <tbody id="watchlist-table">
            {% for item in data %}
            <tr>
                <td><strong>{{ item.ticker }}</strong></td>
                <td>{{ item.name }}</td>
                <td>{{ item.score }}</td>
                <td>
                    <span class="{% if item.rating == 'BUY' %}badge-buy{% elif item.rating == 'ALMOST BUY' %}badge-almost{% else %}badge-sell{% endif %}">
                        {{ item.rating }}
                    </span>
                </td>
                <td style="color: #cbd5e1; max-width: 400px; font-size: 0.9rem;">{{ item.insight }}</td>
                <td style="color: #94a3b8;">{{ item.refresh }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<script>
function toggleServer(action) {
    fetch('/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: action })
    })
    .then(response => response.json())
    .then(data => {
        const badge = document.getElementById('status-badge');
        if (data.status === 'running') {
            badge.className = 'status-badge status-running';
            badge.innerText = 'RUNNING';
        } else {
            badge.className = 'status-badge status-stopped';
            badge.innerText = 'STOPPED';
        }
    });
}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, data=mock_watchlist_data)

@app.route('/control', methods=['POST'])
def control_server():
    from flask import request
    req_data = request.get_json()
    action = req_data.get('action')
    if action == 'start':
        server_status["running"] = True
        return jsonify({"status": "running"})
    elif action == 'stop':
        server_status["running"] = False
        return jsonify({"status": "stopped"})
    return jsonify({"status": "unknown"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
