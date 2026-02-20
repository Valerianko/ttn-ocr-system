import re
from paddleocr import PaddleOCR


class OCRService:
    def __init__(self):
        self.model = PaddleOCR(use_textline_orientation=True, lang='ru', enable_mkldnn=False)

    def extract(self, img):
        result = self.model.ocr(img)
        if not result or not result[0]: return None, 0, ""

        raw_data = []
        scores = []
        res = result[0]

        iterator = zip(res['rec_texts'], res['rec_scores'], res['dt_polys']) if isinstance(res, dict) else \
            ((line[1][0], line[1][1], line[0]) for line in res)

        for t, s, p in iterator:
            raw_data.append({'x': int(p[0][0]), 'y': int(p[0][1]), 'text': t, 'score': s})
            scores.append(s)

        raw_data.sort(key=lambda x: x['y'])
        lines = []
        if raw_data:
            current_line = [raw_data[0]]
            for i in range(1, len(raw_data)):
                if abs(raw_data[i]['y'] - current_line[-1]['y']) < 15:
                    current_line.append(raw_data[i])
                else:
                    lines.append(current_line)
                    current_line = [raw_data[i]]
            lines.append(current_line)

        trash_keywords = ["белбланкавыд", "гознак", "издательство", "тираж", "заказ №"]
        formatted_text = ""
        for i, line in enumerate(lines):
            line.sort(key=lambda x: x['x'])
            txt = " ".join([item['text'] for item in line])
            if any(k in txt.lower() for k in trash_keywords): continue

            # убираем X, оставляем только текст через |
            line_str = " | ".join([item['text'] for item in line])
            formatted_text += f"ROW_{i:02}: {line_str}\n"

        avg_conf = (sum(scores) / len(scores)) * 100 if scores else 0
        return raw_data, avg_conf, formatted_text