import numpy as np
import cv2
import threading
import time
from PIL import Image
from io import BytesIO
import base64
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from app.repositories import supabase_repository as repo

# Constantes visuales
MARGIN = -1
ROW_SIZE = 10
FONT_SIZE = 2
FONT_THICKNESS = 1
rect_color_GREEN = (66, 255, 0)
rect_color_RED = (227, 7, 34)
TEXT_COLOR = (255, 255, 255)

# Modelo MediaPipe
model_path = repo.download_model()
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.ObjectDetectorOptions(base_options=base_options, score_threshold=0.5)
detector = vision.ObjectDetector.create_from_options(options)

def save_task(frame, estado, confianza, tiempo_procesamiento):
    import uuid
    estado_bool = True if estado.upper() == "HONGO" else False
    nombre_imagen = f"{uuid.uuid4()}.jpg"
    url = repo.upload_imagen(frame, nombre_imagen)
    #print('URL DE LA IMAGEN SUBIDA A SUPABASE')
    #print(url)
    repo.detecciones_ins(estado_bool, confianza, url, tiempo_procesamiento)

def analizar_imagen_base64(image_base64):
    image_data = image_base64.split(',')[1]
    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    frame = cv2.flip(frame, 1)

    start_time = time.time()
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    detection_result = detector.detect(mp_image)

    for detection in detection_result.detections:
        bbox = detection.bounding_box
        x, y, w, h = int(bbox.origin_x), int(bbox.origin_y), int(bbox.width), int(bbox.height)
        category = detection.categories[0]
        category_name = category.category_name
        probability = round(category.score, 2)

        status_category_name = category_name if probability > 0.7 else 'SIN_HONGO'
        result_text = f"{category_name} ({probability})"

        color = rect_color_GREEN if status_category_name == 'SIN_HONGO' else rect_color_RED
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
        cv2.putText(frame, result_text, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

        if status_category_name == 'HONGO':
            roi = frame[y:y + h, x:x + w]
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            lower_hongo = np.array([0, 50, 20])
            upper_hongo = np.array([20, 255, 150])
            mask = cv2.inRange(hsv_roi, lower_hongo, upper_hongo)
            total_pixels = w * h
            affected_pixels = cv2.countNonZero(mask)
            porcentaje_afectado = (affected_pixels / total_pixels) * 100
            porcentaje_text = f"{porcentaje_afectado:.1f}% hongo"
            cv2.putText(frame, porcentaje_text, (x, y + h + 25), cv2.FONT_HERSHEY_PLAIN, FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)
            mask_colored = cv2.merge([mask, mask, mask])
            masked_region = cv2.addWeighted(roi, 1, mask_colored, 0.5, 0)
            frame[y:y + h, x:x + w] = masked_region

        tiempo_procesamiento = round(time.time() - start_time, 2)
        threading.Thread(target=save_task, args=(frame.copy(), status_category_name, probability, tiempo_procesamiento)).start()

    _, buffer = cv2.imencode('.jpg', frame)
    img_bytes = buffer.tobytes()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    return f"data:image/jpeg;base64,{img_base64}"
