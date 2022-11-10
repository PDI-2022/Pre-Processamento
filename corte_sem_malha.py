import cv2
import numpy as np


def corte_sem_malha(img):
    # retorna um vetor com 50 sementes recortadas individualmente

    # limiarizando os canais de cores
    used_threshold, thresholded_bgr_image = cv2.threshold(img, 130, 255, cv2.THRESH_BINARY)
    bt, gt, rt = cv2.split(thresholded_bgr_image)

    zeros = np.zeros(img.shape[:2], dtype="uint8")

    # limiarização do canal vermelho
    rdt = cv2.merge([zeros, zeros, rt])

    # cria a mascara para separar as sementes do fundo
    verm_cinza = cv2.cvtColor(rdt, cv2.COLOR_BGR2GRAY)
    RER, mask = cv2.threshold(verm_cinza, 40, 255, cv2.THRESH_BINARY)

    # aplicando filtro da mediana com janela=5
    median = cv2.medianBlur(mask, 5)

    # achando contornos
    contours, hierarchy = cv2.findContours(median,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    # criando vetor para armazenar as caracteeristicas do bounding rectangle
    rect = []

    # calculando as características dos retangulos de cada contorno
    for c in contours:
        if cv2.contourArea(c) > 2000: # criterio de seleção de contornos por area
            
            xret,yret,wret,hret = cv2.boundingRect(c) 
            cX = int(xret+wret/2) # x do centro do contorno
            cY = int(yret+hret/2) # x do centro do contorno
            rect.append((xret,yret,wret,hret,cX,cY))

    # ordenando os contornos por y
    rect.sort(key=lambda y: y[1]) 
    
    rect_m = [[0 for i in range(10)] for j in range(10)] 

    j=0
    k=0

    # organizando todos os contornos por linha
    for i in range(100):
        if i<10+j:
            rect_m[k][i-j]=rect[i]
        else:
            j+=10   
            k+=1
            rect_m[k][i-j]=rect[i]

    # ordenando as linhas por x
    # agora as sementes estão em posições correspondentes na matriz e na imagem
    for i in range(10):
        rect_m[i].sort(key=lambda x: x[0])

    # vetor que recebe as sementes recortadas
    sementes = []

    # checando a posição relativa das duas metades da semente para fazer o corte
    for coluna in range(0, 10, 2):
        for linha in range(9, -1, -1):
            if rect_m[linha][coluna][5]<rect_m[linha][coluna+1][5]:
                sementes.append(img[rect_m[linha][coluna][1]-25:rect_m[linha][coluna+1][1]+rect_m[linha][coluna+1][3]+25 , rect_m[linha][coluna][0]-25:rect_m[linha][coluna+1][0]+rect_m[linha][coluna+1][2]+25])
            else:
                sementes.append(img[rect_m[linha][coluna+1][1]-25:rect_m[linha][coluna][1]+rect_m[linha][coluna][3]+25 , rect_m[linha][coluna][0]-25:rect_m[linha][coluna+1][0]+rect_m[linha][coluna+1][2]+25])
    
    return sementes