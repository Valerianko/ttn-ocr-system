from langchain_groq import ChatGroq
from src.domain.models import TTNDocument

class LLMService:
    def __init__(self, api_key: str):
        self.llm = ChatGroq(api_key=api_key, model_name="llama-3.3-70b-versatile", temperature=0)
        self.structured_llm = self.llm.with_structured_output(TTNDocument)

    def analyze(self, text: str) -> TTNDocument:
        prompt = f"""
        Ты эксперт-бухгалтер. Твоя задача: перенести данные ТТН/ТН в JSON БЕЗ ПОТЕРЬ.

        ПРАВИЛА ТИПА ДОКУМЕНТА:
        - "ТОВАРНАЯ НАКЛАДНАЯ" (ТН-2) -> это "TN". (Нет данных о ТС и водителе).
        - "ТОВАРНО-ТРАНСПОРТНАЯ НАКЛАДНАЯ" (ТТН-1) -> это "TTN". (Есть данные о ТС).

        ПРАВИЛА ПОЛЕЙ:
        1. series: Это БУКВЕННЫЙ код (например, 'ЮП', 'ЮТ'). Игнорируй цифру "1", если она стоит отдельно.
        2. note: Сюда ОБЯЗАТЕЛЬНО выпиши ВЕСЬ текст из правой колонки примечаний: "Фасовка", "Рег. уд.", "Отпускная цена" и т.д. Не сокращай!
        3. name: Склей только основное название и ТУ ВУ.
        4. raw: ПОЛНАЯ реконструкция строки через ' | '.
        5. SHIPPER/CONSIGNEE: Не путай местами. Отправитель (Shipper) обычно Диасенс, Получатель (Consignee) обычно Лодэ.

        ТЕКСТ:
        {text}
        """
        return self.structured_llm.invoke(prompt)