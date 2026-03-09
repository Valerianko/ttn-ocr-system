import re


class DataNormalizer:
    @staticmethod
    def fix_ocr_numbers(text: str) -> str:
        if not text:
            return text
        mapping = {"о": "0", "О": "0", "O": "0", "o": "0", "з": "3", "З": "3", "б": "6", "Б": "6"}

        def replacer(match):
            f = match.group(0)
            if any(c.isdigit() for c in f):
                for char, digit in mapping.items():
                    f = f.replace(char, digit)
            return f

        return re.sub(r'[0-9оОOозЗбБ]+', replacer, str(text))

    @staticmethod
    def normalize_date(text_blob: str) -> str:
        if not text_blob:
            return ""
        months = {
            "января": "01", "февраля": "02", "марта": "03", "апреля": "04", "мая": "05", "июня": "06",
            "июля": "07", "августа": "08", "сентября": "09", "октября": "10", "ноября": "11", "декабря": "12"
        }
        d = str(text_blob).lower().replace("г.", "").strip()

        # Текстовые даты
        for m_name, m_num in months.items():
            if m_name in d:
                match = re.search(rf'(\d{{1,2}})\s+{m_name}\s+(20\d{{2}})', d)
                if match:
                    return f"{match.group(2)}-{m_num}-{match.group(1).zfill(2)}"

        # Цифровые даты
        match = re.search(r'(\d{1,2})\.(\d{1,2})\.(20\d{2})', d)
        if match:
            return f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
        return ""

