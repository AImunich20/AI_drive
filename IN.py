# IN.py
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# ✅ ตัวแปรสถานะที่ใช้ข้ามไฟล์ (main จะอ่านค่านี้)
shared_state = {"value": 1}  # 1 = ทำงาน, 2 = หยุด

@app.route("/webhook", methods=['POST'])
def receive_webhook():
    try:
        data = request.get_json()
        events = data.get('events', [])
        for event in events:
            if event.get("type") == "message":
                message_type = event['message'].get('type')
                if message_type == "text":
                    text = event['message'].get('text').strip().lower()
                    print(f"[IN] ได้รับข้อความ: {text}")

                    if text == "function car":
                        shared_state["value"] = 2
                        return jsonify({"result": "stopped"}), 200
                    elif text == "function sleep":
                        shared_state["value"] = 1
                        return jsonify({"result": "running"}), 200

        return jsonify({"status": "no_command"}), 200
    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

def IN():
    app.run(host='0.0.0.0', port=4000)

if __name__ == "__main__":
    IN()