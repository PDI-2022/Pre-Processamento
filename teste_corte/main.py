import cv2
import corte_malha as cm

img = cv2.imread("imagem.jpeg")
sementes = cm.cortar_malha(img)
cv2.imwrite("semente1.png", sementes[0])
cv2.imwrite("semente2.png", sementes[4])
cv2.imwrite("semente3.png", sementes[5])
cv2.imwrite("semente4.png", sementes[9])
cv2.imwrite("semente5.png", sementes[15])
cv2.imwrite("semente6.png", sementes[27])
cv2.imwrite("semente7.png", sementes[36])
cv2.imwrite("semente8.png", sementes[41])
cv2.imwrite("semente9.png", sementes[49])

