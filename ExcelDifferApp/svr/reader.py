# -*- coding: utf-8 -*-
import xlrd
import xlutils.copy
import logging

logger = logging.getLogger(__name__) 


#read the excel,and put the data as  [[]] in dic,
#make the sheet_name be the key
def excelReader(excel_path):
    try:
        workbook = xlrd.open_workbook(excel_path)
    except Exception as e:
        logger.error("error when read %s : %s"%(excel_path,e))
        raise Exception
        
    datas = {}
    for sheet in workbook.sheets():
        sheet_name = sheet.name
        nrows = sheet.nrows
        #ncols = sheet.ncols
        rowData = []
        for row in range(nrows):
            rowData.append(sheet.row_values(row))
        datas[sheet_name] = rowData
    return datas
        
#demo, no use in this project
def excelWriter(old_path, diff_data, res_path):
    rb = xlrd.open_workbook(old_path)
    wb = xlutils.copy.copy(rb)
    ws = wb.get_sheet(0)
    ws.write(1, 1, 'changed!')
    wb.add_sheet('sheetnnn2',cell_overwrite_ok=True)
    wb.save(res_path)
    

