# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 15:46:26 2022
@author: weijunan
"""

import pandas as pd
import os
import sys
    
def generate_metadata(metricname, target, testsuits):
    testsuits = '", "'.join(testsuits)
    start = end = '"'
    testsuits = start + testsuits + end
    metadata = '\t{\n' \
        + 2*'\t' + '"KPIMetricName": "' + metricname + '",\n'\
        + 2*'\t' + '"target": "' + str(target) + '",\n'\
        + 2*'\t' + '"custom": [\n'\
        + 3*'\t' + '{\n'+ 4*'\t'\
        + '"testsuit_name": ['\
        + testsuits + '],'  + '\n'\
        + 4*'\t' + '"target": "' + str(target) + '"\n'\
        + 3*'\t'\
        + '}\n'\
        + 2*'\t' + ']\n'\
        + '\t}'
    return metadata

def generate_metadata_multiple(metricname, target, testsuits): #testsuit is nested array
    
    metadata = ''    
        
    metadatastart = '\t{\n' \
        + 2*'\t' + '"KPIMetricName": "' + metricname + '",\n'\
        + 2*'\t' + '"target": "30",\n'\
        + 2*'\t' + '"custom": [\n'\
        
    metadataend = 2*'\t' + ']\n'\
    + '\t}'
    
    for i in range(len(target)):
        
        metadata += 3*'\t' + '{\n'+ 4*'\t'\
        + '"testsuit_name": ["'\
        + '", "'.join(testsuits[i]) + '"],'  + '\n'\
        + 4*'\t' + '"target": "' + str(target[i]) + '"\n'\
        + 3*'\t'\
            
        if i == len(target)-1:
            metadata += '}\n'
        else:
            metadata += '},\n'
    
    metadata = metadatastart + metadata + metadataend
    return metadata
    

inputfile = sys.argv[1]                
# inputfile = "nvr-metadata.xlsx"
# inputfile = "ifpd-metadata.xlsx"
# inputfile = "add-metadata.xlsx"
xlsx = pd.ExcelFile(inputfile)   
df = pd.read_excel(xlsx,"metadata")    

testsuit_list = df['TestSuit'].to_list()
temp_testsuit_list = testsuit_list

sheet_to_remove = []
testsuit_to_remove = []
sheet_list = df['KPI Sheet'].to_list()
temp_sheet_list = sheet_list

for i in range(len(temp_sheet_list)):
    if pd.isna(temp_sheet_list[i]):
        sheet_to_remove.append(sheet_list[i])
        testsuit_to_remove.append(testsuit_list[i])
[sheet_list.remove(sheet_to_remove[i]) for i in range(len(sheet_to_remove))]      
[testsuit_list.remove(testsuit_to_remove[i]) for i in range(len(testsuit_to_remove))]
    

kpiname = []
kpitarget = []
kpitestsuit = []

for i in range(len(sheet_list)):
    sheet = sheet_list[i]
    sheetdf = pd.read_excel(xlsx, sheet)
    sheetdf = sheetdf.iloc[: , 1:]
    numofcolumns = len(sheetdf.columns)
    
    if i == 0:                
        [kpiname.append(sheetdf.columns[j].strip()) for j in range(numofcolumns)]
        [kpitarget.append(sheetdf.at[0,sheetdf.columns[k]]) for k in range(numofcolumns)]
        for x in range(numofcolumns):
            temptestsuit = []
            temptestsuit.append(testsuit_list[i])
            kpitestsuit.append(temptestsuit)

    else:      
        for j in range(numofcolumns):
            found = False            
            for x in range(len(kpiname)):
                if sheetdf.columns[j].strip() == kpiname[x].strip() and sheetdf.at[0,sheetdf.columns[j]] == kpitarget[x]:
                    found = True                    
                    kpitestsuit[x].append(testsuit_list[i])
                    break
            if found == False:
                temptestsuit = []
                kpiname.append(sheetdf.columns[j].strip())
                kpitarget.append(sheetdf.at[0,sheetdf.columns[j]])   
                temptestsuit.append(testsuit_list[i])
                kpitestsuit.append(temptestsuit)
                
                  
    previoussheetdf = sheetdf
    

flag = 0
for i in range(len(kpitarget)):

    if pd.isna(kpitarget[i]):
        flag = 1
        break

if flag == 1:
    to_remove_index = []
    for i in range(len(kpitarget)):    
        if pd.isna(kpitarget[i]):
            to_remove_index.append(i)
            
    target_temp = []        
    if len(to_remove_index) > 0:
        for index, element in enumerate(kpitarget):
            if index not in to_remove_index:
                target_temp.append(element)
                
    name_temp = []        
    if len(to_remove_index) > 0:
        for index, element in enumerate(kpiname):
            if index not in to_remove_index:
                name_temp.append(element)            
                
    kpitarget = target_temp
    kpiname = name_temp
     
tempkpiname = []
tempkpitarget = []
tempkpitestsuit = []
[tempkpitarget.append([]) for i in range(len(set(kpiname)))]
[tempkpitestsuit.append([]) for i in range(len(set(kpiname)))]

idx = 0
for i in range(len(kpiname)):   

    if kpiname[i] not in tempkpiname: #if not duplicated just append
        tempkpiname.append(kpiname[i])
        tempkpitarget[idx].append(kpitarget[i])
        tempkpitestsuit[idx].append(kpitestsuit[i])
        idx+=1
    
    else:   #if duplicated, need find index of the original
        for j in range(len(tempkpiname)):
            if kpiname[i] == tempkpiname[j]:
                tempkpitarget[j].append(kpitarget[i])
                tempkpitestsuit[j].append(kpitestsuit[i])
                
kpiname = tempkpiname
kpitarget = tempkpitarget
kpitestsuit = tempkpitestsuit

myfile = open('metadata.json', 'w')
myfile.write('[\n')

index = 0
for i in range(len(kpiname)):
    index += 1
    if len(kpitarget[i]) == 1:    
        myfile.write(generate_metadata(kpiname[i], int(kpitarget[i][0]), kpitestsuit[i][0]))        
        if i < len(kpiname)-1:
            myfile.write(',\n')
        
    else:
        myfile.write(generate_metadata_multiple(kpiname[i], kpitarget[i], kpitestsuit[i]))
        if i < len(kpiname)-1:
            myfile.write(',\n')

myfile.write('\n]')
myfile.close()