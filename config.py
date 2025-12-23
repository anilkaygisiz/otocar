import os

# Project Settings
VERSION = "v0.1 Beta"

# Camera Settings
# Webcam: 0, 1 (int)
# File: "path/to/video.mp4" (str)
VIDEO_SOURCE = "lane_test.mp4"

# Eğer environment variable varsa oradan al (Override)
env_source = os.getenv("VIDEO_SOURCE")
if env_source:
    try:
        VIDEO_SOURCE = int(env_source)
    except ValueError:
        VIDEO_SOURCE = env_source

DEBUG_MODE = True
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Image Processing
ROI_HEIGHT_RATIO = 0.5  # Ekranın alt %50'si
LANE_COLOR_THRESHOLD = 200 # 0-255 arası parlaklık eşiği

