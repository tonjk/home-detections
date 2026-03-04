# Home Detections - CCTV Person Detection with YOLO26

This project detects people in CCTV streams using YOLO26 and sends Telegram notifications with snapshots when a person is detected for a specified number of consecutive frames.

The detection pipeline runs a background thread for video capturing (to ensure no frame buffer lag) and is fully Dockerized for headless deployment.

## Features

- **YOLO26 Person Detection**: Uses `yolo26s.pt` for fast and accurate person detection.
- **Micro-batching / Consecutive Frame Target**: Triggers notifications only after detecting a person in consecutive frames to drastically eliminate false positives.
- **Smart Notifications**: Sends a snapshot drawn with a clean detection bounding box to a Telegram chat.
- **Dockerized**: Multi-stage Docker build to yield an ultra-lean headless runtime environment with no X11 dependencies.
- **Optimized Performance**:
  - RTSP transport is forced to TCP to maintain stable H.265/HEVC header decoding.
  - Model weights are auto-exported to ONNX on the first startup to provide 2-3x faster CPU inference.
  - Video capturing happens asynchronously on a dedicated thread holding a threading Lock.
  - Telegram API calls reuse persistent HTTP connection pooling.

## Configuration

Create a `.env` file in the project root containing your sensitive settings:

```env
# Telegram configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# CCTV Stream Setup
# Ensure these do not contain quotes (e.g. use 192.168.1.50, not "192.168.1.50")
CCTV_IP=192.168.1.x
CCTV_PASSWORD=your_password_here

# Run mode (true for Docker/headless, false for local GUI preview)
HEADLESS=true
```

You can tweak frame thresholds and cooldown limits in `configs/model_config.ymal`.

## Docker Usage

### 1. Build the Docker Image

Run this in the repository's root directory:

```bash
docker build -t home-detections .
```

### 2. Run the Container

It is recommended to run the container using `--network host` (if on Linux) so it can access local LAN IP cameras, and to map a Docker volume `home-detection-captures` so your snapshots aren't lost when the container stops.

```bash
docker run -d \
  --name home-detections \
  --network host \
  --env-file .env \
  -e HEADLESS=true \
  -v home-detection-captures:/app/captured_images \
  --restart unless-stopped \
  home-detections
```

_(Note: Docker Desktop for Mac has limitations with `--network host` resolving LAN IPs natively. If `CCTV_IP` is inaccessible, you may need to run this natively or on a Linux host)._

### 3. View Logs

```bash
docker logs -f home-detections
```

### 4. Stop and Remove

```bash
docker rm -f home-detections
```

## Project Structure

```
home-detections/
├── configs/              # Configuration files
│   ├── config.py         # YAML loader logic
│   └── model_config.ymal # Model & notification target settings
├── src/                  # Source code
│   ├── detectors/        # YOLO ONNX detection logic
│   ├── notifications/    # Telegram Notification & Pool logic
│   └── video_captures/   # Thread-safe Video Capture loop
├── yolo26s.pt            # YOLO26 target weight (auto-downloaded)
├── run.py                # Main execution loop
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container build configuration
└── README.md             # This file
```
