import re
from paddleocr import PaddleOCR

class OCRService:
    def __init__(self):
        self.model = PaddleOCR(use_textline_orientation=True, lang='ru', enable_mkldnn=False)

    def extract(self, img):
        result = self.model.ocr(img)
        if not result or not result[0]: return None, 0, None, ""

        raw_data = []
        scores = []
        res = result[0]

        if isinstance(res, dict):
            iterator = zip(res['rec_texts'], res['rec_scores'], res['dt_polys'])
        else:
            iterator = ((line[1][0], line[1][1], line[0]) for line in res)

        for t, s, p in iterator:
            raw_data.append({'x': int(p[0][0]), 'y': int(p[0][1]), 'text': t, 'score': s})
            scores.append(s)

        # Сортировка и группировка в виртуальные строки
        raw_data.sort(key=lambda x: x['y'])
        rows = []
        if raw_data:
            current_row = [raw_data[0]]
            for i in range(1, len(raw_data)):
                if abs(raw_data[i]['y'] - current_row[-1]['y']) < 15:
                    current_row.append(raw_data[i])
                else:
                    rows.append(current_row)
                    current_row = [raw_data[i]]
            rows.append(current_row)

        # Формируем текст для ИИ: каждая строка ROW_XX
        formatted_text = ""
        for i, row in enumerate(rows):
            row.sort(key=lambda x: x['x'])
            line_str = " | ".join([f"X:{item['x']:04} {item['text']}" for item in row])
            formatted_text += f"L{i:02} | {line_str}\n"

        avg_conf = (sum(scores) / len(scores)) * 100 if scores else 0
        return raw_data, avg_conf, result, formatted_text