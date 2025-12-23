import cv2
import config
import time

def main():
    print(f"Otocar Başlatılıyor... Video Kaynağı: {config.VIDEO_SOURCE}")
    
    cap = cv2.VideoCapture(config.VIDEO_SOURCE)
    
    if not cap.isOpened():
        print(f"Hata: Video kaynağı açılamadı: {config.VIDEO_SOURCE}")
        return

    # Kamera çözünürlüğünü ayarla (Webcam ise işe yarar)
    if isinstance(config.VIDEO_SOURCE, int):
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Video bitti veya kare alınamadı.")
            # Video ise başa sar (Loop)
            if isinstance(config.VIDEO_SOURCE, str):
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            else:
                break
        
        # Görüntü İşleme (Burada Faz 1 devreye girecek)
        # Örnek: Griye çevir
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if config.DEBUG_MODE:
            cv2.imshow("Otocar Kamera", frame)
            cv2.imshow("Gri Mod", gray)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
