import os
import cv2

# Obtener la ruta absoluta de la carpeta 'biometria'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
XML_PATH = os.path.join(BASE_DIR, "haarcascade_frontalface_default.xml")

detector = cv2.CascadeClassifier(XML_PATH)


def preparar(imagen):
    if imagen is None or detector is None or detector.empty():
        return None

    if len(imagen.shape) == 3:
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    else:
        gris = imagen

    rostros = detector.detectMultiScale(
        gris, scaleFactor=1.1, minNeighbors=5, minSize=(120, 120)
    )

    if len(rostros) == 0:
        return None

    x, y, w, h = rostros[0]
    rostro_recortado = gris[y : y + h, x : x + w]
    rostro_procesado = cv2.resize(rostro_recortado, (250, 250))

    return rostro_procesado