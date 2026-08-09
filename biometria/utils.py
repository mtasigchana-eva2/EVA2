import cv2
import numpy as np
import base64

def base64_a_imagen(base64_string):
    _, datos = base64_string.split(",")
    imagen = base64.b64decode(datos)
    imagen = np.frombuffer(imagen, np.uint8)
    imagen = cv2.imdecode(imagen, cv2.IMREAD_COLOR)
    return imagen

def guardar_imagen(ruta, imagen):
    cv2.imwrite(ruta, imagen)