import cv2
import time

def test_camera_yuztanima_style(index):
    print(f"Testing Index {index} (YuzTanima Style: V4L2 + 640x480)...")
    
    # 1. Open with V4L2
    cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
    
    if not cap.isOpened():
        print(f"[-] Failed to open Index {index}")
        return False
        
    # 2. Set Resolution (Critical step from YuzTanima)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Optional: Wait a bit
    time.sleep(1)
    
    # 3. Read
    ret, frame = cap.read()
    if ret:
        print(f"[+] SUCCESS! Camera works!")
        print(f"    Resolution: {frame.shape[1]}x{frame.shape[0]}")
        cap.release()
        return True
    else:
        print(f"[-] Opened but failed to read frame.")
        cap.release()
        return False

indices = [0, 1, 10, -1]

found = False
for idx in indices:
    if test_camera_yuztanima_style(idx):
        found = True
        break

if not found:
    print("\nXXX HALA ÇALIŞMADI XXX")
else:
    print("\nÇALIŞTI! Lütfen main.py dosyasını buna göre güncellememi isteyin.")

if not found:
    print("\nXXX NO CAMERA FOUND! XXX")
    print("Suggestion: Try restarting the Raspberry Pi. The video memory might be locked by a crashed process.")
else:
    print("\nPlease report the WINNER to me.")
