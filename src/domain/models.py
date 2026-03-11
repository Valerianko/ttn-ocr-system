from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class DocumentType(str, Enum):
    TTN = "TTN"  # ТТН-1 (с автомобилем)
    TN = "TN"    # ТН-2 (без автомобиля)
    UNKNOWN = "UNKNOWN"

class TTNItem(BaseModel):
    name: str = Field(description="ПОЛНОЕ наименование: название, марка, ТУ, артикул, ТН ВЭД, Рег. уд. НЕ СОКРАЩАТЬ.")
    unit: Optional[str] = Field(default=None, description="ед. изм. (шт, уп, набор, флак, упак)")
    quantity: Optional[str] = Field(default=None)
    price: Optional[str] = Field(default=None)
    price_amount: Optional[str] = Field(default=None, description="Стоимость без НДС")
    vat_rate: Optional[str] = Field(default=None, description="Ставка НДС")
    vat_amount: Optional[str] = Field(default=None, description="Сумма НДС")
    total_with_vat: Optional[str] = Field(default=None, description="Стоимость с НДС")
    note: Optional[str] = Field(default=None, description="Примечания: РОЦ, надбавки, сроки")
    raw: Optional[str] = Field(default="", description="Сырая строка из OCR")

class TTNDocument(BaseModel):
    document_type: DocumentType = Field(default=DocumentType.UNKNOWN)
    date: Optional[str] = Field(default=None, description="Дата документа YYYY-MM-DD")
    number: Optional[str] = Field(default=None)
    series: Optional[str] = Field(default=None)
    shipper: Optional[str] = Field(default=None, description="Отправитель: Название + Адрес")
    shipper_unp: Optional[str] = Field(default=None)
    consignee: Optional[str] = Field(default=None, description="Получатель: Название + Адрес")
    consignee_unp: Optional[str] = Field(default=None)
    reason: Optional[str] = Field(default=None, description="Основание отпуска")
    table: List[TTNItem] = Field(default_factory=list)
    # ИТОГИ ДОКУМЕНТА
    grand_total: Optional[str] = Field(default=None, description="ИТОГО к оплате (всего стоимость с НДС)")
    total_vat_sum: Optional[str] = Field(default=None, description="Всего сумма НДС")
    total_amount_no_vat: Optional[str] = Field(default=None, description="Всего стоимость без НДС")
    cargo_places: Optional[str] = Field(default=None, description="Всего грузовых мест")
    cargo_mass: Optional[str] = Field(default=None, description="Всего масса груза, кг")