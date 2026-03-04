import cv2
import os
import threading
import time
from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CCTV_PASSWORD, CCTV_IP = os.getenv('CCTV_PASSWORD'), os.getenv('CCTV_IP')

# Output frame size (landscape)
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

class VideoCaptureThread:
    """
    Background thread to read frames from RTSP stream continuously.
    This prevents buffer accumulation and ensures we process only the latest frame.
    Uses a threading.Lock to guarantee the main thread never reads a half-written frame.
    """
    def __init__(self):
        self.src = f"rtsp://admin:{CCTV_PASSWORD}@{CCTV_IP}:554/Streaming/Channels/101"
        logger.info(f"Initializing VideoCaptureThread for RTSP stream with IP: {CCTV_IP}")

        # Set RTSP transport to TCP BEFORE opening capture (prevents packet loss & resolution issues)
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
        self.cap = cv2.VideoCapture(self.src, cv2.CAP_FFMPEG)

        if not self.cap.isOpened():
            logger.error("Failed to open RTSP stream initially.")
        else:
            w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            logger.info(f"RTSP stream opened successfully. Resolution: {w}x{h}, FPS: {fps}")

        # Thread-safe lock for frame access
        self._lock = threading.Lock()
        self.ret, self.frame = self.cap.read()
        if self.ret and self.frame is not None:
            logger.info(f"First frame captured. Shape: {self.frame.shape}")
        else:
            logger.warning("Could not read the initial frame from stream.")

        self.running = True
        logger.info("Starting background thread for continuous video capture.")
        self.thread = threading.Thread(target=self.update, args=(), daemon=True)
        self.thread.start()

    def update(self):
        logger.info("Video capture thread started and running.")
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self._lock:
                    self.ret = ret
                    self.frame = frame
            else:
                logger.warning("Failed to retrieve frame. Attempting to reconnect in 2 seconds...")
                time.sleep(2)
                self.cap.release()
                self.cap = cv2.VideoCapture(self.src, cv2.CAP_FFMPEG)
                if self.cap.isOpened():
                    w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    logger.info(f"Reconnected to RTSP stream successfully. Resolution: {w}x{h}")
                else:
                    logger.error("Reconnection attempt failed.")
        logger.info("Video capture thread stopped.")

    def read(self):
        with self._lock:
            if self.ret and self.frame is not None:
                resized = cv2.resize(self.frame, (FRAME_WIDTH, FRAME_HEIGHT))
                return self.ret, resized
            return self.ret, self.frame

    def isOpened(self):
        return self.cap is not None and self.cap.isOpened()

    def release(self):
        logger.info("Releasing VideoCaptureThread resources...")
        self.running = False
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join()
        if self.cap is not None:
            self.cap.release()
        logger.info("VideoCaptureThread resources released successfully.")