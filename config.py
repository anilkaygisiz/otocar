import os

# Camera Settings
# Webcam kullanmak için 0, 1 gibi integer değerler.
# Video dosyası kullanmak için dosya yolu (string).
# Örnek: VIDEO_SOURCE = "test_video.mp4"
VIDEO_SOURCE = 0

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
