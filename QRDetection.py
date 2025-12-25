import cv2
import numpy as np
from pyzbar.pyzbar import decode

# 1. Kamera Ayarları
kamera = cv2.VideoCapture(0)

ret, frame = kamera.read()
if not ret:
    print("Kamera açılamadı!")
    exit()

h, w, _ = frame.shape

# 2. Kamera Matrisi (Camera Matrix) Oluşturma
focal_length = w 
center_x = w / 2
center_y = h / 2

camera_matrix = np.array([
    [focal_length, 0, center_x], # x konumunu etkilememsi için y=0
    [0, focal_length, center_y], # Y konumunu etkilememesi için x=0
    [0, 0, 1]
], dtype=np.float32)

# Lens bozulma katsayıları (Distortion coeffs) - 0 varsayıyoruz
dist_coeffs = np.zeros((4, 1))

# 3. 3D QR Kod Modeli Tanımlama
qr_size = 10.0  
object_points = np.array([
    [0, 0, 0],          # Sol Üst
    [0, -qr_size, 0],   # Sol Alt
    [qr_size, -qr_size, 0], # Sağ Alt
    [qr_size, 0, 0]     # Sağ Üst
], dtype=np.float32)

# Eksen Çubukları Modeli (Merkezden X, Y, Z yönüne çizgiler)
axis_points = np.array([
    [0, 0, 0],          # Merkez
    [qr_size, 0, 0],    # X Ekseni ucu
    [0, -qr_size, 0],   # Y Ekseni ucu
    [0, 0, -qr_size]    # Z Ekseni ucu (Bize doğru gelmesi için -Z)
], dtype=np.float32)

print("Kamera başlatıldı. Çıkmak için 'q' tuşuna bas.")

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('qr_video_kaydi.avi', fourcc, 20.0, (w, h))

while True:
    # 4. Görüntü Okuma
    success, frame = kamera.read()
    if not success:
        break

    # 5. QR Kod Tespiti
    decoded_objects = decode(frame)

    for obj in decoded_objects:
        # A) Veriyi ekrana yaz
        qr_data = obj.data.decode('utf-8')
        print(f"QR Verisi: {qr_data}")

        # B) 2D Görüntü Noktalarını Al (Image Points)
        points = obj.polygon
        
        # Eğer 4 köşe tam algılanmadıysa atla (bazen pyzbar 4'ten fazla nokta dönebilir)
        if len(points) == 4:
            image_points = np.array([point for point in points], dtype=np.float32)

            # C) Bounding Box Çizimi
            pts = image_points.astype(np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], True, (0, 255, 0), 3)

            # D) POSE ESTIMATION 
            # Bize Rotation (dönüş) ve Translation (konum) vektörlerini verir.
            success, rvec, tvec = cv2.solvePnP(object_points, image_points, camera_matrix, dist_coeffs)

            if success:
                # E) Eksenleri Ekrana İzdüşürme (Project Points)
                img_axis_points, _ = cv2.projectPoints(axis_points, rvec, tvec, camera_matrix, dist_coeffs)
                
                p = img_axis_points.astype(int)

                # Merkez Noktası
                center = tuple(p[0].ravel())
                
                # X Ekseni (Kırmızı)
                cv2.line(frame, center, tuple(p[1].ravel()), (0, 0, 255), 5)
                # Y Ekseni (Yeşil)
                cv2.line(frame, center, tuple(p[2].ravel()), (0, 255, 0), 5)
                # Z Ekseni (Mavi)
                cv2.line(frame, center, tuple(p[3].ravel()), (255, 0, 0), 5)

                # Metin Yazdırma
                cv2.putText(frame, qr_data, (int(image_points[0][0]), int(image_points[0][1]) - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # 6. Görüntüyü Göster
    cv2.imshow('QR Code & Pose Estimation', frame)
    out.write(frame)

    # 'q' tuşuna basınca çık
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Temizlik
kamera.release()
out.release()
cv2.destroyAllWindows()