from sleep import AI_sleeep
from IN import IN, shared_state
from car import car
from OUT import OUT
import cv2
import threading
import time
from ultralytics import YOLO
import mediapipe as mp

model = YOLO("yolo11n.pt")

# เพิ่ม flag ตรงนี้
has_sent_alert = False

if __name__ == '__main__':
    flask_thread = threading.Thread(target=IN)
    flask_thread.daemon = True
    flask_thread.start()

    cap = cv2.VideoCapture("/dev/video0")
    cap2 = cv2.VideoCapture("/dev/video2")

    last_detection_time = 0

    mp_face_mesh = mp.solutions.face_mesh

    try:
        while True:
            current_time = time.time()

            if shared_state["value"] == 1:
                status = AI_sleeep(cap,mp_face_mesh)
                print(status)

            elif shared_state["value"] == 2:
                frame, status, last_detection_time, already_alerted = car(cap, model, current_time, last_detection_time)

                if status == "have people":
                    if already_alerted and not has_sent_alert:
                        filename = "detected_sleep.jpg"
                        OUT(filename, "⚠️ ตรวจพบว่ามีคนนานเกิน 20 วินาที")
                        has_sent_alert = True  # ส่งแล้ว

                else:
                    has_sent_alert = False  # ถ้าไม่เจอคน รีเซ็ต flag

                print("สถานะ:", status)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cap2.release()
        cv2.destroyAllWindows()
