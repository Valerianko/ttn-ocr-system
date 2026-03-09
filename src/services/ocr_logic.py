from paddleocr import PaddleOCR


class OCRService:
    def __init__(self):
        self.model = PaddleOCR(use_textline_orientation=True, lang='ru', enable_mkldnn=False)

    def extract(self, img):
        result = self.model.ocr(img)
        if not result or not result[0]: return None, 0, None, "", ""
        raw_data = []
        res = result[0]
        # Собираем данные
        texts = res.get('rec_texts', []) if isinstance(res, dict) else [line[1][0] for line in res]
        scores = res.get('rec_scores', []) if isinstance(res, dict) else [line[1][1] for line in res]
        polys = res.get('dt_polys', []) if isinstance(res, dict) else [line[0] for line in res]

        for t, s, p in zip(texts, scores, polys):
            raw_data.append({'x': int(p[0][0]), 'y': int(p[0][1]), 'text': t, 'score': s})

        # Группировка по строкам (Y)
        raw_data.sort(key=lambda x: x['y'])
        lines = []
        if raw_data:
            curr = [raw_data[0]]
            for i in range(1, len(raw_data)):
                if abs(raw_data[i]['y'] - curr[-1]['y']) < 15:
                    curr.append(raw_data[i])
                else:
                    lines.append(curr);
                    curr = [raw_data[i]]
            lines.append(curr)

        formatted_text = ""
        full_blob = ""
        for i, line in enumerate(lines):
            line.sort(key=lambda x: x['x'])
            txt = "  |  ".join([it['text'] for it in line])
            formatted_text += f"L{i:02}: {txt}\n"
            full_blob += " ".join([it['text'] for it in line]) + " "

        return raw_data, (sum(scores) / len(scores)) * 100, result, formatted_text, full_blob