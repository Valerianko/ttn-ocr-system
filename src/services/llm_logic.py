from langchain_groq import ChatGroq
from src.domain.models import TTNDocument


class LLMService:
    def __init__(self, api_key: str):
        self.llm = ChatGroq(api_key=api_key, model_name="llama-3.3-70b-versatile", temperature=0)
        self.structured_llm = self.llm.with_structured_output(TTNDocument)

    def analyze(self, text: str) -> TTNDocument:
        prompt = f"""
        Ты профессиональный аудитор. Твоя задача: оцифровать ТТН Беларуси в JSON БЕЗ СОКРАЩЕНИЙ.

        ОЧЕНЬ ВАЖНО:
        - ЕСЛИ каких‑то данных в тексте НЕТ — оставь поле пустым (null/пустая строка). Ничего НЕ придумывай.
        - shipper/consignee: укажи только то, что ЯВНО видно в тексте (Белреамед, Вмк-Дент, Диасенс, Лодэ и т.п.).

        ПРАВИЛА ТИПА ДОКУМЕНТА:
        - "ТОВАРНАЯ НАКЛАДНАЯ" (ТН-2) -> это "TN". (Нет данных о ТС и водителе).
        - "ТОВАРНО-ТРАНСПОРТНАЯ НАКЛАДНАЯ" (ТТН-1) -> это "TTN". (Есть данные о ТС).

        ПРАВИЛА ПОЛЕЙ:
        1. series: Это БУКВЕННЫЙ код (например, 'ЮП', 'ЮТ'). Игнорируй цифру "1", если она стоит отдельно.
        2. note: Сюда ОБЯЗАТЕЛЬНО выпиши ВЕСЬ текст из правой колонки примечаний: "Фасовка", "Рег. уд.", "Отпускная цена" и т.д. Не сокращай!
        3. name: Склеивай ВСЕ строки описания товара слева от цен. Переноси ТУ, Артикулы, Латиницу (WDF, DCL). Не сокращай!
        4. raw: ПОЛНАЯ дословная реконструкция строки из OCR через ' | '.
        5. SHIPPER/CONSIGNEE: Не путай местами. Отправитель (Shipper) обычно Диасенс, Получатель (Consignee) обычно Лодэ.
        6. shipper_unp и consignee_unp: Найди 9-значные коды для обеих сторон.
        7. unit: строго [шт, уп, набор, флак, упак] или пусто. "yn" считай "уп", "WT" — "шт".
        8. quantity, price, price_amount, vat_rate, vat_amount, total_with_vat — бери только если они явно стоят в одной строке.
        9. reason: (договор, счет).
        10. ИТОГИ: Найди в конце таблицы: grand_total, total_vat_sum, cargo_places (мест), cargo_mass (масса).


        === ДАННЫЕ OCR ===
        {text}
        """
        return self.structured_llm.invoke(prompt)