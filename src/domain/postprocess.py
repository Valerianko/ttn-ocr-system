import re


class DataNormalizer:
    @staticmethod
    def fix_ocr_numbers(text: str) -> str:
        if not text: return text
        mapping = {"о": "0", "О": "0", "O": "0", "o": "0", "з": "3", "З": "3", "б": "6", "Б": "6"}

        def replacer(match):
            fragment = match.group(0)
            if any(char.isdigit() for char in fragment):
                for char, digit in mapping.items():
                    fragment = fragment.replace(char, digit)
            return fragment

        return re.sub(r'[0-9оОOозЗбБ]+', replacer, str(text))

    @staticmethod
    def normalize_date(date_str: str) -> str:
        if not date_str: return ""
        months = {"января": "01", "февраля": "02", "марта": "03", "апреля": "04", "мая": "05", "июня": "06",
                  "июля": "07", "августа": "08", "сентября": "09", "октября": "10", "ноября": "11", "декабря": "12"}
        try:
            d = date_str.lower().replace("г.", "").strip()
            for m_name, m_num in months.items():
                if m_name in d:
                    day = re.search(r'\d+', d).group().zfill(2)
                    year = re.search(r'\d{4}', d).group()
                    return f"{year}-{m_num}-{day}"
            match = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', d)
            if match: return f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
        except:
            pass
        return date_str