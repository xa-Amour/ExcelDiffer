#-*- coding: UTF-8 -*- 
from django.shortcuts import render
from django.http import JsonResponse
from django.http import StreamingHttpResponse
import os
from ExcelDiffer.settings import BASE_DIR
from svr import  differ,util
from models import History
import datetime
import logging

logger = logging.getLogger(__name__)

def index(request):
    logger.debug("request for index")
    return render(request,'index.html')

def listHistory(request):
    logger.debug("request for listHistory")
    his = History.objects.all()
    return render(request,'history.html',{'his':his})

def getHistoryReport(request,hid):
    logger.debug("request for getHistoryReport: %s"%(hid))
    h = History.objects.get(id=int(hid))
    if h:
        report = util.loadReport(h.name)
        return JsonResponse(report)
    else:
        return JsonResponse({'status':'error','msg':'no such report'})


def diff(request):  
    if request.method == "POST":
        try:   
            excel_old = request.FILES.get("excel_old", None)
            excel_new = request.FILES.get("excel_new", None)
            #check if files are correct
            if not excel_old or not excel_new:
                logger.warn("the input is not correct")  
                return JsonResponse({'status':'error','msg':"no files for upload!"})
            f_old,e_old = os.path.splitext(excel_old.name)
            f_new,e_new = os.path.splitext(excel_new.name)
            if e_old not in ('.xls','.xlsx') or e_new not in ('.xls','.xlsx'):
                logger.warn("the input is not correct")  
                return JsonResponse({'status':'error','msg':"please upload the excel!"})
            
            #upload two files to server
            shortName = '_'.join([f_old,f_new,datetime.datetime.now().strftime('%y%m%d%H%M%S')]) 
            uploadPath = os.path.join(BASE_DIR,"upload",shortName)
            os.mkdir(uploadPath)
            path_old = os.path.join(uploadPath,excel_old.name)
            path_new = os.path.join(uploadPath,excel_new.name)
            logger.debug("upload:%s and %s"%(excel_old.name,excel_new.name))
            #upload excel-new
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
        
        try:
            #do diff
            report = differ.excelDiffer(path_old,path_new)
            brief = util.getBriefReport(report)
            #save history to db
            History(name = shortName).save()
            hid = History.objects.get(name = shortName).id
            #save report
            util.saveReport(shortName,{'status':'success','result':report,'brief':brief,'hid':hid})
            return JsonResponse({'status':'success','result':report,'brief':brief,'hid':hid}) 
        except Exception as e:
            logger.error("error when diff: %s"%(e))
            return JsonResponse({'status':'error','msg':'error while diff'})
        
    else:
        logger.warn("getReport is a post api")
        return JsonResponse({'res':'this is a post api'}) 
    
def downloadReport(request,hid):
    logger.debug("request for downloadReport: %s"%(hid))
    h = History.objects.get(id=int(hid))
    if not h:
        return JsonResponse({'status':'error','msg':'no such report'})
    #send the file chunk by chunk, so we can handle the big file    
    def file_iterator(file_name, chunk_size=512):
        with open(file_name) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    the_file_name = os.path.join(BASE_DIR,"upload",h.name+'.zip')
    response = StreamingHttpResponse(file_iterator(the_file_name))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format((h.name+'.zip').encode('utf-8'))
    return response
     
