import os
import json
import cv2
import logging
import re
import time
from dotenv import load_dotenv

os.environ['FLAGS_enable_onednn'] = '0'
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
logging.getLogger("ppocr").setLevel(logging.ERROR)

load_dotenv()

from groq import Groq
from paddleocr import PaddleOCR
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
console = Console()

# Инициализация OCR
with console.status("[bold green]Подготовка системы..."):
    ocr_model = PaddleOCR(
        use_textline_orientation=True,
        lang='ru',
        enable_mkldnn=False,
        text_det_limit_side_len=2000,
        text_recognition_batch_size=1
    )


def process_ttn(img_path):
    avg_conf = 0
    with console.status("[bold yellow]Анализ документа...", spinner="dots"):
        # OCR
        image = cv2.imread(img_path)
        if image is None: return

        h, w = image.shape[:2]
        if max(h, w) > 2000:
            scale = 2000 / max(h, w)
            image = cv2.resize(image, (int(w * scale), int(h * scale)))
            w = image.shape[1]

        result = ocr_model.ocr(image)
        if not result or not result[0]:
            console.print("[red]Текст не найден.[/red]")
            return

        # КЛАСТЕРИЗАЦИЯ СТРОК
        raw_data = []
        res = result[0]
        if isinstance(res, dict):
            for t, s, p in zip(res['rec_texts'], res['rec_scores'], res['dt_polys']):
                raw_data.append({'x': p[0][0], 'y': p[0][1], 'text': t, 'score': s})
        else:
            for line in res:
                raw_data.append({'x': line[0][0][0], 'y': line[0][0][1], 'text': line[1][0], 'score': line[1][1]})

        # Динамический центр
        xs = [r['x'] for r in raw_data]
        center_x = sorted(xs)[len(xs) // 2] if xs else w * 0.45

        # Группировка в полосы
        raw_data.sort(key=lambda r: r['y'])
        lines = []
        if raw_data:
            current_line = [raw_data[0]]
            for i in range(1, len(raw_data)):
                if abs(raw_data[i]['y'] - current_line[-1]['y']) <= 15:
                    current_line.append(raw_data[i])
                else:
                    lines.append(current_line)
                    current_line = [raw_data[i]]
            lines.append(current_line)

        # Сборка текста и фильтрация мусора
        prompt_text = ""
        all_conf = []
        trash_patterns = ['белбланкавыд', 'гознак', 'издательство', 'код формы', 'размножению не подлежит']

        for i, line in enumerate(lines):
            line.sort(key=lambda x: x['x'])
            parts = []
            for item in line:
                # Пропускаем типографский мусор
                if any(p in item['text'].lower() for p in trash_patterns):
                    continue
                side = "L" if item['x'] < center_x else "R"
                parts.append(f"[{side}] {item['text']}")
                all_conf.append(item['score'])

            if parts:
                prompt_text += f"L{i:02} | " + " | ".join(parts) + "\n"

        avg_conf = (sum(all_conf) / len(all_conf)) * 100 if all_conf else 0

        # LLM
        client = Groq(api_key=GROQ_API_KEY)

        prompt = f"""
        Extract data from TTN invoice to JSON. 
        CRITICAL: Field 'name' must be FULL technical description. Merge consecutive lines.
        IGNORE index numbers (6 digits) in UNP fields. UNP is 9 digits.

        OCR TEXT:
        {prompt_text}
        """

        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system",
                     "content": "You are a precise data extractor. Return ONLY JSON. Do not shorten product names."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0,
                max_tokens=8000,
                response_format={"type": "json_object"}
            )
            final_json = json.loads(response.choices[0].message.content)
        except Exception as e:
            console.print(f"[red]Ошибка ИИ:[/red] {e}")
            return

    out_file = f"result_{os.path.basename(img_path)}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(final_json, f, indent=4, ensure_ascii=False)

    console.print(f"\n[bold green]Готово. Точность OCR: {avg_conf:.2f}%[/bold green]")
    syntax = Syntax(json.dumps(final_json, indent=4, ensure_ascii=False), "json", theme="monokai", word_wrap=True)
    console.print(Panel(syntax, title=f"Файл: {out_file}"))


if __name__ == "__main__":
    console.clear()
    console.print(Panel("[bold blue]TTN OCR SYSTEM[/bold blue]", expand=False))
    while True:
        path = input("\nВведите путь к файлу (или 'q' для выхода) > ").strip()
        if path.lower() == 'q': break
        if os.path.exists(path):
            process_ttn(path)
        else:
            console.print("[red]Файл не найден.[/red]")