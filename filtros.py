import matplotlib.pyplot as plt
import cv2
import numpy as np


# Recebe uma imagem em tons de cinza e realiza a equalização de seu histograma
def equalizacao_hist(img):
    return cv2.equalizeHist(img)


# Recebe uma imagem em tons de cinza e a ordem da máscara a ser utilizada no filtro da média (3, 5 ou 7)
def filtro_media(img, ordem_mat):
    validos = [3, 5, 7]
    if ordem_mat in validos:
        return cv2.blur(img, (ordem_mat, ordem_mat))


# Recebe uma imagem em tons de cinza e a ordem da máscara a ser utilizada no filtro da mediana (3, 5 ou 7)
def filtro_mediana(img, ordem_mat):
    validos = [3, 5, 7]
    if ordem_mat in validos:
        return cv2.medianBlur(img, (ordem_mat, ordem_mat))


# Recebe uma imagem em tons de cinza e o valor de limiar
def limiar(img, limiar):
    return cv2.threshold(img, limiar, 255, cv2.THRESH_BINARY)


# Recebe uma imagem em tons de cinza e o raio da máscara a ser aplicada no domínio da frequência
def passa_baixas(img, r):
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)

    mask = np.zeros_like(img)

    cy = mask.shape[0] // 2
    cx = mask.shape[1] // 2
    cv2.circle(mask, (cx, cy), r, (255, 255, 255), -1)[0]

    dft_shift_masked = np.multiply(fshift, mask) / 255
    back_ishift_masked = np.fft.ifftshift(dft_shift_masked)
    img_filtered = np.fft.ifft2(back_ishift_masked)
    return np.abs(img_filtered).clip(0, 255).astype(np.uint8)


# Recebe uma imagem em tons de cinza e o raio da máscara a ser aplicada no domínio da frequência
def passa_altas(img, r):
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)

    mask = np.zeros_like(img)

    cy = mask.shape[0] // 2
    cx = mask.shape[1] // 2
    cv2.circle(mask, (cx, cy), r, (255, 255, 255), -1)[0]

    dft_shift_masked = np.multiply(fshift, 255 - mask) / 255
    back_ishift_masked = np.fft.ifftshift(dft_shift_masked)
    img_filtered = np.fft.ifft2(back_ishift_masked)
    return np.abs(img_filtered).clip(0, 255).astype(np.uint8)


# Recebe uma imagem em tons de cinza e o raio da máscara a ser aplicada no domínio da frequência
def rejeita_banda(img, r):
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)

    mask = np.zeros_like(img)

    cy = mask.shape[0] // 2
    cx = mask.shape[1] // 2
    cv2.circle(mask, (cx, cy), r, (255, 255, 255), 5)[0]

    dft_shift_masked = np.multiply(fshift, 255 - mask) / 255
    back_ishift_masked = np.fft.ifftshift(dft_shift_masked)
    img_filtered = np.fft.ifft2(back_ishift_masked)
    return np.abs(img_filtered).clip(0, 255).astype(np.uint8)
