from functions import *

pdfs_tables = get_pdf_tables([r"D:\my work\python\HST_Pdf_enhancer\documents\الاثنين جلسة 1-4-2024 د19 وراثات.pdf",r"D:\my work\python\HST_Pdf_enhancer\documents\الاثنين 16-12-2024 د19 القاهرة الجديدة.pdf"])

print(pdfs_tables)


tablesList= get_tableList_from_tables(pdfs_tables)
print(tablesList.__len__())
