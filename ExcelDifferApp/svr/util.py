#-*- coding: UTF-8 -*- 
import os
from ExcelDiffer.settings import BASE_DIR
import json
import zipfile
import logging
import shutil

logger = logging.getLogger(__name__) 
htmlPath = os.path.join(BASE_DIR,"ExcelDifferApp","templates","report.html")
cssPath = os.path.join(BASE_DIR,"ExcelDifferApp","static","style.css")
jsPath = os.path.join(BASE_DIR,"ExcelDifferApp","static","bundle.js")

def getBriefReport(report):
    brief = '<h2>diff结果简报</h2></br>'
    A,D,E = len(report['A']),len(report['D']),len(report['E'])
    brief += '共增加sheet： %d 个，删除sheet： %d 个，修改sheet： %d 个</br>'%(A,D,E)
    for esheet in report['E']:
        ebrief = ''
        sheet_name,A_row,D_row,A_col,D_col,cell = esheet['sheet_name'],\
            len(esheet['edit_path']['A_row']),len(esheet['edit_path']['D_row']),\
            len(esheet['edit_path']['A_col']),len(esheet['edit_path']['D_col']),\
            len(esheet['edit_path']['cell'])
        ebrief += '%s 表：增加 %d行，删除 %d行，增加 %d列，删除 %d列，修改 %d个单元格</br>'%(sheet_name.encode('UTF-8'),A_row,D_row,A_col,D_col,cell)
        brief += ebrief
    return brief

def saveReport(shortName,report):
    targetPath=os.path.join(BASE_DIR,"upload",shortName)
    #copy local html css js
    shutil.copyfile(htmlPath, os.path.join(targetPath,shortName+'.html'))
    shutil.copyfile(cssPath, os.path.join(targetPath,'style.css'))
    shutil.copyfile(jsPath, os.path.join(targetPath,'bundle.js'))
    #save report
    with open(os.path.join(targetPath,'report.json'),'w') as f:
        f.write("fun("+json.dumps(report)+")")
    #zip report
    make_zip(shortName)
        
def loadReport(shortName):
    with open(os.path.join(BASE_DIR,"upload",shortName,'report.json'),'r') as f:
        report = json.loads(f.read()[4:-1])
        return report

def make_zip(shortName):
    source_dir = os.path.join(BASE_DIR,"upload",shortName)
    output_dir = os.path.join(BASE_DIR,"upload",shortName+'.zip')
    zipf = zipfile.ZipFile(output_dir, 'w')    
    pre_len = len(os.path.dirname(source_dir))
    for parent, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)
            zipf.write(pathfile, arcname)
    zipf.close()