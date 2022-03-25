import cv2              # pip install opencv-contrib-python
import numpy as np      # pip install numpy

endrecoImagem = r'C:\Users\march\OneDrive\Documentos\Imagens Latex\ImagemSemaforo.jpg'
#endrecoImagem = r'C:\Users\march\OneDrive\Documentos\Imagens Latex\melhor.png'
img = cv2.imread(endrecoImagem)
img = cv2.resize(img, (800, 600), interpolation=cv2.INTER_CUBIC)

Hmin = 10
Hmax = 50

def reconhecerCirculos(img):
    gray_blurred = cv2.blur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (3, 3))
    detected = cv2.HoughCircles(gray_blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=50, param1=50, param2=20, minRadius=20, maxRadius=30)

    if detected is not None:
        detected = np.uint16(np.around(detected))

        for lista in detected[0, :]:
            x, y, r = lista[0], lista[1], lista[2]

            # Draw the circumference of the circle.
            cv2.circle(img, (x, y), r, (0, 255, 0), 2)

            # Draw a small circle (of radius 1) to show the center.
            cv2.circle(img, (x, y), 1, (0, 0, 255), 3)

reconhecerCirculos(img)
cv2.imshow('Semaforo', img)
cv2.waitKey(0)