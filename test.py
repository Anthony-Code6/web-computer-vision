# test.py
import cv2
import time
import numpy as np
import threading
import os
import base64
from PIL import Image
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from app.repositories import detecciones_repository as repo
from app.repositories import clasificaciones_repository as repo_clasificacion
from app.services import storage_service as storage

# Constantes visuales
MARGIN = -1
ROW_SIZE = 10
FONT_SIZE = 2
FONT_THICKNESS = 1
rect_color_GREEN = (66, 255, 0)
rect_color_RED = (227, 7, 34)
TEXT_COLOR = (255, 255, 255)

# Cargar modelo
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app', 'models', 'best.tflite'))
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.ObjectDetectorOptions(base_options=base_options, score_threshold=0.5)
detector = vision.ObjectDetector.create_from_options(options)

def save_task(frame, estado, confianza, tiempo_procesamiento):
    import uuid
    estado_bool = True if estado.upper() == "HONGO" else False
    nombre_imagen = f"{uuid.uuid4()}.jpg"
    url = storage.upload_imagen(frame, nombre_imagen)
    respuesta = repo.detecciones_ins(estado_bool, confianza, url, tiempo_procesamiento)
    if respuesta:
        print(respuesta)
        if float(respuesta['confianza']) > 70:
            comentario = 'Se ha encontrado hongo en el fruto del tangelo' if respuesta['estado'] else 'No se ha encontrado ningún hongo en el fruto del tangelo'
            repo_clasificacion.clasificacion_ins(respuesta['id'], 'Verdadero Positivo', comentario)

def analizar_frame(frame):
    frame = cv2.flip(frame, 1)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    start_time = time.time()
    detection_result = detector.detect(mp_image)

    for detection in detection_result.detections:
        bbox = detection.bounding_box
        x, y, w, h = int(bbox.origin_x), int(bbox.origin_y), int(bbox.width), int(bbox.height)
        category = detection.categories[0]
        category_name = category.category_name
        probability = round(category.score, 2)

        status_category_name = category_name if probability > 0.5 else 'SIN_HONGO'
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

    return frame

def main():

    video = 'xxx.mp4'
    # cap = cv2.VideoCapture(video)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error al abrir la cámara.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * 5)  # Un frame cada 5 segundos

    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            processed_frame = analizar_frame(frame)
            cv2.imshow("Detección de Hongo", processed_frame)

        frame_count += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
