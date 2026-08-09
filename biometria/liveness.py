import cv2
import os

cascade_path = os.path.join(
    cv2.data.haarcascades,
    "haarcascade_frontalface_default.xml"
)

detector = cv2.CascadeClassifier(cascade_path)


def detectar_vida(imagen):

    if detector.empty():
        return False, "No se pudo cargar el detector facial."

    if len(imagen.shape) == 3:
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    else:
        gris = imagen

    rostros = detector.detectMultiScale(
        gris,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(100,100)
    )

    if len(rostros)==0:
        return False,"No se detectó ningún rostro."

    if len(rostros)>1:
        return False,"Debe aparecer solamente un rostro."

    return True,"Prueba de vida aprobada."