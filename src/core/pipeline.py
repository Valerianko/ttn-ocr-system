import os
import json
import cv2
from rich.console import Console
from src.domain.postprocess import DataNormalizer

console = Console()


class TTNProcessingPipeline:
    def __init__(self, image_proc, ocr_service, llm_service):
        self.image_proc = image_proc
        self.ocr = ocr_service
        self.llm = llm_service

    def process(self, img_path: str):
        console.print(f"[blue]Шаг 1: Подготовка изображения {os.path.basename(img_path)}...[/blue]")
        img = cv2.imread(img_path)
        if img is None:
            raise FileNotFoundError(f"Файл не найден: {img_path}")
        img = self._prepare_image(img)

        console.print("[yellow]Шаг 2: Распознавание текста (PaddleOCR)...[/yellow]")
        raw_data, conf, full_ocr_res, clustered_text = self.ocr.extract(img)

        debug_file = self.image_proc.save_debug(img_path, full_ocr_res)
        console.print(f"[green]Текст извлечен (Точность: {conf:.2f}%). Дебаг: {debug_file}[/green]")

        console.print("[cyan]Шаг 3: Интеллектуальный анализ (LangChain)...[/cyan]")
        document = self.llm.analyze(clustered_text)

        doc = self._finalize(document)
        self._save_to_file(img_path, doc)

        return doc, conf

    def _prepare_image(self, img):
        h, w = img.shape[:2]
        if max(h, w) > 2000:
            scale = 2000 / max(h, w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_LANCZOS4)
        return self.image_proc.enhance(img)

    def _finalize(self, doc):
        # 1. Дату нормализуем всегда
        doc.date = DataNormalizer.normalize_date(doc.date or "")

        if doc.shipper_unp: doc.shipper_unp = DataNormalizer.fix_ocr_numbers(doc.shipper_unp)
        if doc.consignee_unp: doc.consignee_unp = DataNormalizer.fix_ocr_numbers(doc.consignee_unp)
        if doc.number: doc.number = DataNormalizer.fix_ocr_numbers(doc.number)

        return doc

    def _save_to_file(self, img_path, doc):
        out_file = f"result_{os.path.basename(img_path)}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(doc.model_dump(), f, indent=4, ensure_ascii=False)