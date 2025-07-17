import requests

def OUT(image_path, text):
    url = "https://line-natthanat.as2.pitunnel.net/IN"  # URL Server ปลายทาง

    # เปิดไฟล์ภาพในโหมดไบนารี
    with open(image_path, 'rb') as f:
        files = {
            'image': (image_path, f, 'image/jpeg'),  # เปลี่ยน MIME type ตามไฟล์จริงได้
        }
        data = {
            'message': text
        }
        try:
            response = requests.post(url, files=files, data=data)
            print("Status code:", response.status_code)
            print("Response:", response.text)
        except Exception as e:
            print("เกิดข้อผิดพลาดในการส่งข้อมูล:", e)

# if __name__ == "__main__":
#     send_image_and_text("test.jpg", "นี่คือภาพจากคอมพิวเตอร์ของฉัน")
