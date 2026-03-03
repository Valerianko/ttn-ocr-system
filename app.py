import os

os.environ['FLAGS_enable_onednn'] = '0'
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

import logging

logging.getLogger("ppocr").setLevel(logging.ERROR)

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from src.core.pipeline import TTNProcessingPipeline
from src.services.image_utils import ImageProcessor
from src.services.ocr_logic import OCRService
from src.services.llm_logic import LLMService

load_dotenv()
console = Console()


def main():
    pipeline = TTNProcessingPipeline(
        image_proc=ImageProcessor(),
        ocr_service=OCRService(),
        llm_service=LLMService(os.getenv("GROQ_API_KEY"))
    )

    console.clear()
    console.print(Panel("[bold green]TTN OCR [/bold green]"))

    while True:
        path = input("\nВведите путь (или 'q') > ").strip()
        if path.lower() == 'q': break
        if os.path.exists(path):
            try:
                doc, _ = pipeline.process(path)
                console.print(doc.model_dump_json(indent=4))
            except Exception as e:
                console.print(f"[red]Ошибка: {e}[/red]")
        else:
            console.print("[red]Файл не найден[/red]")


if __name__ == "__main__":
    main()