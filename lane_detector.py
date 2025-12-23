import cv2
import numpy as np
import config

def process_frame(frame):
    """
    Görüntüyü işler ve şerit hatasını döndürür.
    """
    height, width = frame.shape[:2]
    roi_height = int(height * config.ROI_HEIGHT_RATIO)
    roi = frame[height-roi_height:height, 0:width]
    
    thresh = None
    
    if config.DETECTION_MODE == 'COLOR':
        # HSV Modu (Sarı ve Beyaz)
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Sarı Maske
        lower_yellow = np.array(config.HSV_LOWER_YELLOW)
        upper_yellow = np.array(config.HSV_UPPER_YELLOW)
        mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
        
        # Beyaz Maske
        lower_white = np.array(config.HSV_LOWER_WHITE)
        upper_white = np.array(config.HSV_UPPER_WHITE)
        mask_white = cv2.inRange(hsv, lower_white, upper_white)
        
        # İkisini birleştir
        thresh = cv2.bitwise_or(mask_yellow, mask_white)
        
    else:
        # Klasik Parlaklık Modu (Brightness)
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, config.LANE_COLOR_THRESHOLD, 255, cv2.THRESH_BINARY)
    
    # Kalan işlemler ortak (Kontur bulma ve hata hesabı)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Hata hesaplama
    if len(contours) > 0:
        # Alanlarına göre sırala
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        centers = []
        for cnt in contours[:2]: # En büyük 2 parça
            if cv2.contourArea(cnt) > 100: # Gürültüyü engelle
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    centers.append(cX)
                    
                    # Çizim (Sarı)
                    cv2.drawContours(roi, [cnt], -1, (0, 255, 255), 2)
                    cv2.circle(roi, (cX, cY), 7, (255, 0, 0), -1)
        
        if len(centers) > 0:
            lane_center = int(sum(centers) / len(centers))
            frame_center = width // 2
            error = lane_center - frame_center
            
            # Görselleştirme
            cv2.line(roi, (frame_center, 0), (frame_center, roi_height), (0, 0, 255), 1) 
            cv2.line(roi, (lane_center, 0), (lane_center, roi_height), (0, 255, 255), 2) 
            
            return frame, error, thresh
            
    return frame, 0, thresh
