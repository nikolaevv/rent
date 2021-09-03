from openpyxl import Workbook

def create_all_payments_report(payments):
    wb = Workbook()
    ws = wb.active
    ws.append(['№', 'Сумма', 'Статус', 'Дата и время'])
    for payment in payments:
        ws.append([payment.id, payment.summ, payment.status, payment.timestamp])

    report_path = 'files/{}/report.xlsx'.format(REPORTS_FOLDER_NAME)
    wb.save(.format())