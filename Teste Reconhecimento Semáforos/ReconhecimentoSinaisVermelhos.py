import cv2, os
import numpy as np


# MOSTRANDO A IMAGEM PELO SEU OBJETO E ESPERANDO
def show(img):
    img = cv2.resize(img, (800, 600), interpolation=cv2.INTER_CUBIC)
    cv2.imshow('imagem', img)
    cv2.waitKey(0)


# DESENHANDO OS CÍRCULOS EM UMA LISTA DE COORDENADAS
def desenharCirculos(img, detected):
    if not len(detected):
        return

    x, y, r = int(detected[0]), int(detected[1]), int(detected[2])

    img = cv2.circle(img, (x, y), r, (0, 255, 0), 2)

    img = cv2.rectangle(img, (x - 3 * r, y - 3 * r),
                             (x + 3 * r, y + 3 * r),
                             (0, 0, 255), thickness=4)
    return img


def validar(img, redCircles):
    profundidadeLimite = int(img.shape[0]/2) # METADE DA FIGURA

    largura = img.shape[1]
    #cv2.line(img, (0, profundidadeLimite), (largura, profundidadeLimite), (0, 255, 255), thickness=3)

    if type(redCircles).__module__ == np.__name__:
        for coordenadas in redCircles[0]:
            #if coordenadas[1] <= profundidadeLimite:
            return coordenadas
    return []


# RECONHECENDO O CÍRCULO MAIS VERMELHOS PRESENTE EM UMA IMAGEM
def reconhecerVermelhos(img):
    HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    low = np.array([170, 150, 100])
    high = np.array([180, 220, 190])
    maskr = cv2.inRange(HSV, low, high)

    redCircles = cv2.HoughCircles(maskr, cv2.HOUGH_GRADIENT, 1, minDist=80,
                                     param1=50, param2=10, minRadius=5, maxRadius=300)

    lista = validar(img, redCircles)
    #show(maskr)

    if len(lista):
        return lista

    return []


def allFiles(endereco):
    arquivos = []
    for caminhoDiretorio, nomeDiretorio, nomeArquivo in os.walk(endereco):
        if caminhoDiretorio == endereco:  # OBTENHA OS ARQUIVOS QUE ESTÃO NESSA PASTA
            arquivos.extend(nomeArquivo)

    for c, file in enumerate(arquivos):
        arquivos[c] = endereco + fr'\{arquivos[c]}'

    return arquivos


def fotos(endereco):
    imagens = allFiles(endereco)

    for endereco in imagens:
        img = cv2.imread(endereco)

        print(endereco)
        vermelhos = reconhecerVermelhos(img)

        if len(vermelhos):
            img = desenharCirculos(img, vermelhos)

        show(img)
        print()


def video(endereco):
    cap = cv2.VideoCapture(endereco)

    if cap.isOpened()== False:
      print("Error opening video  file")

    while cap.isOpened():
        ret, frame = cap.read()
        if ret == True:
            frame = cv2.resize(frame, (800, 600), interpolation=cv2.INTER_CUBIC)

            vermelhos = reconhecerVermelhos(frame)

            if len(vermelhos):
                img = desenharCirculos(frame, vermelhos)

            cv2.imshow('Frame', frame)

            if cv2.waitKey(25) & 0xFF == ord('q'):
              break

        else:
            break

    cap.release()

    # Closes all the frames
    cv2.destroyAllWindows()


#fotos('FotosSemaforo')
#fotos('Teste')
video('Video.mp4')