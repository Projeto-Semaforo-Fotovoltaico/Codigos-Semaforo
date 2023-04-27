import cv2
import tkinter as tk
from PIL import Image, ImageTk
import urllib.request
import numpy as np
import os
from time import sleep
from time import time

urlCamera = r'http://192.168.4.6/CAPTURE'


def conectarRede(networkName):
    os.system(f'''cmd /c "netsh wlan connect name={networkName}"''')


def requisicao(url, timeout):
    try:
        return urllib.request.urlopen(url, timeout=timeout)
    except Exception:
        return False


def zoom(img, zoom_factor=2):
    y_size = img.shape[0]
    x_size = img.shape[1]

    x1 = int(0.5 * x_size * (1 - 1 / zoom_factor))
    x2 = int(x_size - 0.5 * x_size * (1 - 1 / zoom_factor))
    y1 = int(0.5 * y_size * (1 - 1 / zoom_factor))
    y2 = int(y_size - 0.5 * y_size * (1 - 1 / zoom_factor))

    img_cropped = img[y1:y2, x1:x2]
    return cv2.resize(img_cropped, None, fx=zoom_factor, fy=zoom_factor)


def getImage(url):
    try:
        img = urllib.request.urlopen(url, timeout=6)
        img = np.array(bytearray(img.read()), dtype=np.uint8)
    except:
        return None

    return cv2.imdecode(img, -1)


def video_loop(canvas, url):
    img = getImage(url)

    if img is not None:
        img = zoom(img)
        image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)

        canvas.create_image(0, 0, image=image, anchor=tk.NW)
        canvas.image = image

    canvas.after(1, video_loop, canvas, url)


root = tk.Tk()
root.title("Aplicativo de Vídeo Tkinter")
root.geometry("640x480")
root.resizable(0, 0)

# Crie o canvas para exibir o vídeo
canvas = tk.Canvas(root, width=640, height=480, bg="black")
canvas.pack(fill=tk.BOTH, expand=True)

# Chame a função de loop de vídeo
video_loop(canvas, urlCamera)

# Inicie o loop principal do Tkinter
conectarRede('ProjetoSemaforo')
root.mainloop()