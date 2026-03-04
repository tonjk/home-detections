# Home Detection - CCTV Person Detection with YOLOv8

This project detects people in CCTV streams using YOLOv8 and sends Telegram notifications with snapshots when a person is detected for a specified number of consecutive frames.

## Features

- **YOLOv8 Person Detection**: Uses `yolo26n.pt` for fast person detection.
- **Telegram Notifications**: Sends real-time alerts with images to a Telegram chat.
- **Consecutive Frame Logic**: Triggers notifications only after detecting a person in `NOTI_FRAME_THRESHOLD` consecutive frames to reduce false positives.
- **Dockerized**: Pre-built Docker image for easy deployment.
- **Optimized**: Uses ONNX export for faster CPU inference and persistent HTTP sessions for Telegram.

## Prerequisites

- Docker installed and running.
- A Telegram bot and chat ID.

## Configuration

Create a `.env` file in the project root (or set environment variables) with the following:

```env
# Telegram configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Video stream URL (e.g., RTSP from IP camera)
VIDEO_URL=rtsp://username:password@ip_address:port/stream

# Detection parameters
NOTI_FRAME_THRESHOLD=5
NOTI_COOLDOWN=60

# Run mode (true for Docker/headless, false for local GUI)
HEADLESS=true
```

## Build the Docker Image

```bash
docker build -t home-detection .
```

## Run the Container

```bash
docker run -d \
  --name home-detection \
  --env-file .env \
  --restart unless-stopped \
  home-detection
```

## View Logs

```bash
docker logs -f home-detection
```

## Stop and Remove

```bash
docker stop home-detection
docker rm home-detection
```

## Project Structure

```
home-detections/
├── configs/              # Configuration files
│   ├── config.py
│   └── ...
├── src/                  # Source code
│   ├── detectors/        # YOLO detection logic
│   ├── notifications/    # Telegram notification logic
│   └── video_captures/   # Video capture logic
├── yolo26n.pt            # YOLOv8 model weights
├── run.py                # Main application entry point
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker build configuration
└── README.md             # This file
```

## Model

The project uses `yolo26n.pt` (YOLOv8n) for person detection. The model is automatically exported to ONNX format on the first run for faster CPU inference.
