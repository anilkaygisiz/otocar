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
LANE_COLOR_THRESHOLD = 140 # 0-255 arası parlaklık eşiği (Düşürüldü)

# PID Settings
PID_KP = 0.5  # Oransal katsayı (Hata ile orantılı tepki)
PID_KI = 0.0  # İntegral katsayı (Toplam hata birikimi - genelde çizgi izlemede düşük veya 0)
PID_KD = 0.1  # Türev katsayı (Hata değişim hızı - ani hareketleri sönümler)
MAX_SPEED = 50 # Maksimum motor hızı (0-100 veya 0-255)
BASE_SPEED = 30 # Düz giderkenki temel hız

