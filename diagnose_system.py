import subprocess
import os

def run_cmd(cmd):
    print(f"\n> {cmd}")
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        print(output.decode('utf-8'))
        return True
    except subprocess.CalledProcessError as e:
        print(f"FAILED (Exit Code: {e.returncode})")
        print(e.output.decode('utf-8'))
        return False

print("=== SISTEM SEVIYESI KAMERA TESTI ===")

# 1. GPU Memory Check
print("\n[1] GPU Bellek Kontrolü (Raspberry Pi)")
run_cmd("vcgencmd get_mem gpu")

# 2. V4L2 Device Info
print("\n[2] Kamera Format ve Ayar Bilgisi")
run_cmd("v4l2-ctl -V")

# 3. FFMPEG Capture Test (The Ultimate Test)
print("\n[3] FFMPEG ile Fotoğraf Çekme Testi (Raw V4L2)")
# Try to grab 1 frame using mjpeg or yuyv
if run_cmd("ffmpeg -y -f v4l2 -video_size 640x480 -i /dev/video0 -frames:v 1 test_image.jpg"):
    print("\n[+] KAMERA ÇALIŞIYOR! 'test_image.jpg' oluşturuldu.")
else:
    print("\n[-] FFMPEG bile görüntü alamadı.")

# 4. Libcamera Test (If available)
print("\n[4] Libcamera Testi")
run_cmd("libcamera-hello --list-cameras")

print("\n=== TEST BITTI ===")
if os.path.exists("test_image.jpg"):
    print("SONUÇ: Kamera donanımı SAĞLAM. Sorun OpenCV/Python kütüphanesinde.")
else:
    print("SONUÇ: Kamera donanımı veya sürücüsü YANIT VERMİYOR (Sistem genelinde bozuk).")
