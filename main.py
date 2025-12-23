import cv2
import config
import time
import os

import lane_detector
import pid_controller
import utils

def main():
    print(f"Otocar {config.VERSION} Başlatılıyor... Kaynak: {config.VIDEO_SOURCE}")
    
    # PID Kontrolcüsünü Başlat
    pid = pid_controller.PID(config.PID_KP, config.PID_KI, config.PID_KD)
    
    cap = cv2.VideoCapture(config.VIDEO_SOURCE)
    
    if not cap.isOpened():
        print(f"Hata: Video kaynağı açılamadı: {config.VIDEO_SOURCE}")
        # Test videosu yoksa oluşturmayı öner
        if config.VIDEO_SOURCE == "lane_test.mp4":
             print("İpucu: 'python generate_test_video.py' çalıştırarak test videosu oluşturun.")
        return

    # Kamera çözünürlüğünü ayarla (Webcam ise işe yarar)
    if isinstance(config.VIDEO_SOURCE, int):
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    # Video Listesini Al
    video_files = utils.scan_videos("Videos")
    # Eğer hiç video yoksa veya ana config'deki video dosyası listede yoksa listeye ekle (eğer dosya ise)
    current_video_idx = 0
    
    # Config'deki video zaten bir dosya ise ve listede varsa onun indeksini bul
    if isinstance(config.VIDEO_SOURCE, str) and os.path.exists(config.VIDEO_SOURCE):
        # Tam yol gerekebilir, şimdilik basit karşılaştırma
        pass

    # Trackbar için callback (boş)
    def nothing(x):
        pass

    # Trackbarları Oluştur (Sadece Headless değilse)
    if not config.HEADLESS_MODE:
        cv2.namedWindow("Otocar Main")
        # Değerleri 100 ile çarpıp int yapıyoruz (Trackbar float desteklemez)
        cv2.createTrackbar("KP x100", "Otocar Main", int(config.PID_KP * 100), 500, nothing)
        cv2.createTrackbar("KI x100", "Otocar Main", int(config.PID_KI * 100), 100, nothing)
        cv2.createTrackbar("KD x100", "Otocar Main", int(config.PID_KD * 100), 500, nothing)
        
        # Video Seçici (Eğer video dosyaları varsa)
        if len(video_files) > 0:
            cv2.createTrackbar("Video ID", "Otocar Main", 0, len(video_files) - 1, nothing)

    # İlk video kaynağını belirle
    current_source = config.VIDEO_SOURCE
    if len(video_files) > 0:
        current_source = video_files[0] # Varsayılan olarak listedeki ilk video ile başla
        
    print(f"İlk Kaynak: {current_source}")
    cap = cv2.VideoCapture(current_source)
    
    # ... (Çözünürlük ayarları vs aynı kalır)
    # Kamera çözünürlüğünü ayarla (Webcam ise işe yarar)
    if isinstance(current_source, int):
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    last_video_idx = -1

    while True:
        # Trackbar'dan Video Değişimi Kontrolü
        if not config.HEADLESS_MODE and len(video_files) > 0:
            try:
                vid_idx = cv2.getTrackbarPos("Video ID", "Otocar Main")
                if vid_idx != last_video_idx and vid_idx < len(video_files):
                    # Video Değiştir
                    print(f"Video değiştiriliyor: {video_files[vid_idx]}")
                    current_source = video_files[vid_idx]
                    cap.release()
                    cap = cv2.VideoCapture(current_source)
                    last_video_idx = vid_idx
            except:
                pass

        ret, frame = cap.read()
        if not ret:
            print("Video bitti. Başa sarılıyor...")
            if isinstance(current_source, str):
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            else:
                # Video okunamadıysa
                break
        
        height, width = frame.shape[:2]

        # Trackbar Değerlerini Oku (Canlı Tuning)
        if not config.HEADLESS_MODE:
            # Sadece pencere açıksa oku
            try:
                kp_val = cv2.getTrackbarPos("KP x100", "Otocar Main") / 100.0
                ki_val = cv2.getTrackbarPos("KI x100", "Otocar Main") / 100.0
                kd_val = cv2.getTrackbarPos("KD x100", "Otocar Main") / 100.0
                
                # PID Kontrolcüsünü Güncelle
                pid.Kp = kp_val
                pid.Ki = ki_val
                pid.Kd = kd_val
            except:
                pass # Pencere kapalıysa hata vermesin

        # Faz 1: Şerit Takip
        processed_frame, error, debug_thresh = lane_detector.process_frame(frame)
        
        # PID Hesaplama
        steering = pid.update(error)
        
        # Motor Hızlarını Hesapla
        # steering pozitif ise sağa dön (sol motor artar, sağ azalır)
        # steering negatif ise sola dön (sağ motor artar, sol azalır)
        left_speed = config.BASE_SPEED + steering
        right_speed = config.BASE_SPEED - steering
        
        # Hızları sınırla (0 ile MAX_SPEED arası veya -MAX ile +MAX arası donanıma göre)
        # Şimdilik sadece simülasyon print
        
        # Bilgi Ekranı
        # Hata ve PID Çıktısı
        cv2.putText(processed_frame, f"Error: {error} PID: {steering:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        # Motor Hızları
        cv2.putText(processed_frame, f"L: {int(left_speed)} R: {int(right_speed)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        # Video Adı
        vid_name = str(current_source)
        if len(vid_name) > 20: vid_name = "..." + vid_name[-17:]
        cv2.putText(processed_frame, f"Src: {vid_name}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        # PID Katsayıları
        pid_info = f"Kp: {pid.Kp} Ki: {pid.Ki} Kd: {pid.Kd}"
        cv2.putText(processed_frame, pid_info, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(processed_frame, "'S' to Save Config", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        if config.DEBUG_MODE and not config.HEADLESS_MODE:
            try:
                cv2.imshow("Otocar Main", processed_frame)
                # cv2.imshow("Lane Threshold", debug_thresh) # İkinci ekran kapatıldı
            except Exception as e:
                print(f"Ekran hatası (Headless moduna geçiliyor): {e}")
                config.HEADLESS_MODE = True
        
        # Klavye Kontrolü
        key = cv2.waitKey(25) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Kaydet
            utils.save_pid_config("config.py", pid.Kp, pid.Ki, pid.Kd)
            cv2.putText(processed_frame, "SAVED!", (width//2, height//2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            cv2.imshow("Otocar Main", processed_frame)
            cv2.waitKey(500) # Yarım saniye göster
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
