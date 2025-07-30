import cv2

kamera = cv2.VideoCapture(0)  # 0 varsayılan kamerayı açar

while True:
    ret, frame = kamera.read()
    if not ret:
        break

    cv2.imshow("Kamera", frame)

    # 'q' ya basınca çık
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

kamera.release()
cv2.destroyAllWindows()
