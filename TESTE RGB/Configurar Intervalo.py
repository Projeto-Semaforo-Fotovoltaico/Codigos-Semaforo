import cv2, os
import numpy as np
from random import randint

i = 0
ponto1 = [0, 0]
ponto2 = [0, 0]
pasta = 'Teste'
 

# MOSTRANDO A IMAGEM PELO SEU OBJETO E ESPERANDO
def configurarIntervalo(img):
    def onMouse(event, x, y, flags, params):
        global i, ponto1, ponto2

        if event != cv2.EVENT_LBUTTONDOWN: # CLICOU O MOUSE? (EVENTO)
            return

        elif i == 0:
            ponto1 = [x, y]
            i += 1

            print(f'ponto1 = {[x, y]}')
            cv2.circle(img, (x, y), 5, (0, 255, 255), -1)
            cv2.imshow('image', img)

        elif i == 1:
            ponto2 = [x, y]
            i += 1

            print(f'ponto2 = {[x, y]}')
            cv2.rectangle(img, ponto1, ponto2, (0, 255, 255), thickness=3)
            cv2.imshow('image', img)

    cv2.namedWindow('image')
    cv2.setMouseCallback('image', onMouse)

    cv2.imshow('image', img)
    if cv2.waitKey(0) == 13:
        print()
        cv2.destroyAllWindows()


# CONVERTENDO AS DUAS IMAGENS PARA MESMA DIMENSÃO E MOSTRANDO LADO A LADO
def showImages(img1, img2):
    img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)

    result = cv2.hconcat([img1, img2])
    cv2.imshow("IMAGEM", result)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


# DESENHANDO OS CÍRCULOS EM UMA LISTA DE COORDENADAS
def desenharCirculos(img, detected):
    x, y, r = int(detected[0]), int(detected[1]), int(detected[2])
    img = cv2.circle(img, (x, y), r, (0, 255, 0), 5)

    return img


# RECONHECENDO O CÍRCULO MAIS VERMELHO PRESENTE EM UMA IMAGEM
def reconhecerVermelhos(img):
    HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    x1, y1, z1 = randint(0, 255), randint(0, 255), randint(0, 255)

    low  = np.array([x1, y1, z1])
    high = np.array([x1+10, y1+10, z1+10])

    maskr = cv2.inRange(HSV, low, high)
    redCircles = cv2.HoughCircles(maskr, cv2.HOUGH_GRADIENT, 1, minDist=80,
                                     param1=50, param2=10, minRadius=1, maxRadius=500)
    
    if redCircles is not None:
        redCircle = redCircles[0][0]

        if validarPosicao(redCircle):
            print('DETECTADO: ', f'[{low[0]}, {low[1]}, {low[2]}],', f'[{high[0]}, {high[1]}, {high[2]}]\n')
            return redCircle, maskr

    return None, maskr


# RETORNA VERDADEIRO SE UM NÚMERO ESTÁ EM UM INTERVALO INDEPENDENTE DA ORDEM
def isBetween(n, intervalo):
    return min(intervalo) <= n <= max(intervalo)


# VERIFICANDO SE O SINAL ESTÁ ACIMA DA MENOR ALTURA ACEITA
def validarPosicao(redCircle):
    global ponto1, ponto2

    r = int(redCircle[2])
    x0, y0 = redCircle[0] - r, redCircle[1] - r
    x,  y  = redCircle[0] + r, redCircle[1] + r

    x1, y1 = ponto1[0], ponto1[1]
    x2, y2 = ponto2[0], ponto2[1]

    if isBetween(x0, [x1, x2]) and isBetween(x, [x1, x2]) and isBetween(y0, [y1, y2]) and isBetween(y, [y1, y2]):
        return True

    return False


# EXIBE TODAS AS FOTOS ENCONTRADAS EM UM ENDEREÇO
def fotos(endereco):
    configurarIntervalo(cv2.imread(endereco))
    print('CARREGANDO...   ', end='')

    while True:
        img = cv2.imread(endereco)
        redCircle, maskr = reconhecerVermelhos(img)

        if redCircle is not None:
            img = desenharCirculos(img, redCircle)
            showImages(img, maskr)

            print()
            print('CARREGANDO...   ', end='')


# RETORNA O NOME DE TODOS OS ARQUIVOS ENCONTRADOS EM UMA PASTA
def arquivosDiretorio(endereco=''):
        arquivos = []
        for caminho_diretorio, nome_diretorio, nome_arquivo in os.walk(endereco):
            if caminho_diretorio == endereco: 
                arquivos.extend(nome_arquivo)
                return arquivos


# FUNÇÃO PRINCIPAL DO PROGRAMA PARA QUE A FOTO SEJA SELECIONADA E CONFIGURADA
def main():
    arquivos = arquivosDiretorio(pasta)

    print()
    print('QUAL IMAGEM DESEJA TESTAR: ')

    for c, arquivo in enumerate(arquivos):
        print(f'[{c+1}] {arquivo}')
    choice = int(input('sua opcao: ')) - 1

    print()
    fotos(pasta + rf'\{arquivos[choice]}')


main()
