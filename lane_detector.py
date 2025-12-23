import cv2
import numpy as np
import config

def process_frame(frame):
    """
    Görüntüyü işler ve şerit hatasını döndürür.
    Return:
        processed_frame: İşlenmiş, çizim yapılmış görüntü
        error: Hata değeri (-100 ile +100 arası, 0 merkez)
    """
    height, width = frame.shape[:2]
    
    # 1. ROI (Region of Interest) - Sadece yolun alt kısmına bak
    roi_height = int(height * config.ROI_HEIGHT_RATIO)
    roi = frame[height-roi_height:height, 0:width]
    
    # 2. Grayscale & Threshold
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Beyaz renkleri ayıkla (Siyah zemin üzerinde beyaz şerit)
    # Threshold değeri config'den gelebilir
    _, thresh = cv2.threshold(gray, config.LANE_COLOR_THRESHOLD, 255, cv2.THRESH_BINARY)
    
    # 3. Kontur Bulma
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Hata hesaplama
    # Amacımız şeritlerin ortasını bulmak.
    # En büyük iki konturu bulmaya çalışalım (Sol ve sağ şerit)
    
    if len(contours) > 0:
        # Alanlarına göre sırala (Büyükten küçüğe)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        # En anlamlı konturların merkezlerini bul
        centers = []
        for cnt in contours[:2]: # En büyük 2 şerit parçası
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                # ROI koordinatlarını gerçek koordinatlara çevir
                # (cY + height - roi_height)
                
                centers.append(cX)
                
                # Çizim (Debug)
                cv2.drawContours(roi, [cnt], -1, (0, 255, 0), 2)
                cv2.circle(roi, (cX, cY), 7, (255, 0, 0), -1)
        
        if len(centers) > 0:
            # Şeritlerin ortalamasını al (Eğer tek şerit varsa ona kilitlenir, riskli ama başlangıç için ok)
            lane_center = int(sum(centers) / len(centers))
            frame_center = width // 2
            
            # Hata: Frame merkezi ile şerit merkezi farkı
            error = lane_center - frame_center
            
            # Görselleştirme
            cv2.line(roi, (frame_center, 0), (frame_center, roi_height), (0, 0, 255), 1) # Araba merkezi
            cv2.line(roi, (lane_center, 0), (lane_center, roi_height), (0, 255, 255), 2) # Hedef
            
            return frame, error, thresh
            
    return frame, 0, thresh
