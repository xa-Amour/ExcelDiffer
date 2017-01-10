#-*- coding: UTF-8 -*- 

import reader
import logging

logger = logging.getLogger(__name__)
THRESHOLD = 0.5

def fuzzyComp(list_old,list_new):
    '''
    #use dp to count editdis
    #I define that if editdis< len(list_old)/2, return True; 
    #else return False
    #dp[i][j]=n means from list_old[:i] to list_new[:j]
    '''
    dp = [[0 for i in range(len(list_new)+1)] for j in range(len(list_old)+1)]
    dp[0][0] = 0 
    for i in range(1,len(list_old)+1):
        dp[i][0] = dp[i-1][0] + 1
    for j in range(1,len(list_new)+1):
        dp[0][j] = dp[0][j-1] + 1
    for i in range(1,len(list_old)+1):
        for j in range(1,len(list_new)+1):
            if list_old[i-1]=='*' or list_new[j-1]=='*' or list_old[i-1] == list_new[j-1]:
                dp[i][j] = min(dp[i-1][j-1],dp[i][j-1]+1,dp[i-1][j]+1)
            else:
                dp[i][j] = min(dp[i-1][j-1]+1,dp[i][j-1]+1,dp[i-1][j]+1) 

    return True if dp[-1][-1]<=len(list_old)*THRESHOLD else False



def diffRows(sheet_old,sheet_new):
    #only focus on row del and add, and fix that by make both fat
    #ignore the change, because we will repaire that at last
    #record the path when count the editdis
    dp = [[[0,[]] for i in range(len(sheet_new)+1)] for j in range(len(sheet_old)+1)]
    dp[0][0]=[0,[]]
    for i in range(1,len(sheet_old)+1):
        dp[i][0][0] = dp[i-1][0][0]+1
        dp[i][0][1] = dp[i-1][0][1][::]
        dp[i][0][1].append(('D',i-1))
    for j in range(1,len(sheet_new)+1):
        dp[0][j][0] = dp[0][j-1][0]+1
        dp[0][j][1] = dp[0][j-1][1][::]
        dp[0][j][1].append(('A',0))
    for i in range(1,len(sheet_old)+1):
        for j in range(1,len(sheet_new)+1):
            if fuzzyComp(sheet_old[i-1],sheet_new[j-1]):
                dp[i][j][0] = min(dp[i-1][j-1][0],dp[i][j-1][0]+1,dp[i-1][j][0]+1)
                flag = (dp[i-1][j-1][0],dp[i][j-1][0]+1,dp[i-1][j][0]+1).index(dp[i][j][0])
            else:
                dp[i][j][0] = min(dp[i][j-1][0]+1,dp[i-1][j][0]+1)
                flag = ('@',dp[i][j-1][0]+1,dp[i-1][j][0]+1).index(dp[i][j][0])
                   
            if flag == 0: # no change
                dp[i][j][1] = dp[i-1][j-1][1][::]
            elif flag == 1: #add new 
                dp[i][j][1] = dp[i][j-1][1][::]
                dp[i][j][1].append(('A',i))
            elif flag == 2: #del old
                dp[i][j][1] = dp[i-1][j][1][::]
                dp[i][j][1].append(('D',i-1))
                 
    return dp[-1][-1]


def sheetDiff(data_old, data_new):
    finalReport = {'A':[],'D':[],'E':[]}
    for sheet in data_old.keys():
        if sheet not in data_new:
            finalReport['D'].append({'sheet_name':sheet,
                                     'old_data':data_old[sheet]})
        else:
            #sheetReport = [sheetName,diffPath].append(fat_old_sheet,fat_new_sheet)
            if data_old[sheet] != data_new[sheet]:
                finalReport['E'].append({'sheet_name':sheet,
                                         'edit_path':{'A_row':[],'D_row':[],'A_col':[],'D_col':[],'cell':[]},
                                         'old_data':None,
                                         'new_data':None})
    for sheet in data_new.keys():
        if sheet not in data_old:
            finalReport['A'].append({'sheet_name':sheet,
                                     'new_data':data_new[sheet]})
    return finalReport



def excelDiffer(excel_old,excel_new):
    data_old = reader.excelReader(excel_old)
    data_new = reader.excelReader(excel_new)
    finalReport = sheetDiff(data_old, data_new)
    for sheetReport in finalReport['E']:
        sheetName,diffPath = sheetReport['sheet_name'],sheetReport['edit_path']
        sheet_old,sheet_new = data_old[sheetName],data_new[sheetName]

        #diff row
        report = diffRows(sheet_old,sheet_new)
        #fat
        of,l_o,l_n = 0,len(sheet_old[0]),len(sheet_new[0])
        for op,index in report[1]:
            if op == 'D':
                sheet_new.insert(index+of,['*']*l_n)
                diffPath['D_row'].append(index+of) 
            elif op == 'A':
                sheet_old.insert(index+of,['*']*l_o)
                diffPath['A_row'].append(index+of) 
                of += 1
       
        #T tansform
        sheet_old = map(list,zip(*sheet_old))
        sheet_new = map(list,zip(*sheet_new))

        #diff col
        report = diffRows(sheet_old,sheet_new)
        #fat again
        of,l_o,l_n = 0,len(sheet_old[0]),len(sheet_new[0])
        for op,index in report[1]:
            if op == 'D':
                sheet_new.insert(index+of,['*']*l_n)
                diffPath['D_col'].append(index+of) 
            elif op == 'A':
                sheet_old.insert(index+of,['*']*l_o)
                diffPath['A_col'].append(index+of) 
                of += 1

        #T tansform back
        sheet_old = map(list,zip(*sheet_old))
        sheet_new = map(list,zip(*sheet_new))

        #diff cell
        for i in range(len(sheet_old)):
            for j in range(len(sheet_old[0])):
                if sheet_old[i][j] == '*' or sheet_new[i][j] == '*' or sheet_old[i][j] == sheet_new[i][j]:
                    pass
                else:
                    diffPath['cell'].append([i,j]) 
        #sheetReport = [sheetName,diffPath,sheet_old(fat),sheet_new(fat)]
        sheetReport['old_data'] = sheet_old
        sheetReport['new_data'] = sheet_new
        
    return finalReport





if __name__ =="__main__": 
    res = excelDiffer("oldexcel1.xlsx","newexcel1.xlsx")
    print  res['E'][0]['edit_path']
