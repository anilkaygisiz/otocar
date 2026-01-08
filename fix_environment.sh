#!/bin/bash
# Raspberry Pi 5 Environment Fixer
# Pip ile kurulan opencv-python, sistemdeki GStreamer/Libcamera eklentileriyle uyumsuz olabiliyor.
# Bu script, sanal ortamı silip "sistem paketlerini" (apt install python3-opencv) görecek şekilde yeniden kurar.

echo "[-] Eski sanal ortam (venv) siliniyor..."
rm -rf venv

echo "[-] Yeni sanal ortam oluşturuluyor (--system-site-packages)..."
# --system-site-packages: Sistemdeki apt paketlerini (opencv gibi) venv içinden erişilebilir yapar.
python3 -m venv venv --system-site-packages

echo "[-] Paketler yükleniyor..."
source venv/bin/activate

# OpenCV'yi PIP İLE YÜKLEMİYORUZ! Sistemden gelecek.
# Sadece eksik olabilecekleri kuruyoruz.
pip install pyserial

echo "[-] OpenCV Kontrolü..."
python3 -c "import cv2; print('OpenCV Version (System):', cv2.__version__)"

echo "=== ONARIM TAMAMLANDI ==="
echo "Lütfen şu komutla başlatın:"
echo "source venv/bin/activate"
echo "python3 main.py"
