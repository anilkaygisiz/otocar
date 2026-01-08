#!/usr/bin/env python3
"""
Raspberry Pi 5 Kamera Test Aracı
picamera2 kütüphanesi ile Camera Module 3 testi.

Bu script, OpenCV/GStreamer yerine Raspberry Pi'nin resmi kamera kütüphanesini kullanır.
"""

import time
import sys

def test_picamera2():
    """picamera2 ile kamera testi"""
    print("=== PICAMERA2 TEST ===")
    
    try:
        from picamera2 import Picamera2
        print("[OK] picamera2 import edildi")
    except ImportError:
        print("[HATA] picamera2 yüklü değil!")
        print("Çözüm: sudo apt install -y python3-picamera2")
        return False
    
    try:
        # Kamerayı başlat
        picam2 = Picamera2()
        print(f"[OK] Kamera bulundu: {picam2.camera_properties}")
        
        # Konfigürasyon (640x480, BGR formatı - OpenCV uyumlu)
        config = picam2.create_preview_configuration(
            main={"size": (640, 480), "format": "BGR888"}
        )
        picam2.configure(config)
        print("[OK] Konfigürasyon uygulandı: 640x480 BGR888")
        
        # Başlat
        picam2.start()
        print("[OK] Kamera başlatıldı, frame alınıyor...")
        
        # Birkaç frame al
        for i in range(5):
            frame = picam2.capture_array()
            print(f"[OK] Frame {i+1}: Shape={frame.shape}, Dtype={frame.dtype}")
            time.sleep(0.1)
        
        # Kapat
        picam2.stop()
        print("\n✅ BAŞARILI! Kamera çalışıyor.")
        print("picamera2 -> OpenCV entegrasyonu için main.py güncellenebilir.")
        return True
        
    except Exception as e:
        print(f"[HATA] Kamera hatası: {e}")
        return False

def test_opencv_with_picamera2():
    """picamera2 + OpenCV entegrasyonu testi"""
    print("\n=== PICAMERA2 + OPENCV TEST ===")
    
    try:
        from picamera2 import Picamera2
        import cv2
        import numpy as np
    except ImportError as e:
        print(f"[HATA] Import hatası: {e}")
        return False
    
    try:
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(
            main={"size": (640, 480), "format": "BGR888"}
        )
        picam2.configure(config)
        picam2.start()
        
        print("OpenCV penceresi açılıyor (3 saniye)...")
        print("'q' tuşu ile çıkabilirsiniz.")
        
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < 3:
            frame = picam2.capture_array()
            frame_count += 1
            
            # OpenCV ile göster
            cv2.putText(frame, f"Frame: {frame_count}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("PiCamera2 Test", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        fps = frame_count / (time.time() - start_time)
        print(f"[OK] {frame_count} frame, {fps:.1f} FPS")
        
        picam2.stop()
        cv2.destroyAllWindows()
        
        print("\n✅ OPENCV ENTEGRASYONU BAŞARILI!")
        return True
        
    except Exception as e:
        print(f"[HATA] OpenCV test hatası: {e}")
        return False

if __name__ == "__main__":
    print("Raspberry Pi 5 - Camera Module 3 Test Aracı")
    print("=" * 50)
    
    # Test 1: Temel picamera2
    if not test_picamera2():
        print("\n❌ picamera2 testi başarısız. Kurulum kontrol edin.")
        sys.exit(1)
    
    # Test 2: OpenCV entegrasyonu
    if not test_opencv_with_picamera2():
        print("\n⚠️ OpenCV entegrasyonu başarısız ama temel kamera çalışıyor.")
        sys.exit(0)
    
    print("\n" + "=" * 50)
    print("TÜM TESTLER BAŞARILI! 🎉")
    print("Sonraki adım: main.py'ı picamera2 ile güncellemek.")
