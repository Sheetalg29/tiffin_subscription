from pydantic import BaseModel


class ImportRejectedRow(BaseModel):
    row: int
    reason: str


class CustomerImportReport(BaseModel):
    total: int
    imported: int
    duplicates: int
    rejected: int
    rejected_rows: list[ImportRejectedRow]
