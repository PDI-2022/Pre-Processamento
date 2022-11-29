import cv2
import numpy as np
import imutils

def reject_outliers(data, m=2.):
    """ Utilizado para remover outliers da amostra
        de angulos de desalinhamento encontrados
    """
    
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    return data[s < m]

def alinhar(img):
    """ Alinha a imagem para que posteriormente
        seja feito corte das sementes.
        Retorna a imagem alinhada.
    """
    # Limiariza os canais de cores
    used_threshold, thresholded_bgr_image = cv2.threshold(img, 130, 255, cv2.THRESH_BINARY)
    bt, gt, rt = cv2.split(thresholded_bgr_image)

    zeros = np.zeros(img.shape[:2], dtype="uint8")

    # Vermelho separado limiarizado
    rdt = cv2.merge([zeros, zeros, rt])

    # Passa imagem do limiar do vermelho para grayscale e fazendo o limiar
    verm_cinza = cv2.cvtColor(rdt, cv2.COLOR_BGR2GRAY)
    RER, mask = cv2.threshold(verm_cinza, 40, 255, cv2.THRESH_BINARY)

    # Aplica filtro da mediana com janela=5
    median = cv2.medianBlur(mask, 5)

    # Acha contornos
    contours, hierarchy = cv2.findContours(median, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Calcula os centros de cada contorno
    rect = []

    for c in contours:
        if cv2.contourArea(c) > 2000:
            xret, yret, wret, hret = cv2.boundingRect(c) # caracatersticas do retangulo delimitador
            cX = int(xret + wret/2)
            cY = int(yret + hret/2)
            rect.append((xret, yret, wret, hret, cX, cY))

    # Ordena o vetor pelo valor de y do centro do contorno
    rect.sort(key=lambda a: a[5])

    by_line = []
    cnt = 1
    i = 0

    # Detecta a quantidade de sementes por linha
    while i <= len(rect) - 1:
        if i > 0:
            if rect[i][5] > rect[i - 1][5] + 41:
                by_line.append(cnt)
                i += cnt            
                cnt = 1
            else:
                cnt += 1
        i += 1

    # Ordena o vetor pelo valor de x do centro do contorno
    rect.sort(key=lambda a: a[4])

    by_column = []
    cnt = 1
    i = 0

    # Detecta a quantidade de sementes por coluna
    while i <= len(rect) - 1:
        if rect[i][4] > rect[i - 1][4] + 40:
            by_column.append(int(cnt/2))          
            cnt = 1
        else:
            cnt += 1
        if i == len(rect) - 1:
            by_column.append(int(cnt/2))
        i += 1

    j = 0
    k = 0
    i = 0
    rect_m = [[(0, 0, 0, 0, 9999, 0) for coluna in range(2 * max(by_line))] for linha in range(len(by_line))]

    # Organiza os elementos do vetor em uma matriz
    for linha in range(len(by_line)):
        if k == len(by_line):
            break
        else:
            while j < 2 * by_line[k]:
                rect_m[k][j] = rect[i]
                j += 1
                i += 1
            j = 0
            k += 1
    
    # Ordena cada linha da matriz pelo x do centro dos contornos
    for i in range(len(by_line)):
        rect_m[i].sort(key=lambda a: a[4])

    # Procura as colunas com quantidade de sementes maior que 1
    colunas = []
    for i in range(len(by_column)):
        if by_column[i] > 1:
            colunas.append(i)
            
    # Procura as linhas com quantidade de sementes maior que 1
    linhas = []
    for i in range(len(by_line)):
        if by_line[i] > 1:
            linhas.append(i)
          
            
    # Calculo do angulo de rotacao utilizando trigonometria
    angulos = []
    
    # Compara o alinhamento entre 2 sementes da mesma coluna
    for i in colunas:
        for j in range(by_column[i]):
            l1 = abs(rect_m[i][j][5] - rect_m[i][0][5])   # Cateto adjacente
            l2 = abs(rect_m[i][0][4] - rect_m[i][j][4])   # Cateto oposto
            try:
                angulo = np.arctan(l2/l1)
            except(ZeroDivisionError):
                angulo = 0
            finally:
                # Correcao do sentido do angulo de alinhamento
                if rect_m[i][j][5] < rect_m[i][0][5]:
                    angulo = -angulo
                angulos.append(int(np.rad2deg(2 * angulo)))
    
    # Compara o alinhamento entre 2 sementes da mesma linha
    for i in colunas:
        for j in range(by_column[i]):
            for k in colunas:
                # Sementes de uma mesma coluna nao devem ser comparadas
                if k == i:
                    continue
                for l in range(by_column[k]):
                    # Caso diferenca entre os valores de x das sementes indique pertinencia a mesma linha
                    if abs(rect_m[k][l][4] - rect_m[i][j][4]) < 70:
                         l1 = abs(rect_m[i][j][5] - rect_m[i][0][5])   # Cateto adjacente
                         l2 = abs(rect_m[i][0][4] - rect_m[i][j][4])   # Cateto oposto
                         try:
                             angulo = np.arctan(l2/l1)
                         except(ZeroDivisionError):
                             angulo = 0
                         finally:
                             if rect_m[i][0][4] < rect_m[i][j][4]:
                                 angulo = -angulo
                             angulos.append(int(np.rad2deg(2 * angulo)))
                
    # Calcula o angulo de alinhamento medio da amostra
    angulos = np.asarray(angulos)
    angulos = reject_outliers(angulos)
    angulo = np.average(angulos)
    
    # Rotaciona a imagem
    rot_img = imutils.rotate(img, angulo/2)

    return rot_img
