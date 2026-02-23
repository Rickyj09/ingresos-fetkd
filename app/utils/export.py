import csv
import io
from datetime import datetime
from typing import Iterable, List, Tuple, Any

from flask import Response, send_file
from openpyxl import Workbook


def export_csv(filename_base: str, headers: List[str], rows: Iterable[Iterable[Any]]) -> Response:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for r in rows:
        writer.writerow(list(r))
    csv_bytes = io.BytesIO(output.getvalue().encode("utf-8-sig"))  # UTF-8 con BOM (Excel friendly)

    filename = f"{filename_base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return send_file(
        csv_bytes,
        mimetype="text/csv",
        as_attachment=True,
        download_name=filename,
    )


def export_xlsx(filename_base: str, headers: List[str], rows: Iterable[Iterable[Any]]) -> Response:
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte"

    ws.append(headers)
    for r in rows:
        ws.append(list(r))

    bio = io.BytesIO()
    wb.save(bio)
    bio.seek(0)

    filename = f"{filename_base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(
        bio,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename,
    )