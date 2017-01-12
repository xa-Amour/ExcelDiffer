# readme

## require：

本系统使用django框架实现，使用xlrd读取excel文件，采用最短编辑距离dp算法实现对excel进行对比，并提供历史对比记录查看和对比报告下载。  

若从源码运行时（运行django服务或者直接从命令行调用diff方法）需要以下依赖：  

    python==2.7
    django==1.8.17
    xlrd
    sqlite3

若直接使用该系统，无需任何依赖可以直接从exe运行系统（已经使用dj2exe打包）。  

## use:  

*  运行exe即可。同时你也可以通过浏览器访问已经启动的[本机服务](http://localhost:5423/)，或访[我的云服务器](http://www.zing.ac.cn:8888)。   

* 从源码运行。通过github（暂时设为私有仓库）获取源码，使用`python path/to/ExcelDiffer/manage.py runserver`启动django服务，或者通过`python path/to/ExcelDifferApp/svr/differ oldpath newpath`直接从命令行调用对比算法。  

## function：  

1. Excel对比，在页面选择原excel和新excel（支持拖拽），点击对比即可得到对比结果。对比结果包括sheet的增加、删除、修改。对于修改的sheet，还有具体的行增删、列增删、单元格修改。删除显示为浅红色，增加显示为浅蓝色，修改显示为浅黄色。当选中修改时显示为浅灰色。  
2. 支持对比报告的下载，下载的报告可以离线查看。  
3. 支持历史对比记录和报告的查看和下载。   

## alg：
使用xlrd读取excel，读取格式为{'sheet_name':[[row0],[row1],...,[rown]],}
设计report格式为：  


    finalReport = {'A':[sheetReport],
                  'D':[sheetReport],
                  'E':[sheetReport],}
    #注：A代表新增的sheet，D代表删除的sheet，E代表修改的sheet
    sheetReport = {sheet_name:'sheet_name',
                   editReport:{editReport},
                   old_data:[[]],
                   new_data:[[]]
                }
    #注：A对应的sheetReport中edit_path和old_data为空
    #注：D对应的sheetReport中edit_path和new_data为空
    editReport = {'A_row':[Add_row_index],
                  'D_row':[Del_row_index],
                  'A_col':[Add_col_index],
                  'D_col':[Del_col_index],
                  'cell':[[Edit_cell_pos]]}
                  
首先通过sheet_name对比，获取新增的sheet，删除的sheet，修改的sheet。    
对于sheet需要进一步获取具体的修改内容。    
sheet的diff算法借鉴于字符串编辑距离的动态规划算法。  

1. 将行作为整体，计算从old到new的行编辑距离。  
2. 对行增加，在old对应位置插入空行；对于行删除，在new对应位置插入空行。  
3. 将二维数组转置`map(list,zip(*sheet))`。  
4. 重复步骤1，2，3。  
5. 对比扩展后的old和new，得到修改的cell。  

由于行的增删和列的增删会相互影响（行列的地位是相同的）。那么在计算行的编辑距离时，如何判断两行（在经过行增删或单元格修改后可能）为同一行。本系统采取的方法是，使用动态规划计算两行的编辑距离（=两个字符串的编辑距离），若两行的编辑距离<len(old_row)*THRESHOLD(默认为0.5)，则认为两行可能为同一行。计算两个sheet的行编辑距离时，只关注行的增删。得到行编辑距离后，使用空行填充两个sheet新增和删除的行，这么做是为了在计算列时屏蔽行对列的影响。  

本地报告的小黑科技，为了报告的离线查看，把结果报告以json形式保存到本地，但是使用ajax从html访问本地json文件属于跨域访问，受到浏览器的安全限制。因此，将json保存为fun(data),以js形式引入到html中，在html中注册function fun(data){}对本地json进行处理并展示。  
    
