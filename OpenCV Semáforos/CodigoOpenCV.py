import cv2
import numpy as np


# MOSTRANDO A IMAGEM PELO SEU OBJETO E ESPERANDO
def show(img):
    cv2.imshow('imagem', img)
    cv2.waitKey(0)


# DESENHANDO UM CÍRCULO E UM RETÂNGULO NAS COORDENADAS DO SEMÁFORO DETECTADO
def desenharDetectados(img, detected):
    if not len(detected):
        return

    for circulo in detected:
        x, y, r = int(circulo[0]), int(circulo[1]), int(circulo[2])
        cv2.circle(img, (x, y), r, (0, 255, 0), 2)

    x = [int(x) for x, y, r in detected]
    y = [int(y) for x, y, r in detected]
    r = [int(r) for x, y, r in detected]

    img = cv2.rectangle(img, (min(x) - 2 * max(r), min(y) - 2 * max(r)),
                             (max(x) + 2 * max(r), max(y) + 2 * max(r)),
                             (0, 0, 255), thickness=4)

    return img


# DETECTA APENAS OS CÍRCULOS COM CORES (NO INTERVALO ESPECIFICADO)
def coresSemaforo(img):
    HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # DEFININDO OS LIMITES DE RECONHECIMENTO DE CADA COR
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    lower_green = np.array([40, 50, 50])
    upper_green = np.array([90, 255, 255])
    lower_yellow = np.array([15, 150, 150])
    upper_yellow = np.array([35, 255, 255])

    # DESTACANDO OS TONS DE VERDE (O QUE FOR VERDE É BRANCO 255 E O RESTO É PRETO 0)
    maskg = cv2.inRange(HSV, lower_green, upper_green)

    # DESTACANDO OS TONS DE AMARELO
    masky = cv2.inRange(HSV, lower_yellow, upper_yellow)

    # DESTACANDO OS TONS DE VERMELHO (USANDO DOIS INTERVALOS DESEJADOS)
    mask1 = cv2.inRange(HSV, lower_red1, upper_red1)
    mask2 = cv2.inRange(HSV, lower_red2, upper_red2)
    maskr = cv2.add(mask1, mask2)

    redCircles = cv2.HoughCircles(maskr, cv2.HOUGH_GRADIENT, 1, 80,
                                     param1=50, param2=10, minRadius=0, maxRadius=60)

    greenCircles = cv2.HoughCircles(maskg, cv2.HOUGH_GRADIENT, 1, 60,
                                     param1=50, param2=10, minRadius=0, maxRadius=60)

    yellowCircles = cv2.HoughCircles(masky, cv2.HOUGH_GRADIENT, 1, 30,
                                     param1=50, param2=5, minRadius=0, maxRadius=60)

    listaCirculos = []

    if type(redCircles).__module__ == np.__name__:
        for coordenadas in redCircles[0]:
            listaCirculos.append(['vermelho', coordenadas[0]])

    if type(greenCircles).__module__ == np.__name__:
        for coordenadas in greenCircles:
            listaCirculos.append(['verde', coordenadas[0]])

    if type(yellowCircles).__module__ == np.__name__:
        for coordenadas in yellowCircles:
            listaCirculos.append(['amarelo', coordenadas[0]])

    return listaCirculos


# DETECTA TODOS OS CIRCULOS PRESENTES NA IMAGEM (DENTRO DOS LIMITES ESTABELECIDOS)
def listaCirculos(img):
    gray_blurred = cv2.blur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (3, 3))
    detected = cv2.HoughCircles(gray_blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=minDist,
                                param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)

    if detected is not None:            # SE ALGUM CÍRCULO FOI ENCONTRADO
        detected = np.around(detected)  # CONVERTENDO OS VALORES PARA INTEIRO
        return detected[0, :]

    return []


# OBTENDO APENAS OS 3 CÍRCULOS COMPATÍVEIS COM AS REGRAS DE DETECÇÃO DO SEMÁFORO
def processarCirculos(lista):
    for i in range(0, len(lista)):
        x1, y1, r1 = lista[i][0], lista[i][1], lista[i][2]
        circulo1 = np.array([x1, y1, r1])

        listaCirculos = []
        x = 0
        for j in range(0, len(lista)):
            if i == j:
                continue

            x2, y2, r2 = lista[j][0], lista[j][1], lista[j][2]
            circulo2 = np.array([x2, y2, r2])

            diferencaX = abs(circulo2[0] - circulo1[0])
            diferencaY = abs(circulo2[1] - circulo1[1])

            if minX <= diferencaX <= maxX and minY <= diferencaY <= maxY:
                listaCirculos.append(circulo2)
                x += 1

            if x == 2:
                listaCirculos.append(circulo1)
                return listaCirculos

    return []


# COMPARA O CÍRCULO COLORIDO COM OS 3 DETECTADOS DE UM POSSÍVEL SEMÁFORO
def reconhecerSemaforos(img):
    lista = listaCirculos(img)          # TODOS OS CICRULOS
    lista = processarCirculos(lista)    # APENAS OS 3 CIRCULOS DENTRO DA CONFIANÇA
    listaCores = coresSemaforo(img)     # APENAS CIRCULOS COLORIDOS

    if len(listaCores) and len(lista):
        for cor, posicao in listaCores:
            for circulo in lista:
                distancia = np.array(posicao) - np.array(circulo)
                distancia = np.linalg.norm(distancia)

                # SE O CIRCULO COM COR ESTIVER PERTO DO CIRCULO PROCESSADO DENTRO DOS LIMITES
                if distancia < distanciaMaximaCores:   # É O MESMO CIRCULO ENTÃO, DO SEMÁFORO
                    print(f'SEMÁFORO {cor} DETECTADO!')
                    return lista
    return []


# VARIÁVEIS PARA ESTABELECER UM GRAU DE CONFIANÇA PARA DETECÇÃO DE CÍRCULOS
def variaveisDeteccao():
    global minDist, param1, param2, minRadius, maxRadius
    global minX, maxX, minY, maxY, distanciaMaximaCores

    minDist = 20    # DISTÂNCIA MÍNIMA ENTRE CÍRCULOS
    param1 = 50     # GRADIENTE PARA DETECÇÃO DE BORDA
    param2 = 20     # TOLERÂNCIA PARA CÍRCULOS DETECTADOS
    minRadius = 10  # TAMANHO MÍNIMO DO RAIO DOS CÍRCULOS
    maxRadius = 30  # TAMANHO MÁXIMO DO RAIO DOS CÍRCULOS

    minX, maxX = 0, 10         # LIMITES HORIZONTAIS PARA DISTÂNCIA (VALIDAÇÃO)
    minY, maxY = 10, 200       # LIMITES VERTICAIS PARA DISTÂNCIA (VALIDAÇÃO)
    distanciaMaximaCores = 20  # DISTÂNCIA MÁXIMA PARA CÍCULO DETECTADO E UM CÍCRULO COM CORES


# DIMINUINDO O GRAU DE CONFIANÇA PARA ENCONTRAR MAIS POSSÍVEIS CÍRCULO
def diminuirConfianca():
    global minDist, param1, param2, minRadius, maxRadius
    global minX, maxX, minY, maxY, distanciaMaximaCores

    if minDist > 5:
        minDist -= 5  # DISTÂNCIA MÍNIMA ENTRE CÍRCULOS

    if param2 < 600:
        param2 += 5

    if minRadius > 5:
        minRadius -= 5

    if maxRadius < 1000:
        maxRadius += 5

    if maxX < 100:
        maxX += 5

    if minY > 5:
        minY -= 5

    if maxY < 1000:
        maxY += 5

    if distanciaMaximaCores < 100:
        distanciaMaximaCores += 5


# CÓDIGO PRINCIPAL PARA ATIVAR O RECONHECIMENTO
for c in range(1, 13):
    endereco = r'FotosSemaforo/Semaforo' + str(c) + '.png'
    print()
    print(endereco)

    img = cv2.imread(endereco)
    #img = cv2.resize(img, (800, 600), interpolation=cv2.INTER_CUBIC)

    # RECONHECENDO SEMÁFOROS (INICIALIZANDO VARIÁVEIS DE CONFIABILIDADE DE DETECÇÃO)
    variaveisDeteccao()

    for c in range(0, 50):
        lista = reconhecerSemaforos(img)

        if lista:
            print(lista)
            img = desenharDetectados(img, lista)
            show(img)
            break

        diminuirConfianca()
