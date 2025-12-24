import cv2
import time

def test_camera(source, backend_name, backend_id):
    print(f"Testing Source '{source}' with {backend_name}...")
    try:
        if backend_id is not None:
             cap = cv2.VideoCapture(source, backend_id)
        else:
             cap = cv2.VideoCapture(source)
             
        if not cap.isOpened():
            print(f"[-] Failed to open '{source}'")
            return False
            
        # FORCE LOW RES & MJPG BEFORE READ
        # This is critical for Raspberry Pi "Failed to allocate memory" errors
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        time.sleep(1) # Warmup
        
        # Try to read
        ret, frame = cap.read()
        if ret:
            print(f"[+] SUCCESS! Camera works with {backend_name} (Low Res Mode)")
            print(f"    Resolution: {int(cap.get(3))}x{int(cap.get(4))}")
            cap.release()
            return True
        else:
            print(f"[-] Opened, set MJPG/320x240, but failed to read frame.")
            cap.release()
            return False
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

print("Scanning for cameras with LOW RES / MJPG force...")
scenarios = [
    (0, "Index 0 (V4L2 + MJPG Fix)", cv2.CAP_V4L2),
    (0, "Index 0 (Any)", cv2.CAP_ANY),
]

found = False
for source, name, bid in scenarios:
    if test_camera(source, name, bid):
        print(f"\nWINNER: {name}")
        found = True
        break

if not found:
    print("\nXXX NO CAMERA FOUND! XXX")
    print("Suggestion: Try restarting the Raspberry Pi. The video memory might be locked by a crashed process.")
else:
    print("\nPlease report the WINNER to me.")
