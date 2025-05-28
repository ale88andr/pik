import openpyxl

from django.http import HttpResponse
from django.utils.encoding import escape_uri_path
from openpyxl.styles import Alignment, Font


ORDERS_HEADER = [
    "Изображение",
    "Наименование",
    "Ссылка",
    "Статус",
    "Цена ¥",
    "Курс",
    "Цена ₽",
    "Комиссия %",
    "Комиссия ₽",
    "Цена",
    "Заказчик",
]


def export_data_to_excel(fname, qs, header=ORDERS_HEADER, footer=None):
    CTYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    response = HttpResponse(content_type=CTYPE)
    response["Content-Disposition"] = f"attachment; filename={escape_uri_path(fname)}.xlsx"

    # Создание excel
    wb = openpyxl.Workbook()
    sheet = wb.active
    current_row = 2 if header else 1

    # Установка стилей
    bold_font = Font(size=12, bold=True)
    centered = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Добавление данных
    if header:
        sheet.append(header)
        for cell in sheet[1]:
            cell.font = bold_font

    for obj in qs:
        if obj.img:
            img = openpyxl.drawing.image.Image(obj.img)
            img.height = 250
            img.width = 100
            img.anchor = f"A{current_row}"
            sheet.add_image(img)
            sheet.row_dimensions[current_row].height = 200

        sheet.append(obj.get_calculated_data)

        for cell in sheet[current_row]:
            if cell.value is not None:
                cell.alignment = centered

        current_row += 1

    if footer:
        sheet.append(footer)

    sheet.column_dimensions["A"].width = 15
    sheet.column_dimensions["B"].width = 30
    sheet.column_dimensions["C"].width = 30
    sheet.column_dimensions["D"].width = 20
    sheet.column_dimensions["K"].width = 20

    wb.save(response)

    return response


def export_to_excel(fname, data, header, footer=None):
    CTYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    response = HttpResponse(content_type=CTYPE)
    response["Content-Disposition"] = f"attachment; filename={escape_uri_path(fname)}.xlsx"

    # Создание excel
    wb = openpyxl.Workbook()
    sheet = wb.active

    # Установка стилей
    bold_font = Font(size=12, bold=True)

    # Добавление данных
    if header:
        sheet.append(header)
        for cell in sheet[1]:
            cell.font = bold_font

    for row in data:
        sheet.append(row)

    if footer:
        sheet.append(footer)

    sheet.column_dimensions["A"].width = 50
    sheet.column_dimensions["B"].width = 30
    sheet.column_dimensions["C"].width = 20

    wb.save(response)

    return response
