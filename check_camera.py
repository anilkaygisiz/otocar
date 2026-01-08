import cv2
import time
import sys

# v7: Pi 5 Explicit Formats (The "Golden" Tests)
GST_PIPELINES = [
    (
        "libcamerasrc ! video/x-raw, width=640, height=480, format=YUY2 ! "
        "videoconvert ! video/x-raw, format=BGR ! appsink drop=1",
        "Pi 5: Explicit YUY2 (Recommended)"
    ),
    (
        "libcamerasrc ! video/x-raw, width=640, height=480, format=NV12 ! "
        "videoconvert ! video/x-raw, format=BGR ! appsink drop=1",
        "Pi 5: Explicit NV12"
    ),
    (
        "libcamerasrc ! video/x-raw, width=640, height=480 ! "
        "videoconvert ! video/x-raw, format=BGR ! appsink drop=1",
        "Pi 5: Explicit Res (Auto Format)"
    ),
    (
        "libcamerasrc ! videoconvert ! video/x-raw, format=BGR ! appsink drop=1", 
        "Pi 5: Fully Auto"
    ),
]

def check_gstreamer_support():
    try:
        build_info = cv2.getBuildInformation()
        if "GStreamer: NO" in build_info:
            print("KRITIK: OpenCV GStreamer destegi YOK!")
            return False
    except:
        pass
    return True

def test_pipeline(pipeline, desc):
    print(f"\n--- TEST: {desc} ---")
    print(f"Pipeline: {pipeline}")
    
    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
    if not cap.isOpened():
        print("Sonuc: ACILMADI (isOpened=False)")
        return False
        
    print("Kamera acildi, frame okunuyor...")
    success_count = 0
    start = time.time()
    
    while time.time() - start < 3.0: # 3 saniye dene
        ret, frame = cap.read()
        if ret:
            success_count += 1
            if success_count == 1:
                print(f"ILK FRAME BASARILI: {frame.shape}")
                # Birkac frame daha oku emin ol
            if success_count > 10:
                print("Sonuc: BASARILI (Stabil akis var)")
                cap.release()
                return True
        else:
            time.sleep(0.01)
            
    cap.release()
    print("Sonuc: TIMEOUT (Frame gelmedi)")
    return False

def main():
    print("=== OTOAR KAMERA TANI ARACI v7 (Remote Push) ===")
    check_gstreamer_support()
    
    works = False
    for p, d in GST_PIPELINES:
        if test_pipeline(p, d):
            print(f"\n\n>>> TEBRIKLER! Calisan Ayar Bulundu: {d}")
            print("config.py dosyasina sunu yazin:")
            print(f"PI5_CAMERA_PIPELINE = '{p}'")
            works = True
            break
            
    if not works:
        print("\n\n>>> HICBISEY CALISMADI <<<")
        print("Lutfen 'rpicam-hello' komutunu deneyin.")

if __name__ == "__main__":
    main()
