from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class DocumentType(str, Enum):
    TTN = "TTN"
    TN = "TN"
    UNKNOWN = "UNKNOWN"

class TTNItem(BaseModel):
    name: str = Field(description="ПОЛНОЕ наименование товара (артикул, ТУ, Рег. уд., марка, модель)")
    unit: Optional[str] = Field(default=None, description="Единица измерения (шт, уп, набор, кг, л, мл)")
    quantity: Optional[str] = Field(default=None, description="Количество (строго из текста)")
    price: Optional[str] = Field(default=None, description="Цена за единицу (строго из текста)")
    price_amount: Optional[str] = Field(default=None, description="Стоимость без НДС")
    vat_rate: Optional[str] = Field(default=None, description="Ставка НДС (10%, 20%, Без НДС)")
    vat_amount: Optional[str] = Field(default=None, description="Сумма НДС")
    total_with_vat: Optional[str] = Field(default=None, description="Стоимость с НДС")
    note: Optional[str] = Field(default=None, description="Примечание: РОЦ, надбавки, сведения о первом импортере")
    raw: Optional[str] = Field(default="", description="Реконструкция строки: Название | Ед | Кол-во | Цена | Итог")

class TTNDocument(BaseModel):
    document_type: DocumentType = Field(default=DocumentType.UNKNOWN, description="Тип накладной: ТТН-1 или ТН-2")
    date: Optional[str] = Field(default=None, description="Дата составления документа")
    number: Optional[str] = Field(default=None, description="Номер документа")
    series: Optional[str] = Field(default=None, description="Серия документа")
    shipper: Optional[str] = Field(default=None, description="Грузоотправитель: Наименование + Полный адрес")
    shipper_unp: Optional[str] = Field(default=None, description="УНП отправителя (9 цифр)")
    consignee: Optional[str] = Field(default=None, description="Грузополучатель: Наименование + Полный адрес")
    consignee_unp: Optional[str] = Field(default=None, description="УНП получателя (9 цифр)")
    reason: Optional[str] = Field(default=None, description="Основание отпуска: Договор, счет, заказ")
    table: List[TTNItem] = Field(default_factory=list, description="Массив товарных позиций")
    grand_total: Optional[str] = Field(default=None, description="Итоговая сумма к оплате по документу")