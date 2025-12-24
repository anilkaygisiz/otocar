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
        
        # Try to read
        ret, frame = cap.read()
        if ret:
            print(f"[+] SUCCESS! Camera works with {backend_name}")
            print(f"    Resolution: {int(cap.get(3))}x{int(cap.get(4))}")
            cap.release()
            return True
        else:
            print(f"[-] Opened but failed to read frame.")
            cap.release()
            return False
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

print("Scanning for cameras...")
scenarios = [
    (0, "Index 0 (V4L2)", cv2.CAP_V4L2),
    (0, "Index 0 (GStreamer Auto)", cv2.CAP_GSTREAMER),
    (0, "Index 0 (Any)", cv2.CAP_ANY),
    (1, "Index 1 (V4L2)", cv2.CAP_V4L2),
    ("v4l2src device=/dev/video0 ! video/x-raw, width=640, height=480, framerate=30/1 ! videoconvert ! appsink", "GStreamer Pipeline", cv2.CAP_GSTREAMER),
    (10, "Index 10 (Libcamera V4L2)", cv2.CAP_V4L2)
]

found = False
for source, name, bid in scenarios:
    if test_camera(source, name, bid):
        print(f"\nWINNER: {name}")
        found = True
        break

if not found:
    print("\nXXX NO CAMERA FOUND! XXX")
else:
    print("\nPlease report the WINNER to me.")
