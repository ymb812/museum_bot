import io
import datetime
from openpyxl import Workbook
from tortoise.fields.relational import BackwardFKRelation
from core.database.models import Report


async def create_excel(model):
    entries = await model.all()

    file_in_memory = io.BytesIO()
    book = Workbook()
    sheet = book.active

    # get model headers
    headers = []
    for field in model._meta.fields_map.values():
        if type(field) != BackwardFKRelation:
            headers.append(field.model_field_name)
    sheet.append(headers)

    # add users data
    for entry in entries:
        row = []
        for field_name in headers:
            cell = getattr(entry, field_name)
            if type(cell) == datetime.datetime:
                cell: datetime.datetime = cell.replace(tzinfo=None)
            row.append(cell)

        sheet.append(row)

    book.save(file_in_memory)
    file_in_memory.seek(0)

    return file_in_memory


async def create_excel_after_checking(reports: list[Report]):
    file_in_memory = io.BytesIO()
    book = Workbook()
    sheet = book.active

    sheet.append(['Айди отчета', 'Экспонат', 'Статус', 'Комментарий', 'ФИО проверяющего'])

    # add data
    is_empty = True
    for report in reports:
        if report.status != Report.StatusType.work:
            is_empty = False
            sheet.append(
                [
                    report.id,
                    (await report.exhibit).name,
                    report.status.value,
                    report.description,
                    (await report.creator).fio
                ]
            )

    book.save(file_in_memory)
    file_in_memory.seek(0)

    return file_in_memory, is_empty
