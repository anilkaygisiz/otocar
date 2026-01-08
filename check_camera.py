import cv2
import time
import sys

# v7: Pi 5 Explicit Formats (The "Golden" Tests)
GST_PIPELINES = [
    # 1. YUY2 Force (Standard for Pi 5 GStreamer)
    (
        "libcamerasrc ! video/x-raw, width=640, height=480, format=YUY2 ! "
        "videoconvert ! video/x-raw, format=BGR ! appsink drop=1",
        "Pi 5: Explicit YUY2"
    ),
    # 2. NV12 Force (What rpicam-hello uses)
    (
        "libcamerasrc ! video/x-raw, width=640, height=480, format=NV12 ! "
        "videoconvert ! video/x-raw, format=BGR ! appsink drop=1",
        "Pi 5: Explicit NV12"
    ),
    # 3. YUY2 with Queues (More stable)
    (
        "libcamerasrc ! video/x-raw, width=640, height=480, format=YUY2 ! queue ! "
        "videoconvert ! queue ! video/x-raw, format=BGR ! appsink drop=1",
        "Pi 5: YUY2 + Queues"
    ),
    # 4. Minimalist
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
    print("GStreamer destegi: OK")
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
    
    # 3 saniye veya 20 frame dene
    while time.time() - start < 3.0:
        ret, frame = cap.read()
        if ret:
            success_count += 1
            if success_count == 1:
                print(f"ILK FRAME BASARILI: {frame.shape}")
            if success_count > 10:
                print(f"Sonuc: BASARILI (Stabil akis var, {success_count} frame)")
                cap.release()
                return True
        else:
            time.sleep(0.01)
            
    cap.release()
    print("Sonuc: TIMEOUT (Frame gelmedi)")
    return False

def main():
    print("=== OTOCAR KAMERA TANI ARACI v7 (Remote Push) ===")
    check_gstreamer_support()
    
    works = False
    good_pipeline = ""
    
    for p, d in GST_PIPELINES:
        if test_pipeline(p, d):
            print(f"\n\n>>> TEBRIKLER! Calisan Ayar Bulundu: {d}")
            good_pipeline = p
            works = True
            break
            
    if works:
        print("\n\nLutfen config.py dosyasini su sekilde guncelleyin:")
        print(f"PI5_CAMERA_PIPELINE = '{good_pipeline}'")
    else:
        print("\n\n>>> HICBISEY CALISMADI <<<")
        print("Donanim rpicam-hello ile calisiyor ama OpenCV pipeline kuramiyor.")
        print("libcamera ve gstreamer paketlerini tekrar kontrol edin.")

if __name__ == "__main__":
    main()
