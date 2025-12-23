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

    # İlk video kaynağını belirle
    current_source = config.VIDEO_SOURCE
    if len(video_files) > 0:
        current_source = video_files[0] # Varsayılan olarak listedeki ilk video ile başla
        current_video_idx = 0
        
    print(f"İlk Kaynak: {current_source}")
    cap = cv2.VideoCapture(current_source)
    
    video_change_request = False # Döngü içinde değişim isteği bayrağı

    while True:
        ret, frame = cap.read()
        
        # Video bittiyse veya değişim isteniyorsa
        if not ret:
            if isinstance(current_source, str):
                # Video dosyası ise başa sar
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            else:
                print("Kare alınamadı, çıkılıyor...")
                break
        
        # --- UI FIX: Sabit Çözünürlük ---
        # Gelen görüntü ne olursa olsun, config'deki boyuta zorla.
        # Bu sayede pencere boyutu sabit kalır.
        frame = cv2.resize(frame, (config.FRAME_WIDTH, config.FRAME_HEIGHT))
        
        height, width = frame.shape[:2]

        # Trackbar Değerlerini Oku (Canlı Tuning)
        if not config.HEADLESS_MODE:
            try:
                kp_val = cv2.getTrackbarPos("KP x100", "Otocar Main") / 100.0
                ki_val = cv2.getTrackbarPos("KI x100", "Otocar Main") / 100.0
                kd_val = cv2.getTrackbarPos("KD x100", "Otocar Main") / 100.0
                
                pid.Kp = kp_val
                pid.Ki = ki_val
                pid.Kd = kd_val
            except:
                pass

        # Faz 1: Şerit Takip
        processed_frame, error, debug_thresh = lane_detector.process_frame(frame)
        
        # PID Hesaplama
        steering = pid.update(error)
        
        left_speed = config.BASE_SPEED + steering
        right_speed = config.BASE_SPEED - steering
        
        # Bilgi Ekranı
        cv2.putText(processed_frame, f"Error: {error} PID: {steering:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(processed_frame, f"L: {int(left_speed)} R: {int(right_speed)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        # Video Adı
        vid_name = str(current_source)
        if len(vid_name) > 20: vid_name = "..." + vid_name[-17:]
        cv2.putText(processed_frame, f"Src ({current_video_idx+1}/{len(video_files)}): {vid_name}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(processed_frame, "[N]ext / [P]rev Video", (10, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

        # Mod Bilgisi
        mode_color = (0, 255, 0) if config.DETECTION_MODE == 'COLOR' else (255, 0, 255)
        cv2.putText(processed_frame, f"MODE: {config.DETECTION_MODE} ('m' toggle)", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, mode_color, 2)

        # PID Katsayıları
        pid_info = f"Kp: {pid.Kp} Ki: {pid.Ki} Kd: {pid.Kd}"
        cv2.putText(processed_frame, pid_info, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(processed_frame, "'S' Save | 'Q' Quit", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        if config.DEBUG_MODE and not config.HEADLESS_MODE:
            try:
                cv2.imshow("Otocar Main", processed_frame)
            except Exception as e:
                print(f"Ekran hatası: {e}")
                config.HEADLESS_MODE = True
        
        # Klavye Kontrolü
        key = cv2.waitKey(25) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('m'):
            config.DETECTION_MODE = 'COLOR' if config.DETECTION_MODE == 'BRIGHTNESS' else 'BRIGHTNESS'
        elif key == ord('s'):
            utils.save_pid_config("config.py", pid.Kp, pid.Ki, pid.Kd)
            cv2.putText(processed_frame, "SAVED!", (width//2, height//2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            cv2.imshow("Otocar Main", processed_frame)
            cv2.waitKey(500)
        
        # Video Değiştirme (Klavye ile)
        elif key == ord('n') or key == ord('p'):
            if len(video_files) > 0:
                if key == ord('n'):
                    current_video_idx = (current_video_idx + 1) % len(video_files)
                elif key == ord('p'):
                    current_video_idx = (current_video_idx - 1 + len(video_files)) % len(video_files)
                
                current_source = video_files[current_video_idx]
                print(f"Video değiştiriliyor: {current_source}")
                cap.release()
                cap = cv2.VideoCapture(current_source)
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
