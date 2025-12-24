#!/bin/bash
echo "=== KAMERA FORMAT SIFIRLAMA ARACI ==="

# 1. Mevcut duruma bak
echo "[1] Eski Durum:"
v4l2-ctl -V

# 2. Formatı YUYV (YUY2) olarak zorla
echo "[-] Format YUYV (640x480) olarak ayarlanıyor..."
v4l2-ctl --set-fmt-video=width=640,height=480,pixelformat=YUYV

# 3. Framerate ayarla (Bazen 0 kalırsa hata verir)
echo "[-] Framerate 30fps yapılıyor..."
v4l2-ctl --set-parm=30

# 4. Yeni duruma bak
echo "[2] Yeni Durum:"
v4l2-ctl -V

# 5. Hızlı Test
echo "[-] Test ediliyor..."
if ffmpeg -y -f v4l2 -input_format yuyv422 -video_size 640x480 -i /dev/video0 -frames:v 1 cam_fixed.jpg; then
    echo "\n[+] SIFIRLAMA BAŞARILI! Kamera kurtarıldı."
    echo "    Artık 'check_camera.py' veya 'main.py' çalışacaktır."
else
    echo "\n[-] Sıfırlama işe yaramadı. Donanım bağlantısını kontrol edin."
fi
