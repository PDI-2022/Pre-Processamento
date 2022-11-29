import cv2
import numpy as np
import alinhamento as al

# parametro are_joined sinaliza se as metades das sementes estão juntas na imagem
# valor default eh False
def corte(img, are_joined=False):
    # Alinha a imagem antes do corte
    img = al.alinhar(img)

    # limiarizando os canais de cores
    used_threshold, thresholded_bgr_image = cv2.threshold(img, 130, 255, cv2.THRESH_BINARY)
    bt, gt, rt = cv2.split(thresholded_bgr_image)

    zeros = np.zeros(img.shape[:2], dtype="uint8")

    # vermelho separado limiarizado
    rdt = cv2.merge([zeros, zeros, rt])

    # passando imagem do limiar do vermelho para grayscale e fazendo o limiar
    verm_cinza = cv2.cvtColor(rdt, cv2.COLOR_BGR2GRAY)
    RER, mask = cv2.threshold(verm_cinza, 40, 255, cv2.THRESH_BINARY)

    # aplicando filtro da mediana com janela=5
    median = cv2.medianBlur(mask, 5)

    if are_joined:
        # realizando operação de fechamento para garantir que o contorno das duas
        # metades de uma semente sera unico
        kernel = np.ones((30,10),np.uint8)
        closing = cv2.morphologyEx(median, cv2.MORPH_CLOSE, kernel)

        # achando contornos
        contours, hierarchy = cv2.findContours(closing,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    else:
        # achando contornos
        contours, hierarchy = cv2.findContours(median,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    #calculando os centros de cada contorno
    rect = []

    for c in contours:
        if cv2.contourArea(c) > 3500:
            
            xret,yret,wret,hret = cv2.boundingRect(c) # caracatersticas do retangulo delimitador
            cX = int(xret+wret/2)
            cY = int(yret+hret/2)
            rect.append((xret,yret,wret,hret,cX,cY))

    # ordenando o vetor pelo valor de y do centro do contorno
    rect.sort(key=lambda a: a[5])

    by_line=[]
    cnt=1
    i=0

    # recorte caso as metades da semente estejam juntas
    if are_joined:
        # detectando a quantidade de sementes por linha
        while i<=len(rect)-1:
            if i>0:
                if rect[i][5]>rect[i-1][5]+100:
                    by_line.append(cnt)            
                    cnt=1
                else:
                    cnt+=1
                    if i==len(rect)-1:
                        by_line.append(cnt)  
                    
            i+=1

        j=0
        k=0
        rect_m = [[(0,0,0,0,9999,0) for coluna in range(max(by_line))] for linha in range(len(by_line))]

        # organizando os elementos do vetor em uma matriz
        i=0
        for linha in range(len(by_line)):
            if k==len(by_line):
                break
            else:
                while j<by_line[k]:
                    rect_m[k][j]=rect[i]
                    j+=1
                    i+=1
                j=0
                k+=1

        # ordenando cada linha da matriz pelo x do centro dos contornos
        for i in range(len(by_line)):
            rect_m[i].sort(key=lambda a: a[4])

        sementes = []

        # recortando as sementes
        for coluna in range(max(by_line)):
            for linha in range(len(by_line)-1, -1, -1):
                if rect_m[linha][coluna][0]!=0:
                    sementes.append(img[rect_m[linha][coluna][1]-25:rect_m[linha][coluna][1]+rect_m[linha][coluna][3]+25 , rect_m[linha][coluna][0]-25:rect_m[linha][coluna][0]+rect_m[linha][coluna][2]+25])           

    # recorte caso as metades da semente estejam separadas
    else:
        # detectando a quantidade de sementes por linha
        while i<=len(rect)-1:
            if i>0:
                if rect[i][5]>rect[i-1][5]+41:
                    by_line.append(cnt)
                    i+=cnt            
                    cnt=1
                else:
                    cnt+=1
            i+=1

        j=0
        k=0
        i=0
        rect_m = [[(0,0,0,0,9999,0) for coluna in range(2*max(by_line))] for linha in range(len(by_line))]

        # organizando os elementos do vetor em uma matriz
        for linha in range(len(by_line)):
            if k==len(by_line):
                break
            else:
                while j<2*by_line[k]:
                    rect_m[k][j]=rect[i]
                    j+=1
                    i+=1
                j=0
                k+=1

        # ordenando cada linha da matriz pelo x do centro dos contornos
        for i in range(len(by_line)):
            rect_m[i].sort(key=lambda a: a[4])

        sementes = []

        # recortando as sementes
        for coluna in range(0, 2*max(by_line), 2):
            for linha in range(len(by_line)-1, -1, -1):
                if rect_m[linha][coluna][0]!=0:
                    if rect_m[linha][coluna][5]<rect_m[linha][coluna+1][5]:
                        sementes.append(img[rect_m[linha][coluna][1]-25:rect_m[linha][coluna+1][1]+rect_m[linha][coluna+1][3]+25 , rect_m[linha][coluna][0]-25:rect_m[linha][coluna+1][0]+rect_m[linha][coluna+1][2]+25])
                    else:
                        sementes.append(img[rect_m[linha][coluna+1][1]-25:rect_m[linha][coluna][1]+rect_m[linha][coluna][3]+25 , rect_m[linha][coluna][0]-25:rect_m[linha][coluna+1][0]+rect_m[linha][coluna+1][2]+25])           
    
    return sementes