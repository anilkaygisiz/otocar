"""
Camera Wrapper - Pi 5 ve diğer platformlar için uyumlu kamera sınıfı.

Pi 5'te picamera2, diğer platformlarda OpenCV VideoCapture kullanır.
"""

import os
import cv2
import time
import sys

# Libcamera loglarını sustur (sadece ERROR göster)
os.environ["LIBCAMERA_LOG_LEVELS"] = "*:ERROR"

# Platform tespiti
IS_PI5 = False
try:
    from picamera2 import Picamera2
    IS_PI5 = True
    print("[CameraWrapper] Pi 5 modu aktif (picamera2)")
except ImportError:
    print("[CameraWrapper] OpenCV modu aktif")


class CameraWrapper:
    """
    Platform bağımsız kamera sınıfı.
    OpenCV VideoCapture API'sine benzer arayüz sunar.
    """
    
    def __init__(self, source=0, width=640, height=480):
        self.width = width
        self.height = height
        self.source = source
        self.cap = None
        self.picam = None
        self.is_opened = False
        self.use_picamera2 = False
        
    def open(self):
        """Kamerayı açar."""
        # Önce picamera2 dene (Pi 5)
        if IS_PI5 and (self.source == 0 or self.source == "picamera2"):
            try:
                self.picam = Picamera2()
                config = self.picam.create_preview_configuration(
                    main={"size": (self.width, self.height), "format": "BGR888"}
                )
                self.picam.configure(config)
                self.picam.start()
                time.sleep(0.5)  # Kamera ısınması için bekle
                self.use_picamera2 = True
                self.is_opened = True
                print(f"[CameraWrapper] picamera2 ile açıldı: {self.width}x{self.height}")
                return True
            except Exception as e:
                print(f"[CameraWrapper] picamera2 hatası: {e}")
                self.picam = None
        
        # OpenCV VideoCapture (Fallback veya dosya)
        try:
            if isinstance(self.source, str) and self.source != "picamera2":
                # Video dosyası
                self.cap = cv2.VideoCapture(self.source)
            else:
                # Kamera index
                self.cap = cv2.VideoCapture(self.source, cv2.CAP_V4L2)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            
            if self.cap.isOpened():
                self.is_opened = True
                self.use_picamera2 = False
                print(f"[CameraWrapper] OpenCV ile açıldı: {self.source}")
                return True
        except Exception as e:
            print(f"[CameraWrapper] OpenCV hatası: {e}")
        
        return False
    
    def read(self):
        """
        Bir frame okur.
        Returns: (success: bool, frame: np.ndarray)
        """
        if not self.is_opened:
            return False, None
        
        if self.use_picamera2 and self.picam:
            try:
                frame = self.picam.capture_array()
                return True, frame
            except Exception as e:
                print(f"[CameraWrapper] picamera2 read hatası: {e}")
                return False, None
        
        if self.cap:
            return self.cap.read()
        
        return False, None
    
    def isOpened(self):
        """Kameranın açık olup olmadığını döner."""
        return self.is_opened
    
    def release(self):
        """Kamerayı kapatır."""
        if self.picam:
            try:
                self.picam.stop()
                self.picam.close()
            except:
                pass
            self.picam = None
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.is_opened = False
        print("[CameraWrapper] Kamera kapatıldı")
    
    def set(self, prop, value):
        """OpenCV uyumluluğu için property setter."""
        if self.cap:
            return self.cap.set(prop, value)
        return False
    
    def get(self, prop):
        """OpenCV uyumluluğu için property getter."""
        if self.cap:
            return self.cap.get(prop)
        
        # picamera2 için temel değerler
        if prop == cv2.CAP_PROP_FRAME_WIDTH:
            return self.width
        if prop == cv2.CAP_PROP_FRAME_HEIGHT:
            return self.height
        return 0


def find_working_camera(width=640, height=480):
    """
    Çalışan bir kamera bulur.
    Returns: (CameraWrapper, source_name) veya (None, None)
    """
    # 1. Pi 5 picamera2
    if IS_PI5:
        cam = CameraWrapper(source=0, width=width, height=height)
        if cam.open():
            # Test frame
            ret, frame = cam.read()
            if ret and frame is not None:
                print("[find_working_camera] picamera2 çalışıyor!")
                return cam, "picamera2"
            cam.release()
    
    # 2. V4L2 cihazları
    for idx in [0, 1, 2]:
        cam = CameraWrapper(source=idx, width=width, height=height)
        if cam.open():
            ret, frame = cam.read()
            if ret and frame is not None:
                print(f"[find_working_camera] V4L2 index {idx} çalışıyor!")
                return cam, f"v4l2:{idx}"
            cam.release()
    
    return None, None


# Test
if __name__ == "__main__":
    print("=== CameraWrapper Test ===")
    
    cam, source = find_working_camera()
    if cam is None:
        print("Kamera bulunamadı!")
        sys.exit(1)
    
    print(f"Kamera bulundu: {source}")
    
    # 10 frame oku ve göster
    for i in range(10):
        ret, frame = cam.read()
        if ret:
            cv2.putText(frame, f"Frame {i+1}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Test", frame)
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
    
    cam.release()
    cv2.destroyAllWindows()
    print("Test tamamlandı!")
