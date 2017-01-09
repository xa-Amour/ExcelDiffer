# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
import os
from ExcelDiffer.settings import BASE_DIR
from svr import  differ
import datetime
import logging

logger = logging.getLogger(__name__)

def index(request):
    logger.debug("request for index")
    return render(request,'index.html')


def getReport(request):  
    
    if request.method == "POST":
        try:   
            excel_old = request.FILES.get("excel_old", None)
            excel_new = request.FILES.get("excel_new", None)
            if not excel_old or not excel_new:
                logger.warn("the input is not correct")  
                return JsonResponse({'status':'error','msg':"no files for upload!"})
            f_old,e_old = os.path.splitext(excel_old.name)
            f_new,e_new = os.path.splitext(excel_new.name)
            if e_old not in ('.xls','.xlsx') or e_new not in ('.xls','.xlsx'):
                logger.warn("the input is not correct")  
                return JsonResponse({'status':'error','msg':"please upload the excel!"})
            uploadPath = os.path.join(BASE_DIR,"upload",
                            '_'.join([f_old,f_new,datetime.datetime.now().strftime('%y%m%d%H%M')]))
            os.mkdir(uploadPath)
            path_old = os.path.join(uploadPath,excel_old.name)
            path_new = os.path.join(uploadPath,excel_new.name)
            logger.debug("upload:%s and %s"%(excel_old.name,excel_new.name))
        
            #upload excel-old  
            dest_excel_old = open(path_old,'wb+')
            for chunk in excel_old.chunks():
                dest_excel_old.write(chunk)  
            dest_excel_old.close()  
            #upload excel-new
            dest_excel_new = open(path_new,'wb+')
            for chunk in excel_new.chunks():
                dest_excel_new.write(chunk)  
            dest_excel_new.close()
        except Exception as e:
            logger.error("error when uploading: %s"%(e))
            return JsonResponse({'status':'error','msg':e})
        #do differ
        try:
            report = differ.excelDiffer(path_old,path_new)
            brief = '<h2>diff结果简报</h2></br>'
            A,D,E = len(report['A']),len(report['D']),len(report['E'])
            brief += '共增加sheet： %d 个，删除sheet： %d 个，修改sheet： %d 个</br>'%(A,D,E)
            for esheet in report['E']:
                ebrief = ''
                sheet_name,A_row,D_row,A_col,D_col,cell = esheet['sheet_name'],\
                    len(esheet['edit_path']['A_row']),len(esheet['edit_path']['D_row']),\
                    len(esheet['edit_path']['A_col']),len(esheet['edit_path']['D_col']),\
                    len(esheet['edit_path']['cell'])
                ebrief += '%s 表：增加 %d行，删除 %d行，增加 %d列，删除 %d列，修改 %d个单元格</br>'%(str(sheet_name),A_row,D_row,A_col,D_col,cell)
            brief += ebrief
            return JsonResponse({'status':'success','report':report,'brief':brief}) 
        except Exception as e:
            logger.error("error when diff: %s"%(e))
            return JsonResponse({'status':'error','msg':'error while diff'})
        
    else:
        logger.warn("getReport is a post api")
        return JsonResponse({'res':'this is a post api'}) 
     
