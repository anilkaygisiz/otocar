import cv2
import config
import time
import os
import numpy as np

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
    # Kamera (0) kaynağını listenin başına ekle
    video_files.insert(0, 0)
    
    # ... (Video config check - skipped for brevity as we prioritize the list for navigation)

    # İlk video kaynağını belirle
    current_source = config.VIDEO_SOURCE
    current_video_idx = 0
    
    # Configdeki kaynak listede varsa indexi güncelle
    if current_source in video_files:
        current_video_idx = video_files.index(current_source)
    elif len(video_files) > 0:
        current_source = video_files[0]
        
    first_run = True
    
    # Akıllı Kamera Bulucu
    def find_working_camera():
        # NOT: Raspberry Pi CSI Kamera kullanıyorsanız "Legacy Camera" modu açık olmalı!
        # (sudo raspi-config -> Interface -> Legacy Camera -> Yes)
        
        # 1. Standart V4L2 Taraması (Pi 4 Legacy / USB Cam)
        indices = [0, 1, 10]
        for idx in indices:
            print(f"Kamera aranıyor (V4L2): Index {idx}...")
            cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
                # MJPG formatını zorla (Daha hızlıdır)
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                time.sleep(1)
                
                # Test okuması
                ret, _ = cap.read()
                if ret:
                    print(f"KAMERA BULUNDU: Index {idx} (V4L2)")
                    return cap, idx
                cap.release()

        # 2. Raspberry Pi 5 / Libcamera Taraması (GStreamer)
        print("V4L2 başarısız. Pi 5 Libcamera GStreamer deneniyor...")
        try:
            gst_pipeline = config.PI5_CAMERA_PIPELINE
            cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    print(f"KAMERA BULUNDU: Libcamera GStreamer")
                    return cap, "GSTREAMER"
                cap.release()
        except Exception as e:
            print(f"GStreamer hatası: {e}")

        return None, None
    
    while True:
        # İlk turda veya değişimde VideoCapture başlat
        if 'cap' not in locals() or cap is None or not cap.isOpened():
             print(f"Kaynak başlatılıyor: {current_source}")
             
             if current_source == 0:
                 # Yeni akıllı kamera bulucu kullan
                 new_cap, found_source = find_working_camera()
                 if new_cap:
                     cap = new_cap
                     current_source = found_source # Kaynağı güncelleyelim
                 else:
                     print("Hata: Hiçbir kamera bulunamadı!")
                     # Siyah ekran oluşturup hata mesajı göster
                     cap = None # cap'i geçersiz kıl
                     ret = False # Okuma başarısız say
                     # Frame uret ve bekle, sonra basa don
                     frame = np.zeros((config.FRAME_HEIGHT, config.FRAME_WIDTH, 3), dtype=np.uint8)
                     cv2.putText(frame, "KAMERA BULUNAMADI!", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                     cv2.putText(frame, "Baglantiyi ve 'install_pi5.sh'i kontrol et", (20, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
                     
                     # Ekranda goster (Eger GUI calisiyorsa)
                     try:
                        cv2.imshow("Otocar Lane Detection", frame)
                        if cv2.waitKey(500) & 0xFF == ord('q'):
                            break
                     except:
                        time.sleep(1)
                     continue # Döngünün başına dön
             else:
                 cap = cv2.VideoCapture(current_source)

        ret, frame = cap.read()
        
        # Hata Yönetimi: Okuma başarısızsa
        if not ret:
            if isinstance(current_source, str) and current_source != "GSTREAMER": # "GSTREAMER" özel bir durum, dosya değil
                # Video dosyası ise başa sar
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            else:
                # Kamera hatası: Siyah ekran oluştur ve hatayı bas
                print("Kamera hatası, yeniden deneniyor...")
                cap.release() # Kaynağı serbest bırak
                frame = np.zeros((config.FRAME_HEIGHT, config.FRAME_WIDTH, 3), dtype=np.uint8)
                cv2.putText(frame, "KAMERA HATASI!", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, "Baglantiyi kontrol et", (50, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
                time.sleep(0.5) # CPU'yu yorma
        
        # --- UI FIX: Sabit Çözünürlük ---
        if frame is not None:
             frame = cv2.resize(frame, (config.FRAME_WIDTH, config.FRAME_HEIGHT))
        
        # Faz 1: Şerit Takip (Eğer frame doluysa)
        # Hata durumunda frame siyah olduğu için işlem yapmaya gerek yok ama UI bozulmasın diye devam edebilir
        if ret:
            processed_frame, error, debug_thresh = lane_detector.process_frame(frame)
        else:
            processed_frame = frame
            error = 0
            steering = 0
            left_speed = 0
            right_speed = 0
        
        # PID Hesaplama (Sadece görüntü varsa)
        if ret:
            steering = pid.update(error)
            left_speed = config.BASE_SPEED + steering
            right_speed = config.BASE_SPEED - steering
        
        # Bilgi Ekranı (OSD) - Her durumda bas
        cv2.putText(processed_frame, f"Error: {error} PID: {steering:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(processed_frame, f"L: {int(left_speed)} R: {int(right_speed)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        # Video Adı
        if current_source == 0:
            vid_name = "CAMERA LIVE"
        else:
            vid_name = str(current_source)
            if len(vid_name) > 20: vid_name = "..." + vid_name[-17:]
            
        cv2.putText(processed_frame, f"Src ({current_video_idx+1}/{len(video_files)}): {vid_name}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(processed_frame, "[N]ext/[P]rev | [C]amera", (10, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

        # Mod Bilgisi
        mode_color = (0, 255, 0) if config.DETECTION_MODE == 'COLOR' else (255, 0, 255)
        cv2.putText(processed_frame, f"MODE: {config.DETECTION_MODE} ('m' toggle)", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, mode_color, 2)

        # PID Katsayıları ve Kısayollar
        pid_info = f"Kp: {pid.Kp:.2f} Ki: {pid.Ki:.2f} Kd: {pid.Kd:.2f}"
        cv2.putText(processed_frame, pid_info, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        shortcuts = "Kp: T/G | Ki: R/F | Kd: Y/H | 'S' Save"
        cv2.putText(processed_frame, shortcuts, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        if config.DEBUG_MODE and not config.HEADLESS_MODE:
            try:
                cv2.imshow("Otocar Main", processed_frame)
            except Exception as e:
                print(f"Ekran hatası: {e}")
                config.HEADLESS_MODE = True
        
        # Klavye Kontrolü (Hata olsa bile çalışmalı!)
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
        
        # PID Tuning Kısayolları
        elif key == ord('t'): pid.Kp += 0.05
        elif key == ord('g'): pid.Kp = max(0, pid.Kp - 0.05)
        elif key == ord('r'): pid.Ki += 0.05
        elif key == ord('f'): pid.Ki = max(0, pid.Ki - 0.05)
        elif key == ord('y'): pid.Kd += 0.05
        elif key == ord('h'): pid.Kd = max(0, pid.Kd - 0.05)
        
        # Trackbar Update (Headless değilse)
        if not config.HEADLESS_MODE and key in [ord('t'), ord('g'), ord('r'), ord('f'), ord('y'), ord('h')]:
             try:
                 cv2.setTrackbarPos("KP x100", "Otocar Main", int(pid.Kp * 100))
                 cv2.setTrackbarPos("KI x100", "Otocar Main", int(pid.Ki * 100))
                 cv2.setTrackbarPos("KD x100", "Otocar Main", int(pid.Kd * 100))
             except: pass

        # Video Değiştirme
        elif key == ord('n') or key == ord('p') or key == ord('c'):
            video_changed = False
            if len(video_files) > 0:
                if key == ord('n'):
                    current_video_idx = (current_video_idx + 1) % len(video_files)
                    video_changed = True
                elif key == ord('p'):
                    current_video_idx = (current_video_idx - 1 + len(video_files)) % len(video_files)
                    video_changed = True
                elif key == ord('c'):
                    if 0 in video_files:
                        current_video_idx = video_files.index(0)
                        video_changed = True
            
            if video_changed:
                current_source = video_files[current_video_idx]
                print(f"Video değiştiriliyor: {current_source}")
                cap.release()
                # cap yeniden oluşturulacak (döngü başında)
                del cap 

            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
