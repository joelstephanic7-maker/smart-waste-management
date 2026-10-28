
import cv2
from ultralytics import YOLO
from collections import Counter, deque
import time

# ==========================================
# VISIONX AI WASTE DETECTION SYSTEM
# ==========================================

MODEL_PATH = "yolo11n.pt"
CAMERA_INDEX = 0
CONFIDENCE_THRESHOLD = 0.35
HISTORY_SIZE = 10

# Generic YOLO classes that can indicate organic waste.
# These are not a complete list of biodegradable materials.
BIO_CLASSES = {
    "banana",
    "apple",
    "orange",
    "broccoli",
    "carrot",
}

# Objects considered non-biodegradable for this prototype.
NONBIO_CLASSES = {
    "bottle",
}

# Store recent classifications to reduce flickering.
status_history = deque(maxlen=HISTORY_SIZE)

print("=" * 45)
print("       VISIONX AI WASTE SYSTEM")
print("=" * 45)

# Load the YOLO model
print("Loading YOLO model...")
model = YOLO(MODEL_PATH)
print("YOLO model loaded successfully!")

# Open laptop webcam
camera = cv2.VideoCapture(CAMERA_INDEX)

if not camera.isOpened():
    print("ERROR: Could not open camera.")
    print("Check camera permissions or try CAMERA_INDEX = 1.")
    raise SystemExit

print("Camera opened successfully!")
print("Press Q to quit.")

previous_time = time.time()

try:
    while True:
        success, frame = camera.read()

        if not success:
            print("ERROR: Failed to read camera frame.")
            break

        # Run object detection
        results = model(frame, verbose=False)
        detections = results[0].boxes

        detected_bio = set()
        detected_nonbio = set()
        confidence_values = []

        # Draw detected objects and collect classifications
        for box in detections:
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            object_name = model.names[class_id].lower()

            if confidence < CONFIDENCE_THRESHOLD:
                continue

            confidence_values.append(confidence)

            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

            if object_name in BIO_CLASSES:
                detected_bio.add(object_name)
                box_color = (0, 200, 0)

            elif object_name in NONBIO_CLASSES:
                detected_nonbio.add(object_name)
                box_color = (255, 120, 0)

            else:
                # Detected, but not categorized as BIO/NON-BIO.
                box_color = (180, 180, 180)

            label = f"{object_name}: {confidence * 100:.1f}%"

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                box_color,
                2
            )

            cv2.putText(
                frame,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                box_color,
                2
            )

        # Decide the current waste status
        if detected_bio and detected_nonbio:
            current_status = "MIXED"
            status_color = (0, 0, 255)

        elif detected_bio:
            current_status = "BIO"
            status_color = (0, 200, 0)

        elif detected_nonbio:
            current_status = "NON-BIO"
            status_color = (255, 120, 0)

        else:
            current_status = "NO KNOWN WASTE DETECTED"
            status_color = (200, 200, 200)

        # Stabilize status across multiple frames
        status_history.append(current_status)
        stable_status = Counter(status_history).most_common(1)[0][0]

        # Average confidence of accepted detections
        if confidence_values:
            average_confidence = (
                sum(confidence_values) / len(confidence_values)
            )
            confidence_text = (
                f"Detection confidence: {average_confidence * 100:.1f}%"
            )
        else:
            confidence_text = "Detection confidence: N/A"

        # FPS estimate
        current_time = time.time()
        elapsed = current_time - previous_time
        fps = 1 / elapsed if elapsed > 0 else 0
        previous_time = current_time

        # Display VisionX status
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 115), (25, 25, 25), -1)

        cv2.putText(
            frame,
            "VISIONX - AI WASTE VERIFICATION",
            (15, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"STATUS: {stable_status}",
            (15, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            status_color,
            2
        )

        cv2.putText(
            frame,
            confidence_text,
            (15, 92),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1
        )

        cv2.putText(
            frame,
            f"FPS: {fps:.1f}",
            (frame.shape[1] - 115, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1
        )

        cv2.imshow("VisionX AI Camera", frame)

        # Press Q to exit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    camera.release()
    cv2.destroyAllWindows()
    print("VisionX AI camera stopped.")
