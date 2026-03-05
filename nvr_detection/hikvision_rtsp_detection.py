# pip install opencv-python yt-dlp ultralytics

import cv2
import os
import time
from ultralytics import YOLO
import yt_dlp

# ==========================================
# การตั้งค่าการเชื่อมต่อกล้อง Hikvision
# ==========================================
# รูปแบบ RTSP URL ของ Hikvision:
# rtsp://[username]:[password]@[ip]:[port]/Streaming/Channels/[channel][stream_type]
# channel: 1 (กล้องตัวที่ 1)
# stream_type: 01 (Main stream ความละเอียดสูง), 02 (Sub stream ความละเอียดต่ำ)
# ตัวอย่าง: "rtsp://admin:password123@192.168.1.64:554/Streaming/Channels/101"

CCTV_IP = "192.168.1.xxx"
CCTV_USERNAME = "admin"
CCTV_PASSWORD = "Admin12345"
CCTV_PORT = "554"
CCTV_CHANNEL = "101"

RTSP_URL = f"rtsp://{CCTV_USERNAME}:{CCTV_PASSWORD}@{CCTV_IP}:{CCTV_PORT}/Streaming/Channels/{CCTV_CHANNEL}"

# # โฟลเดอร์สำหรับบันทึกภาพ
# SAVE_DIR = "captured_images"
# if not os.path.exists(SAVE_DIR):
#     os.makedirs(SAVE_DIR)

def capture_stream():
    print(f"กำลังเชื่อมต่อไปยังกล้อง: {RTSP_URL.replace(RTSP_URL.split('@')[0], 'rtsp://***:***')}")
    
    # เชื่อมต่อกับ RTSP Stream
    cap = cv2.VideoCapture(RTSP_URL)
    
    # กำหนด Buffer size เล็กๆ เพื่อลดความล่าช้า (Delay)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

    if not cap.isOpened():
        print("ไม่สามารถเชื่อมต่อกล้องได้ โปรดตรวจสอบ IP, Username, Password และเครือข่าย")
        return

    print("เชื่อมต่อสำเร็จ! กด 's' เพื่อบันทึกภาพ และกด 'q' เพื่อออก")

    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("ไม่ได้รับสัญญาณภาพจากกล้อง กำลังเชื่อมต่อใหม่...")
                time.sleep(2)
                cap = cv2.VideoCapture(RTSP_URL)
                continue

            # # แสดงภาพสด
            # cv2.imshow('Hikvision CCTV Stream', frame)

            # detect objects
            annotated_frame = detect_objects(frame)
            cv2.imshow('Hikvision CCTV Stream', annotated_frame)

            # รอรับคำสั่งจากคีย์บอร์ด
            key = cv2.waitKey(1) & 0xFF
            
            # กด 'q' เพื่อออกจากโปรแกรม
            if key == ord('q'):
                print("กำลังปิดโปรแกรม...")
                break
                
            # # กด 's' เพื่อบันทึกภาพ
            # elif key == ord('s'):
            #     timestamp = time.strftime("%Y%m%d_%H%M%S")
            #     filename = os.path.join(SAVE_DIR, f"capture_{timestamp}.jpg")
            #     cv2.imwrite(filename, frame)
            #     print(f"บันทึกภาพเรียบร้อยแล้ว: {filename}")

    finally:
        # คืนค่า resource ต่างๆ เมื่อจบโปรแกรม
        cap.release()
        cv2.destroyAllWindows()


# YOLO model classes:
# {0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane', 5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light', 10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench', 14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack', 25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase', 29: 'frisbee', 30: 'skis', 31: 'snowboard', 32: 'sports ball', 33: 'kite', 34: 'baseball bat', 35: 'baseball glove', 36: 'skateboard', 37: 'surfboard', 38: 'tennis racket', 39: 'bottle', 40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon', 45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli', 51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake', 56: 'chair', 57: 'couch', 58: 'potted plant', 59: 'bed', 60: 'dining table', 61: 'toilet', 62: 'tv', 63: 'laptop', 64: 'mouse', 65: 'remote', 66: 'keyboard', 67: 'cell phone', 68: 'microwave', 69: 'oven', 70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book', 74: 'clock', 75: 'vase', 76: 'scissors', 77: 'teddy bear', 78: 'hair drier', 79: 'toothbrush'}

# Load model
model = YOLO("yolo26s.pt") # yolo26n.pt, yolo26s.pt, yolo26m.pt, yolo26l.pt, yolo26x.pt
MODEL_CLASSES = [0, 2, 3] # 0: person, 2: car, 3: motorcycle

# detect and draw bounding box
def detect_objects(frame):
    results = model(frame, verbose=False, classes=MODEL_CLASSES, conf=0.5)
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            conf = box.conf[0]
            cls = int(box.cls[0])
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, f"{model.names[cls]}: {conf:.2f}", (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return frame

def stream_youtube(url):
    # Configure yt-dlp to get the direct stream URL
    ydl_opts = {
        'format': 'best[ext=mp4]', # Fetch the best mp4 quality
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        stream_url = info['url']

    # Open the stream with OpenCV
    cap = cv2.VideoCapture(stream_url)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    print("Stream started. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect objects
        annotated_frame = detect_objects(frame)

        cv2.imshow('YouTube Stream with Detector', annotated_frame)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # capture_stream()
    stream_youtube("https://www.youtube.com/watch?v=PJ5xXXcfuTc")
