import os
from flask import Flask, request, abort
import json
import hashlib
import hmac
import base64
import requests

app = Flask(__name__)

# ตั้งค่า LINE Messaging API
CHANNEL_SECRET = '039de94944ffc302a88d1190049ee0cf'
CHANNEL_ACCESS_TOKEN = 'qysZ8/Onq8YQsQf/BWLWhxJUxXhZuihx9mKukM+KfZF/SWVoem6o8a9tL17dB0tkbbuEc2blcjkn+EJIopmOQlpIofynYFcngbArqAVyLvNHZtckKISAQC+P3JjZPbRqYKG8Dn99ZlcGwlRr9nThdQdB04t89/1O/w1cDnyilFU='
LINE_API_PUSH_URL = 'https://api.line.me/v2/bot/message/push'

# ตั้งค่าพื้นฐาน
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
LINE_USER_ID = "Uc4e322ac25cee130bb2cf3e2ce06d2db"

# ตรวจสอบลายเซ็นจาก LINE
def verify_signature(request):
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    hash = hmac.new(CHANNEL_SECRET.encode('utf-8'), body.encode('utf-8'), hashlib.sha256).digest()
    computed_signature = base64.b64encode(hash).decode()
    return hmac.compare_digest(computed_signature, signature)

# ฟังก์ชันส่งข้อความแบบ push
def push_message(text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    data = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text": text}]
    }
    requests.post(LINE_API_PUSH_URL, headers=headers, json=data)

# ฟังก์ชันส่งภาพแบบ push
def push_image(image_url, preview_url=None):
    if preview_url is None:
        preview_url = image_url
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    data = {
        "to": LINE_USER_ID,
        "messages": [
            {
                "type": "image",
                "originalContentUrl": image_url,
                "previewImageUrl": preview_url
            }
        ]
    }
    requests.post(LINE_API_PUSH_URL, headers=headers, json=data)

# รับ webhook จาก LINE → ส่งต่อ
@app.route("/webhook", methods=['POST'])
def webhook():
    if not verify_signature(request):
        abort(400)

    data = json.loads(request.get_data(as_text=True))

    try:
        forward_url = 'https://in-natthanat.as2.pitunnel.net/webhook'
        headers = {'Content-Type': 'application/json'}
        requests.post(forward_url, headers=headers, json=data)
    except Exception as e:
        print("การส่งต่อข้อมูลล้มเหลว:", e)

    return 'OK'

@app.route("/IN", methods=["POST"])
def receive_image():
    try:
        image = request.files.get('image')
        message = request.form.get('message', 'ไม่มีข้อความ')

        if image:
            filename = image.filename
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(save_path)

            base_url = "https://line-natthanat.as2.pitunnel.net"
            image_url = f"{base_url}/{UPLOAD_FOLDER}/{filename}"

            push_message(message)
            push_image(image_url)

            return {'status': 'ok', 'message': 'ส่งภาพไป LINE แล้ว'}, 200
        else:
            return {'status': 'error', 'message': 'ไม่พบไฟล์ภาพ'}, 400
    except Exception as e:
        return {'status': 'error', 'detail': str(e)}, 500

# สำหรับให้เข้าถึงไฟล์ที่อัปโหลด (ต้องเปิดให้เว็บเข้าถึงได้ด้วย)
from flask import send_from_directory

@app.route(f'/{UPLOAD_FOLDER}/<filename>')
def serve_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9000)
