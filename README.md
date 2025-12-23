# Otocar - Otonom Araç Projesi

Raspberry Pi 4 ve Arduino kullanılarak geliştirilen tam otonom araç yazılımı.

## Proje Fazları

### Faz 1: Şerit Takip Eden Robot (The "Rail" Robot)
- Şerit takibi ve yoldan çıkmama.
- Kamera görüntü işleme (ROI, Threshold/Canny).
- PID kontrolü ile direksiyon açısı hesaplama.

### Faz 2: Engel Algılama ve Acil Durum (The "Safe" Robot)
- Ultrasonik sensör ile engel tespiti.
- 15cm altı mesafede acil duruş (Hard Stop).

### Faz 3: Trafik İşaretleri ve Karar Verme (The "Obedient" Robot)
- Trafik işaretlerini (Dur, Geç, Dön) algılama.
- Renk ve şekil tespiti.

### Faz 4: State Machine Entegrasyonu (Artinyo v1.0)
- Tüm modların tek bir Durum Makinesi (State Machine) altında birleştirilmesi.

## Kurulum
Gerekli Python kütüphanelerini yükleyin:
```bash
pip install opencv-python numpy pyserial
```

## Çalıştırma
```bash
python main.py
```
Ayarları `config.py` içerisinden değiştirebilirsiniz.
