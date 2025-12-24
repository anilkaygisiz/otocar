import cv2
import time

def test_camera_robust(index):
    print(f"--- Testing Index {index} ---")
    cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
    
    if not cap.isOpened():
        print(f"[-] Failed to open Index {index}")
        return False
    
    # Read properties
    w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    backend = cap.get(cv2.CAP_PROP_BACKEND)
    print(f"    Properties -> Res: {int(w)}x{int(h)} | FPS: {fps} | Backend ID: {backend}")
    
    # WARMUP LOOP: Try reading multiple frames
    print("    Attempting to read 10 frames (Warmup)...")
    success = False
    for i in range(10):
        ret, frame = cap.read()
        if ret:
            print(f"    [+] Frame {i+1} captured! Shape: {frame.shape}")
            success = True
            break # Found it!
        else:
            print(f"    [.] Frame {i+1} failed...")
            time.sleep(0.2)
            
    cap.release()
    
    if success:
        print("WINNER! This index works.")
        return True
    else:
        print("FAILED to capture any frames.")
        return False

# Test common indices
indices = [0, 1, 10]
found = False

for idx in indices:
    if test_camera_robust(idx):
        found = True
        break

if not found:
    print("\nXXX NO WORKING CAMERA FOUND XXX")
    print("\nLutfen terminale su komutu yazip ciktisini bana atin:")
    print("v4l2-ctl --list-formats-ext")
    print("(Eger komut yoksa: sudo apt-get install v4l-utils)")
