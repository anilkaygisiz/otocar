import re

def save_pid_config(filepath, kp, ki, kd):
    """
    config.py dosyasındaki PID değerlerini günceller.
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Regex ile değerleri bul ve değiştir
        content = re.sub(r'PID_KP = .*', f'PID_KP = {kp}', content)
        content = re.sub(r'PID_KI = .*', f'PID_KI = {ki}', content)
        content = re.sub(r'PID_KD = .*', f'PID_KD = {kd}', content)
        
        with open(filepath, 'w') as f:
            f.write(content)
            
        print(f"Konfigürasyon kaydedildi: P={kp} I={ki} D={kd}")
        return True
    except Exception as e:
        print(f"Kaydetme hatası: {e}")
        return False
