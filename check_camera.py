import cv2
import time

def test_config(index, backend_name, backend_id, use_gray=False):
    desc = f"Index {index} | {backend_name}"
    if use_gray: desc += " | GRAYSCALE/RAW"
    
    print(f"--- Testing: {desc} ---")
    
    cap = cv2.VideoCapture(index, backend_id)
    if not cap.isOpened():
        print("[-] Failed to open.")
        return False
        
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    if use_gray:
        # Prevent auto-conversion to RGB (gets raw data/YUYV or Grey)
        cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)
        
    # Read properties
    aw = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    ah = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"    Set -> {int(aw)}x{int(ah)}")
    
    time.sleep(1) # Warmup
    
    # Read loop
    success = False
    for i in range(20): # Increased attempts
        ret, frame = cap.read()
        if ret:
            print(f"[+] SUCCESS! Frame {i} captured.")
            if frame is not None:
                print(f"    Shape: {frame.shape}")
                # If raw, it might be 2D or YUYV
            success = True
            break
        time.sleep(0.1)
        
    cap.release()
    return success

# Scenarios
scenarios = [
    # 1. Try CAP_ANY (Let OpenCV decide, GStreamer might work now that pipewire is gone)
    (0, "CAP_ANY (Auto)", cv2.CAP_ANY, False),
    
    # 2. Try V4L2 Grayscale Force (Bandwidth saver)
    (0, "V4L2 (Raw/Gray)", cv2.CAP_V4L2, True),
    
    # 3. Last ditch: Index 0, V4L2, Normal
    (0, "V4L2 (RGB)", cv2.CAP_V4L2, False)
]

print("Starting Camera Diagnostics (v4 - desperation)...")
found = False
for idx, name, bid, gray in scenarios:
    if test_config(idx, name, bid, gray):
        print(f"\nWINNER FOUND: {name}")
        if gray: print("NOTE: Using Grayscale mode (Good for Lane Detection!)")
        found = True
        break
        
if not found:
    print("\nXXX ALL FAILED XXX")

