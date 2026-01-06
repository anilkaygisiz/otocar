import os

# Otocar Konfigürasyon Dosyası
VERSION = "0.2 (Beta - Camera Fixed)"
# CHANGELOG v0.2:
# - Fix: Raspberry Pi Legacy Camera desteği eklendi (enable_legacy_camera.sh).
# - Fix: GStreamer bellek hataları giderildi.
# - New: check_camera.py ve diagnose_system.py araçları eklendi.

import cv2
import numpy as np
# Project Settings
# Camera Settings
# Webcam: 0, 1 (int)
# File: "path/to/video.mp4" (str)
VIDEO_SOURCE = 0

# Kısıtlamaları kaldırdım, bırakalım kamera ve opencv anlaşsın.
# NOT: 'video/x-raw, format=YUY2' ekleyerek libcamerasrc'in sevdigi formati veriyoruz.
PI5_CAMERA_PIPELINE = (
    "libcamerasrc ! "
    "video/x-raw, width=640, height=480, framerate=30/1 ! "
    "videoconvert ! "
    "video/x-raw, format=BGR ! "
    "appsink drop=1"
)

# Resolution
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Eğer environment variable varsa oradan al (Override)
env_source = os.getenv("VIDEO_SOURCE")
if env_source:
    try:
        VIDEO_SOURCE = int(env_source)
    except ValueError:
        VIDEO_SOURCE = env_source

DEBUG_MODE = True

# Görüntü Ayarları
# True: SSH'dan bağlansanız bile ekranı açmaya zorlar (VNC/HDMI için :0 ekranını kullanır)
# False: Ekran yoksa otomatik Headless moda geçer (Görüntü yok, sadece log)
FORCE_DISPLAY = True

# Otomatik Headless Algılama
if FORCE_DISPLAY:
    if os.environ.get('DISPLAY') is None:
        os.environ['DISPLAY'] = ':0' # Varsayılan ekranı ata
    HEADLESS_MODE = False
    print("Ekran zorlandı (FORCE_DISPLAY). Hedef: " + os.environ.get('DISPLAY', ':0'))
elif os.environ.get('DISPLAY') is None:
    HEADLESS_MODE = True
    print("Headless mod aktif: Ekran bulunamadı.")
else:
    HEADLESS_MODE = False

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Image Processing
ROI_HEIGHT_RATIO = 0.5  # Ekranın alt %50'si
LANE_COLOR_THRESHOLD = 140 # 0-255 arası parlaklık eşiği (Brightness Mode)

# Algılama Modu: 'BRIGHTNESS' veya 'COLOR'
DETECTION_MODE = 'BRIGHTNESS'

# HSV Renk Ayarları (Color Mode)
# Sarı (Yellow) Aralığı
HSV_LOWER_YELLOW = [20, 100, 100]
HSV_UPPER_YELLOW = [40, 255, 255]

# Beyaz (White) Aralığı (Gölge vb hassas ayar gerekebilir)
HSV_LOWER_WHITE = [0, 0, 200]
HSV_UPPER_WHITE = [180, 50, 255]

# PID Settings
PID_KP = 0.5  # Oransal katsayı (Hata ile orantılı tepki)
PID_KI = 0.0  # İntegral katsayı (Toplam hata birikimi - genelde çizgi izlemede düşük veya 0)
PID_KD = 0.1  # Türev katsayı (Hata değişim hızı - ani hareketleri sönümler)
MAX_SPEED = 50 # Maksimum motor hızı (0-100 veya 0-255)
BASE_SPEED = 30 # Düz giderkenki temel hız

