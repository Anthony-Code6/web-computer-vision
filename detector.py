import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from supabase_method import descargar_modelo_desde_supabase

MARGIN = -1
ROW_SIZE = 10
FONT_SIZE = 2
FONT_THICKNESS = 1
rect_color_GREEN = (66, 255, 0)
rect_color_RED = (227, 7, 34)
TEXT_COLOR = (255, 255, 255)

# Descargar el modelo desde Supabase
model_path = descargar_modelo_desde_supabase()

# Configurar MediaPipe
base_options = python.BaseOptions(model_asset_path=model_path) # Define la ubicacion del modelo
options = vision.ObjectDetectorOptions(base_options=base_options, score_threshold=0.5) # Obcion de deteccion - umbral
detector = vision.ObjectDetector.create_from_options(options) # Instacia de detector

# Generador de frames
def generar_frames():

    cap = cv2.VideoCapture(0)

    # Ajuste de resolucion y (frames) para evitar retrasos
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 850)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 630)
    cap.set(cv2.CAP_PROP_FPS, 15)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        detection_result = detector.detect(mp_image)

        for detection in detection_result.detections:
            bbox = detection.bounding_box
            x, y, w, h = int(bbox.origin_x), int(bbox.origin_y), int(bbox.width), int(bbox.height)
            category = detection.categories[0]
            category_name = category.category_name
            probability = round(category.score, 2)
            result_text = f"{category_name} ({probability})"

            color = rect_color_GREEN if category_name == 'SIN_HONGO' else rect_color_RED
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
            cv2.putText(frame, result_text, (x, y - 10), cv2.FONT_HERSHEY_PLAIN,
                        FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

            # Segmentacion del area afectada si hay hongo
            if category_name == 'HONGO':
                roi = frame[y:y + h, x:x + w]
                hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

                # Rango de color tipico del hongo (ajustable)
                lower_hongo = np.array([0, 50, 20])
                upper_hongo = np.array([20, 255, 150])
                mask = cv2.inRange(hsv_roi, lower_hongo, upper_hongo)

                # Calculo de porcentaje de area afectada
                total_pixels = w * h
                affected_pixels = cv2.countNonZero(mask)
                porcentaje_afectado = (affected_pixels / total_pixels) * 100

                # Mostrar porcentaje en pantalla
                porcentaje_text = f"{porcentaje_afectado:.1f}% hongo"
                cv2.putText(frame, porcentaje_text, (x, y + h + 25),
                            cv2.FONT_HERSHEY_PLAIN, FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

                # Dibujar la mascara sobre el area (transparente)
                mask_colored = cv2.merge([mask, mask, mask])
                masked_region = cv2.addWeighted(roi, 1, mask_colored, 0.5, 0)
                frame[y:y + h, x:x + w] = masked_region

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
