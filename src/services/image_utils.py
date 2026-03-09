import cv2
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont


class ImageProcessor:
    @staticmethod
    def enhance(image):
        return image

    @staticmethod
    def save_debug(image_np, ocr_result, original_path, output_dir="debug"):
        if not ocr_result: return "None"
        os.makedirs(output_dir, exist_ok=True)

        # Конвертируем OpenCV (BGR) в PIL (RGB) для рисования русского текста
        img_pil = Image.fromarray(cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)

        try:
            font = ImageFont.truetype("arial.ttf", 22)
        except:
            font = ImageFont.load_default()

        res = ocr_result[0]
        polys = res.get('dt_polys', []) if isinstance(res, dict) else [line[0] for line in res]
        texts = res.get('rec_texts', []) if isinstance(res, dict) else [line[1][0] for line in res]

        for poly, text in zip(polys, texts):
            flat_poly = [(int(p[0]), int(p[1])) for p in poly]
            draw.polygon(flat_poly, outline="green", width=3)
            draw.text((flat_poly[0][0], flat_poly[0][1] - 25), text, fill="red", font=font)

        out_name = f"debug_{os.path.basename(original_path)}"
        out_path = os.path.join(output_dir, out_name)
        img_pil.save(out_path)
        return out_path