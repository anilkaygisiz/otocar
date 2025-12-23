import cv2
import numpy as np

def generate_video(filename="lane_test.mp4", width=640, height=480, duration=15, fps=30):
    print(f"Video oluşturuluyor: {filename} ({duration} saniye)")
    
    # Codec ayarları
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    
    total_frames = duration * fps
    
    # Yol parametreleri
    lane_width = 300
    line_thickness = 20
    
    for i in range(total_frames):
        # Siyah zemin
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Yolun merkezi (Zamanla değişerek viraj oluşturacak)
        # Sinüs dalgası ile sağ-sol hareketi simüle ediyoruz
        center_x = width // 2 + int(150 * np.sin(2 * np.pi * i / (total_frames / 2)))
        
        # Şerit noktaları
        pt1 = (center_x - lane_width // 2, height) # Sol alt (ekran dışından gelebilir)
        pt2 = (center_x + lane_width // 2, height) # Sağ alt
        
        # Üst noktalar (Perspektif etkisi için biraz daha dar)
        pt3 = (center_x + (lane_width // 4), height // 2) # Sağ üst
        pt4 = (center_x - (lane_width // 4), height // 2) # Sol üst
        
        # Beyaz şeritleri çiz (Poligon olarak değil, sadece kenar çizgileri olarak çizelim ki şerit takibi olsun)
        # Sol çizgi
        cv2.line(frame, (center_x - lane_width // 2, height), (int(width/2 - 50 + 100 * np.sin(i/50)), height//2), (255, 255, 255), line_thickness)
        # Sağ çizgi
        cv2.line(frame, (center_x + lane_width // 2, height), (int(width/2 + 50 + 100 * np.sin(i/50)), height//2), (255, 255, 255), line_thickness)
        
        # Basit bir yol çizimi: Ortada kesikli çizgi olmadan, sadece kenar şeritleri simüle ediyoruz. 
        # Daha dinamik bir viraj için her satırı kaydırarak çizmek daha iyi ama bu basit çizim iş görür.
        # Hadi biraz daha gerçekçi yapalım:
        
        frame[:] = 0 # Sıfırla
        
        # Viraj eğriliği (-1 ile 1 arası)
        curve = np.sin(i / 50) * 100
        
        for y in range(height // 2, height):
            # Perspektif etkisi: Y azaldıkça (yukarı çıktıkça) genişlik azalır
            perspective_factor = (y - height // 2) / (height // 2) # 0 (ufuk) ile 1 (en alt) arası
            
            # Yol genişliği aşağıda geniş, yukarıda dar
            w = int(10 + perspective_factor * lane_width)
            
            # X Merkezi: Viraj eğriliği y'ye göre değişir (yukarısı daha çok kayar gibi dursa da aslında kümülatif kayma önemlidir)
            # Basit model: x = center + curve * (1 - perspective)
            # Bu tam fiziksel değil ama görsel olarak iş görür.
            
            x_center = width // 2 + int(curve * (1 - perspective_factor)**2 * 3) 
            # Düzeltme: Virajın 'dönüşü'
            
            # Daha basit bir yöntem: Çizgi çizgi çizelim
            pass

        # Tekrar en basit yönteme dönelim: Çizgi çizmek.
        # Sol şerit çiz
        left_start = (int(width/2 - 100 + curve), height)
        left_end = (int(width/2 - 20), height//2)
        cv2.line(frame, left_start, left_end, (255, 255, 255), line_thickness)

        # Sağ şerit çiz
        right_start = (int(width/2 + 100 + curve), height)
        right_end = (int(width/2 + 20), height//2)
        cv2.line(frame, right_start, right_end, (255, 255, 255), line_thickness)
        
        # Bilgi yazısı
        cv2.putText(frame, f"Frame: {i} Curve: {curve:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        out.write(frame)
        
    out.release()
    print("Video oluşturuldu: " + filename)

if __name__ == "__main__":
    generate_video()
