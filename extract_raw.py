import os

os.environ['FLAGS_enable_onednn'] = '0'
os.environ['FLAGS_enable_pir_api'] = '0'
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

import cv2
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_textline_orientation=True, lang='ru', enable_mkldnn=False)

img_path = 'data/IMG_6983.jpg'


def get_raw_text():
    if not os.path.exists(img_path):
        print(f"Файл не найден: {img_path}")
        return

    print(f"Загрузка изображения...")
    image = cv2.imread(img_path)

    # Ресайз для стабильности
    max_side = 1600
    h, w = image.shape[:2]
    if max(h, w) > max_side:
        scale = max_side / max(h, w)
        image = cv2.resize(image, (int(w * scale), int(h * scale)))

    print(f"Запуск распознавания (PaddleX engine)...")
    result = ocr.ocr(image)

    if not result or len(result) == 0:
        print("Текст не найден.")
        return

    res = result[0]

    raw_lines = []
    confidences = []

    # Проверяем наличие нужных ключей в ответе
    if isinstance(res, dict) and 'rec_texts' in res:
        texts = res['rec_texts']
        scores = res['rec_scores']
        polys = res['dt_polys']

        print(f"Найдено строк: {len(texts)}")

        # Собираем данные, объединяя текст, точность и координаты
        for t, s, p in zip(texts, scores, polys):
            y = int(p[0][1])
            confidences.append(s)
            raw_lines.append(f"Y:{y} | {t} | (conf: {s:.2f})")
    else:
        print("Неожиданный формат результата. Попробуем альтернативный разбор...")
        for line in res:
            if isinstance(line, list) and len(line) > 1:
                y = int(line[0][0][1])
                text = line[1][0]
                conf = line[1][1]
                confidences.append(conf)
                raw_lines.append(f"Y:{y} | {text} | (conf: {conf:.2f})")

    if raw_lines:
        avg_conf = (sum(confidences) / len(confidences)) * 100
        print(f"Средняя уверенность: {avg_conf:.2f}%")

        output_file = "raw_output.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"AVG CONFIDENCE: {avg_conf:.2f}%\n")
            f.write("-" * 30 + "\n")
            for line in sorted(raw_lines, key=lambda x: int(x.split('|')[0].replace('Y:', '').strip())):
                f.write(line + "\n")

        print(f"УСПЕХ! Результат сохранен в {os.path.abspath(output_file)}")
    else:
        print("К сожалению, не удалось извлечь текст.")


if __name__ == "__main__":
    get_raw_text()