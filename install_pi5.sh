#!/bin/bash
echo "=== Otocar: Raspberry Pi 5 Kurulum Sihirbazı ==="

# 1. Sistem Güncelleme ve Kütüphaneler
echo "[-] Sistem güncelleniyor ve bağımlılıklar kuruluyor..."
sudo apt update
# libatlas yerine libopenblas (yeni OS uyumlulugu)
sudo apt install -y libcamera-dev libopencv-dev python3-opencv libopenblas-dev libhdf5-dev

# 2. Sanal Ortam (Virtual Env) - Bookworm için zorunlu
if [ ! -d "venv" ]; then
    echo "[-] Python sanal ortamı (venv) oluşturuluyor..."
    python3 -m venv venv
fi

# 3. Paket Yükleme
echo "[-] Python kütüphaneleri yükleniyor..."
source venv/bin/activate
pip install --upgrade pip
# GUI destegi icin 'opencv-python' (headless degil!)
pip install opencv-python numpy pyserial

echo ""
echo "=== KURULUM TAMAMLANDI ==="
echo "Projeyi başlatmak için:"
echo "source venv/bin/activate"
echo "python3 main.py"
