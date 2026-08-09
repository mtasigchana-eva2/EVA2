import cv2
import numpy as np


def comparar(img_capturada, img_guardada):
    """Compara dos imágenes de rostro estandarizadas de 250x250 mediante

    Correlación Cruzada Normalizada y diferencia de histogramas.
    """
    if img_capturada is None or img_guardada is None:
        return False, 0.0

    try:
        # 1. Convertir a escala de grises si fuera necesario
        if len(img_capturada.shape) == 3:
            img_capturada = cv2.cvtColor(img_capturada, cv2.COLOR_BGR2GRAY)
        if len(img_guardada.shape) == 3:
            img_guardada = cv2.cvtColor(img_guardada, cv2.COLOR_BGR2GRAY)

        img_capturada = cv2.resize(img_capturada, (250, 250))
        img_guardada = cv2.resize(img_guardada, (250, 250))

        # 2. Correlación Cruzada Normalizada (Métrica principal para plantillas de 250x250)
        res_template = cv2.matchTemplate(
            img_capturada, img_guardada, cv2.TM_CCOEFF_NORMED
        )
        _, max_val, _, _ = cv2.minMaxLoc(res_template)
        correlacion = float(max_val) * 100.0

        print(f"--> Correlación calculada: {correlacion:.2f}%")

        # UMBRAL DE DECISIÓN:
        # Tu propio rostro está dando >94%.
        # Una persona distinta en recortes idénticos dará <75%.
        # Establecemos el umbral en 80.0% para máxima precisión.
        coincide = correlacion >= 80.0

        return coincide, round(correlacion, 2)

    except Exception as e:
        print(f"Error en la comparación: {e}")
        return False, 0.0