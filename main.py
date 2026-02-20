import os
import json
import cv2
import logging
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

# Системные настройки
os.environ['FLAGS_enable_onednn'] = '0'
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
logging.getLogger("ppocr").setLevel(logging.ERROR)

from src.image_utils import ImageProcessor
from src.ocr_logic import OCRService
from src.llm_logic import LLMService

load_dotenv()
console = Console()


class TTNApp:
    def __init__(self):
        self.ocr = OCRService()
        self.llm = LLMService(os.getenv("GROQ_API_KEY"))
        self.img_proc = ImageProcessor()

    def run(self, img_path):
        console.print(f"\n[bold blue]Запущена обработка {os.path.basename(img_path)}, пожалуйста, подождите ...[/bold blue]")

        with console.status("[bold yellow]Интеллектуальный анализ...", spinner="dots"):
            img = cv2.imread(img_path)
            if img is None: return

            # Стабильные 2000px
            h, w = img.shape[:2]
            if max(h, w) > 2000:
                scale = 2000 / max(h, w)
                img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

            enhanced = self.img_proc.enhance(img)
            data, conf, _ = self.ocr.extract(enhanced)
            if not data: return

            # Сортировка для ИИ
            data.sort(key=lambda r: (r['y'], r['x']))
            text_for_ai = "\n".join([f"X:{d['x']:04} | {d['text']}" for d in data])

            result_json = self.llm.analyze(text_for_ai)

            # Сохранение
            output_file = f"result_{os.path.basename(img_path)}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result_json, f, indent=4, ensure_ascii=False)

            console.print(f"\n[bold green]Успешно. Точность OCR: {conf:.2f}%[/bold green]")

            json_str = json.dumps(result_json, indent=4, ensure_ascii=False)
            syntax = Syntax(json_str, "json", theme="monokai", word_wrap=True)
            console.print(Panel(syntax, title=f"JSON: {os.path.basename(img_path)}", expand=False))


if __name__ == "__main__":
    app = TTNApp()
    console.clear()
    console.print(Panel("[bold blue]TTN OCR SYSTEM[/bold blue]", expand=False))
    while True:
        path = input("\nВведите путь к файлу (или 'q' для выхода) > ").strip()
        if path.lower() == 'q': break
        if os.path.exists(path):
            app.run(path)
        else:
            console.print(f"[red]Файл не найден: {path}[/red]")