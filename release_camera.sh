#!/bin/bash
echo "=== KAMERA KURTARMA OPERASYONU ==="

# 1. Pipewire ve Wireplumb servislerini durdur (Kamerayı bunlar tutuyor)
echo "[-] Pipewire ve Wireplumb servisleri durduruluyor..."
systemctl --user stop pipewire.socket pipewire.service wireplumb.service

# 2. Emin olmak için zorla kapat
echo "[-] Kalan process'ler temizleniyor..."
pkill -f pipewire
pkill -f wireplumb

# 3. Kontrol et
echo "[?] /dev/video0 kontrol ediliyor..."
if lsof /dev/video0 > /dev/null 2>&1; then
    echo "!!! HATA: Kamera hala meşgul! Çıktı:"
    lsof /dev/video0
else
    echo "[+] BAŞARILI: Kamera serbest bırakıldı!"
    echo "    Şimdi 'python3 check_camera.py' veya 'main.py' çalıştırabilirsiniz."
fi

# Not: Geri açmak için: systemctl --user start pipewire wireplumb
