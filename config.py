import os

# Project Settings
VERSION = "v0.1 Beta"

# Camera Settings
# Webcam: 0, 1 (int)
# File: "path/to/video.mp4" (str)
VIDEO_SOURCE = "Videos/test1.mp4"

# Eğer environment variable varsa oradan al (Override)
env_source = os.getenv("VIDEO_SOURCE")
if env_source:
    try:
        VIDEO_SOURCE = int(env_source)
    except ValueError:
        VIDEO_SOURCE = env_source

DEBUG_MODE = True

# Otomatik Headless Algılama (Ekran yoksa True olur)
if os.environ.get('DISPLAY') is None:
    HEADLESS_MODE = True
    print("Headless mod aktif: Ekran bulunamadı.")
else:
    HEADLESS_MODE = False

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Image Processing
ROI_HEIGHT_RATIO = 0.5  # Ekranın alt %50'si
LANE_COLOR_THRESHOLD = 140 # 0-255 arası parlaklık eşiği (Düşürüldü)

# PID Settings
PID_KP = 0.5  # Oransal katsayı (Hata ile orantılı tepki)
PID_KI = 0.0  # İntegral katsayı (Toplam hata birikimi - genelde çizgi izlemede düşük veya 0)
PID_KD = 0.1  # Türev katsayı (Hata değişim hızı - ani hareketleri sönümler)
MAX_SPEED = 50 # Maksimum motor hızı (0-100 veya 0-255)
BASE_SPEED = 30 # Düz giderkenki temel hız

