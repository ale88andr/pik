import openpyxl

from django.http import HttpResponse
from openpyxl.styles import Alignment


def export_data_to_excel(qs, header=None, footer=None):
    CTYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    response = HttpResponse(content_type=CTYPE)
    response["Content-Disposition"] = "attachment; filename=order.xlsx"

    # Создание excel
    wb = openpyxl.Workbook()
    sheet = wb.active
    current_row = 2 if header else 1

    # Добавление данных
    if header:
        sheet.append(header)

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
                cell.alignment = Alignment(
                    horizontal="center",
                    vertical="center",
                    wrap_text=True,
                )

        current_row += 1

    if footer:
        sheet.append(footer)

    sheet.column_dimensions["A"].width = 15
    sheet.column_dimensions["B"].width = 30
    sheet.column_dimensions["C"].width = 30

    wb.save(response)

    return response
