import json
import time
from groq import Groq


class LLMService:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    def analyze(self, text, retries=3):
        prompt = f"""
        Extract data from Belarusian TTN invoice into a clean JSON. 

        STRICT SCHEMA (KEYS MUST BE EXACTLY AS BELOW):
        consignee, consignee_unp, shipper, shipper_unp, date, document_type, number, reason, series, table.

        CRITICAL INSTRUCTIONS:
        1. TWO UNPs: You MUST find both UNP numbers (9 digits each). One for 'shipper_unp', one for 'consignee_unp'.
        2. NO SUMMARIZATION: Field 'name' must include all technical details (Art, Reg No, TU). 
           IMPORTANT: Remove unit names (шт, уп, yn, набор) from the 'name' field.
        3. TABLE FIELDS: Each item must have: name, unit, quantity, price, price_amount, vat_rate, vat_amount, total_with_vat, note, raw.
        4. RAW FIELD: Single string with column data separated by ' | '. Strip 'X:NNNN' markers.
        5. MISSING DATA: Use null if a specific field is not found.

        OCR TEXT:
        {text}
        """
        for i in range(retries):
            try:
                response = self.client.chat.completions.create(
                    messages=[
                        {"role": "system",
                         "content": "You are a precise data extractor. You follow the requested JSON schema exactly. You do not invent keys. You do not shorten technical text."},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0,
                    max_tokens=8000,
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
            except Exception:
                if i < retries - 1:
                    time.sleep(2)
                else:
                    return {"error": "LLM failed to match schema"}