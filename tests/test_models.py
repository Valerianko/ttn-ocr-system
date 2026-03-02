from src.domain.models import TTNDocument, TTNItem, DocumentType


def test_ttn_document_creation():
    item = TTNItem(name="Тестовый товар", raw="Товар | шт | 10 | 100")

    doc = TTNDocument(
        document_type=DocumentType.TTN,
        number="12345",
        shipper="ООО Отправитель, Минск",
        shipper_unp="123456789",
        table=[item]
    )

    assert doc.document_type == DocumentType.TTN
    assert doc.number == "12345"
    assert len(doc.table) == 1
    assert doc.table[0].name == "Тестовый товар"
    assert doc.consignee is None