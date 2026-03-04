# ============================================================
# Home Detection - CCTV Person Detection with YOLO26
# Optimized multi-stage Docker build (CPU inference)
# ============================================================

# --- Stage 1: Builder (install deps in a clean layer) ---
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build-time system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Stage 2: Runtime (lean final image) ---
FROM python:3.12-slim AS runtime

# Install only runtime system dependencies:
#   - libgl1 + libglib2.0: required by OpenCV
#   - ffmpeg: required for RTSP/HEVC stream decoding
#   - libsm6, libxext6: OpenCV GUI/rendering support
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

WORKDIR /app

# Copy application code
COPY configs/ ./configs/
COPY src/ ./src/
COPY run.py .

# Create directory for captured snapshots
RUN mkdir -p /app/captured_images

# Disable Python buffering for real-time log output
ENV PYTHONUNBUFFERED=1
# Disable ultralytics analytics/telemetry for faster startup
ENV YOLO_VERBOSE=false

CMD ["python", "run.py"]
