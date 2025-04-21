import base64
from io import BytesIO
from PIL import Image, ImageDraw
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from supabase_method import descargar_modelo_desde_supabase

# Cargar el modelo desde Supabase
local_model_path = descargar_modelo_desde_supabase()
base_options = python.BaseOptions(model_asset_path=local_model_path)
options = vision.ObjectDetectorOptions(base_options=base_options, score_threshold=0.5)
detector = vision.ObjectDetector.create_from_options(options)

def calcular_tasa_error(detecciones):
    total = len(detecciones)
    if total == 0:
        return 0.0
    errores = sum(1 for d in detecciones if d.categories[0].category_name != "SIN_HONGO")
    return round((errores / total) * 100, 2)

def detectar_en_imagen(image: Image.Image):
    """
    Detecta tangelos y clasifica si tienen hongo o no.
    Devuelve imagen anotada y tasa de error.
    """
    np_image = np.array(image.convert("RGB"))
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np_image)
    result = detector.detect(mp_image)
    tasa_error = calcular_tasa_error(result.detections)

    draw = ImageDraw.Draw(image)

    for detection in result.detections:
        bbox = detection.bounding_box
        label = detection.categories[0].category_name
        score = detection.categories[0].score
        color = "green" if label == "SIN_HONGO" else "red"

        x, y, w, h = bbox.origin_x, bbox.origin_y, bbox.width, bbox.height
        draw.rectangle([(x, y), (x + w, y + h)], outline=color, width=3)
        draw.text((x, y - 10), f"{label} ({score:.2f})", fill=color)

        # Si tiene hongo, estimar porcentaje de �rea afectada por color
        if label == "HONGO":
            # Convertir imagen a formato OpenCV para procesar color
            cv2_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
            roi = cv2_image[int(y):int(y+h), int(x):int(x+w)]

            if roi.size > 0:
                hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                lower_hongo = np.array([0, 50, 20])
                upper_hongo = np.array([20, 255, 150])
                mask = cv2.inRange(hsv_roi, lower_hongo, upper_hongo)

                total_pixels = w * h
                affected_pixels = cv2.countNonZero(mask)
                porcentaje_afectado = (affected_pixels / total_pixels) * 100

                draw.text((x, y + h + 10), f"{porcentaje_afectado:.1f}% hongo", fill=color)

    return image, tasa_error
