#!/bin/bash
echo "=== Otocar: Raspberry Pi 5 Kurulum Sihirbazı ==="

# 1. Sistem Güncelleme ve Kütüphaneler
echo "[-] Sistem güncelleniyor ve bağımlılıklar kuruluyor..."
sudo apt update
sudo apt install -y libcamera-dev libopencv-dev python3-opencv libhdf5-dev libatlas-base-dev

# 2. Sanal Ortam (Virtual Env) - Bookworm için zorunlu
if [ ! -d "venv" ]; then
    echo "[-] Python sanal ortamı (venv) oluşturuluyor..."
    python3 -m venv venv
fi

# 3. Paket Yükleme
echo "[-] Python kütüphaneleri yükleniyor..."
source venv/bin/activate
# Pi 5'te 'opencv-python' yerine 'opencv-python-headless' daha stabil olabilir (Qt cakismasi yoksa)
# Ama biz GUI kullandigimiz icin normalini deneyelim, sorun olursa headless'a geceriz.
pip install --upgrade pip
pip install opencv-python-headless numpy pyserial

echo ""
echo "=== KURULUM TAMAMLANDI ==="
echo "Projeyi başlatmak için:"
echo "source venv/bin/activate"
echo "python3 main.py"
