import cv2
import config
import time

import lane_detector
import pid_controller

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

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Video bitti. Başa sarılıyor...")
            if isinstance(config.VIDEO_SOURCE, str):
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            else:
                break
        
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
        cv2.putText(processed_frame, f"Error: {error} PID: {steering:.2f}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(processed_frame, f"L: {int(left_speed)} R: {int(right_speed)}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        if config.DEBUG_MODE:
            cv2.imshow("Otocar Main", processed_frame)
            cv2.imshow("Lane Threshold", debug_thresh)
        
        # 'q' ile çıkış
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
