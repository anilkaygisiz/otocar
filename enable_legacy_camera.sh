#!/bin/bash
# Raspberry Pi Legacy Camera Etkinleştirici
# Bu script /boot/config.txt dosyasını düzenler.

CONFIG_FILE="/boot/firmware/config.txt"

# Dosya konumunu kontrol et (Eski/Yeni OS farkı)
if [ ! -f "$CONFIG_FILE" ]; then
    CONFIG_FILE="/boot/config.txt"
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "HATA: Config dosyası bulunamadı!"
    exit 1
fi

echo "Düzenlenen dosya: $CONFIG_FILE"
echo "Yedek alınıyor..."
sudo cp $CONFIG_FILE "$CONFIG_FILE.bak"

# 1. camera_auto_detect kapat (Bu açıkken legacy çalışmaz)
if grep -q "camera_auto_detect=1" "$CONFIG_FILE"; then
    sudo sed -i 's/camera_auto_detect=1/camera_auto_detect=0/g' "$CONFIG_FILE"
    echo "[-] camera_auto_detect=0 yapıldı."
elif ! grep -q "camera_auto_detect=0" "$CONFIG_FILE"; then
    echo "camera_auto_detect=0" | sudo tee -a "$CONFIG_FILE" > /dev/null
    echo "[-] camera_auto_detect=0 eklendi."
fi

# 2. start_x=1 ekle (Legacy driver'ı yükler)
if ! grep -q "start_x=1" "$CONFIG_FILE"; then
    echo "start_x=1" | sudo tee -a "$CONFIG_FILE" > /dev/null
    echo "[-] start_x=1 eklendi."
fi

# 3. GPU Belleğini 128MB yap (Kamera için şart)
if grep -q "gpu_mem=" "$CONFIG_FILE"; then
    sudo sed -i 's/gpu_mem=.*/gpu_mem=128/g' "$CONFIG_FILE"
    echo "[-] gpu_mem güncellendi."
else
    echo "gpu_mem=128" | sudo tee -a "$CONFIG_FILE" > /dev/null
    echo "[-] gpu_mem=128 eklendi."
fi

echo ""
echo "=== İŞLEM TAMAMLANDI ==="
echo "Lütfen şimdi cihazı yeniden başlatın:"
echo "sudo reboot"
