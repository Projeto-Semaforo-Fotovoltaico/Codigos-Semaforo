import numpy as np
import matplotlib.pyplot as plt
import random, cv2
from time import sleep, time


HSV = cv2.imread(r'C:\Users\march\Downloads\Foto_Jader.png')

tempo = time()
dadosRGB = [
    [[174, 132, 245], [184, 142, 255]],
    [[171, 145, 254], [181, 155, 264]],
    [[175, 169, 245], [185, 179, 255]],
    [[168, 172, 253], [178, 182, 263]],
    [[172, 189, 251], [182, 199, 261]],
    [[170, 158, 255], [180, 168, 265]],
    [[165, 139, 74], [175, 149, 84]],
    [[174, 171, 247], [184, 181, 257]],
    [[172, 207, 128], [182, 217, 138]],
    [[170, 210, 128], [180, 220, 138]],
    [[169, 212, 81], [179, 222, 91]],
    [[170, 214, 249], [180, 224, 259]],
    [[175, 233, 198], [185, 243, 208]],
    [[175, 236, 179], [185, 246, 189]]
]
dadosMask = list(range(len(dadosRGB)))


for c in range(len(dadosRGB)):
    low  = np.array(dadosRGB[c][0])
    high = np.array(dadosRGB[c][1])
    dadosMask[c] = cv2.inRange(HSV, low, high)

mask1 = 0
for c in range(len(dadosRGB)):
    mask1 = cv2.add(mask1, dadosMask[c])

mask2 = dadosMask[0]
for c in range(1, len(dadosRGB)):
    mask2 = cv2.add(mask2, dadosMask[c])


print(mask1[mask1 == 255])

