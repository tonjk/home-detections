import cv2
import os
import time
import logging
import threading
from src.detectors.detector import Detector
from src.video_captures.video_capture import VideoCaptureThread
from src.notifications.notification import telegram_notification
from configs.config import NOTI_FRAME_THRESHOLD, NOTI_COOLDOWN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ==========================================
# Configuration
# ==========================================
FRAME_THRESHOLD = NOTI_FRAME_THRESHOLD
COOLDOWN_SECONDS = NOTI_COOLDOWN
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"  # Docker: set HEADLESS=true
CAPTURED_DIR = os.path.join(os.path.dirname(__file__), "captured_images")


def main():
    # ---- Model ----
    logger.info("Loading YOLO model...")
    detector = Detector()

    # ---- Video Stream ----
    logger.info("Initializing video capture thread...")
    cap = VideoCaptureThread()

    # ---- Ensure snapshot directory ----
    os.makedirs(CAPTURED_DIR, exist_ok=True)

    person_frame_count = 0
    last_noti_time = 0.0
    fps_counter = 0
    fps_start = time.time()

    logger.info("Starting detection loop (press 'q' to quit)...")

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                time.sleep(0.01)
                continue

            # ---- Inference ----
            results = detector.detect(frame)

            person_detected = False
            for r in results:
                if len(r.boxes) > 0:
                    person_detected = True
                    for box in r.boxes.xyxy:
                        x1, y1, x2, y2 = map(int, box)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

            # ---- Consecutive-frame logic ----
            if person_detected:
                person_frame_count += 1
            else:
                person_frame_count = max(0, person_frame_count - 1)

            # ---- Notification ----
            if person_frame_count >= FRAME_THRESHOLD:
                now = time.time()
                if (now - last_noti_time) > COOLDOWN_SECONDS:
                    msg = (
                        f"🚨 *Alert!* Person detected in CCTV"
                    )
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    image_path = os.path.join(CAPTURED_DIR, f"person_detect_{timestamp}.jpg")
                    cv2.imwrite(image_path, frame)
                    logger.info(f"Snapshot saved → {image_path}")

                    threading.Thread(
                        target=telegram_notification,
                        args=(msg, image_path),
                        daemon=True,
                    ).start()

                    last_noti_time = now
                    person_frame_count = 0

            # ---- FPS logging (every 60 seconds) ----
            fps_counter += 1
            elapsed = time.time() - fps_start
            if elapsed >= 60:
                logger.info(f"Processing FPS: {fps_counter / elapsed:.1f}")
                fps_counter = 0
                fps_start = time.time()

            # ---- Display (skip in Docker / headless mode) ----
            if not HEADLESS:
                cv2.imshow("CCTV Person Detection", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    logger.info("Quit key pressed.")
                    break

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Shutting down...")
    finally:
        cap.release()
        if not HEADLESS:
            cv2.destroyAllWindows()
        logger.info("Application exited cleanly.")


if __name__ == "__main__":
    main()