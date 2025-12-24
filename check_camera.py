import cv2
import time

def test_camera_yuyv(source, backend_name, backend_id):
    print(f"--- Testing {backend_name} ---")
    print(f"    Source: {source}")
    
    try:
        if backend_id is not None:
             cap = cv2.VideoCapture(source, backend_id)
        else:
             cap = cv2.VideoCapture(source)
             
        if not cap.isOpened():
            print(f"[-] Failed to open.")
            return False
            
        # FORCE YUYV (Since MJPG is missing)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y', 'U', 'Y', 'V'))
        
        # Read properties to confirm
        w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"    Configured -> Res: {int(w)}x{int(h)}")

        # Warmup read
        success = False
        for i in range(5):
            ret, frame = cap.read()
            if ret:
                print(f"[+] SUCCESS! Frame received. Shape: {frame.shape}")
                print(f"    This configuration works!")
                success = True
                break
            time.sleep(0.5)
            
        cap.release()
        return success
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

# Scenarios based on v4l2-ctl output (YUYV supported)
scenarios = [
    # 1. Standard V4L2 with YUYV force
    (0, "OpenCV V4L2 (Force YUYV)", cv2.CAP_V4L2),
    
    # 2. GStreamer Pipeline (Explicit YUY2)
    ("v4l2src device=/dev/video0 ! video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! videoconvert ! appsink", 
     "GStreamer Pipeline (YUY2)", cv2.CAP_GSTREAMER),
     
    # 3. Libcamera Source (Newer Pi OS)
    ("libcamerasrc ! video/x-raw,width=640,height=480,framerate=30/1 ! videoconvert ! appsink", 
     "GStreamer Libcamera", cv2.CAP_GSTREAMER)
]

found = False
for source, name, bid in scenarios:
    if test_camera_yuyv(source, name, bid):
        print(f"\nWINNER: {name}")
        print(f"Source String: {source}")
        found = True
        break

if not found:
    print("\nXXX NO WORKING CONFIGURATION FOUND XXX")
else:
    print("\nPlease report the WINNER source to me.")
