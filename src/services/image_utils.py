import cv2
import os
import numpy as np

class ImageProcessor:
    @staticmethod
    def enhance(image):
        return image

    @staticmethod
    def save_debug(img_path, ocr_result, output_dir="debug"):
        if not ocr_result: return "None"
        os.makedirs(output_dir, exist_ok=True)
        img = cv2.imread(img_path)
        if img is None: return "Error"

        res = ocr_result[0]
        polys = res.get('dt_polys', []) if isinstance(res, dict) else [line[0] for line in res]
        texts = res.get('rec_texts', []) if isinstance(res, dict) else [line[1][0] for line in res]

        for poly, text in zip(polys, texts):
            pts = np.array(poly, np.int32).reshape((-1, 1, 2))
            cv2.polylines(img, [pts], True, (0, 255, 0), 2)
            cv2.putText(img, text[:15], (int(poly[0][0]), int(poly[0][1]-5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        out_path = os.path.join(output_dir, f"debug_{os.path.basename(img_path)}")
        cv2.imwrite(out_path, img)
        return out_path