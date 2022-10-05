import cv2
import imutils
import numpy as np
import matplotlib.pyplot as plt

def alinhar(imagem_original):
	"""Funcao que recebe uma imagem de malha com sementes
	e retorna uma imagem com a malha alinhada.
	"""
	
	# Tamanho da imagem
	[x, y, z] = np.shape(imagem_original)

	# Faz a segmentacao com thresholding
	(T, imagem_thresh) = cv2.threshold(imagem_original, 115, 255, cv2.THRESH_BINARY)

	# Deixa a imagem em escala de cinza
	imagem_cinza = cv2.cvtColor(imagem_thresh, cv2.COLOR_BGR2GRAY)

	# Prepara para alinhamento
	# Ponto de busca da borda da malha situado no hemisferio norte da imagem
	ponto_busca1 = [int(x*(1/3)), int(y*(1/10))]

	# Ponto situado no hemisferio sul da imagem
	ponto_busca2 = [int(x*(2/3)), int(y*(1/10))]

	# Move o ponto de busca 1 a direita ate encontrar a borda da malha
	while True:
	    if (imagem_cinza[ponto_busca1[0], ponto_busca1[1]] == 0):
		        # Sai do loop com coordenada x na borda da malha
		        break

	    # Caso pixel nao possua o valor desejado
	    ponto_busca1[1] = ponto_busca1[1] + 1

	# Move o ponto de busca 2 a direita ate encontrar a borda da malha
	while True:
	    if (imagem_cinza[ponto_busca2[0], ponto_busca2[1]] == 0 ):
		        # Sai do loop com coordenada x na borda da malha
		        break

	    # Caso pixel nao possua o valor desejado
	    ponto_busca2[1] = ponto_busca2[1] + 1


	
	# Calculo do angulo de rotacao utilizando trigonometria
	L1 = ponto_busca2[0] - ponto_busca1[0] # Cateto adjacente
	L2 = ponto_busca2[1] - ponto_busca1[1] # Cateto oposto
	angulo = np.arctan(L2/L1)
	angulo = np.rad2deg(angulo)

	# Rotaciona a imagem
	imagem_rot = imutils.rotate(imagem_original, -angulo)
	
	return imagem_rot
