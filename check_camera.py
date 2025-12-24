import cv2
import time

def test_config(index, width, height, fourcc=None):
    desc = f"Index {index} | {width}x{height}"
    if fourcc: desc += f" | {fourcc}"
    else: desc += " | Auto Format"
    
    print(f"--- Testing: {desc} ---")
    
    cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
    if not cap.isOpened():
        print("[-] Failed to open.")
        return False
        
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    if fourcc:
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc))
        
    # Read Actual properties
    aw = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    ah = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"    Set -> {int(aw)}x{int(ah)}")
    
    # Warmup
    success = False
    for i in range(10):
        ret, frame = cap.read()
        if ret:
            print(f"[+] SUCCESS! Frame {i} captured. Shape: {frame.shape}")
            success = True
            break
        time.sleep(0.2)
        
    cap.release()
    return success

# Scenarios to try
configs = [
    # 1. YuzTanima Replica (V4L2, 640x480, Auto Format)
    (0, 640, 480, None),
    
    # 2. Lower Res (V4L2, 320x240, Auto Format)
    (0, 320, 240, None),
    
    # 3. Explicit YUYV (Last resort)
    (0, 640, 480, "YUYV"),
    
    # 4. Try Index 1
    (1, 640, 480, None)
]

print("Starting Camera Diagnostics (v3 - Minimalist)...")
for idx, w, h, fcc in configs:
    if test_config(idx, w, h, fcc):
        print("\nWINNER FOUND!")
        print(f"Index: {idx}, Res: {w}x{h}, FourCC: {fcc}")
        break  

