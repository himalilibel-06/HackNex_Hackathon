import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture("videos/raw/WhatsApp Video 2026-10-07 at 12.26.23 PM.mp4")

frame_idx = 0
all_detections = []

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        break
    frame_idx += 1
    if frame_idx % 30 == 0:
        res = model(frame, conf=0.1, verbose=False)
        boxes = res[0].boxes
        print(f"Frame {frame_idx}: Found {len(boxes)} objects")
        for box in boxes:
            cls_id = int(box.cls[0].cpu().numpy())
            cls_name = model.names[cls_id]
            conf = float(box.conf[0].cpu().numpy())
            print(f"  -> Class: {cls_name} ({cls_id}), Conf: {conf:.2f}")

cap.release()
