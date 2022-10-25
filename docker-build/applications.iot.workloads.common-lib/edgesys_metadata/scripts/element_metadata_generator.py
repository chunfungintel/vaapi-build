# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 11:00:35 2022

@author: weijunang
"""

import os 
import pandas as pd
import sys
import re

inputfile = sys.argv[1]   
xlsx = pd.ExcelFile(inputfile)   
df = pd.read_excel(xlsx,"metadata") 

unique_nodetype = df['Node type'].to_list()
unique_nodetype = list(dict.fromkeys(unique_nodetype))
# print(unique_nodetype)

elementlist = []
[elementlist.append([]) for i in range(len(unique_nodetype))]
namelist = []
[namelist.append([]) for i in range(len(unique_nodetype))]
displaynamelist = []
[displaynamelist.append([]) for i in range(len(unique_nodetype))]
typelist = []
[typelist.append([]) for i in range(len(unique_nodetype))]
valueslist = []
[valueslist.append([]) for i in range(len(unique_nodetype))]
defaultlist = []
[defaultlist.append([]) for i in range(len(unique_nodetype))]
placeholderlist = []
[placeholderlist.append([]) for i in range(len(unique_nodetype))]


elementdf_list = df["Element name"].to_list()
namedf_list = df["name"].to_list()
displaynamedf_list = df["displayName"].to_list()
typedf_list = df["type"].to_list()
valuesdf_list = df["values"].to_list()
defaultdf_list = df["default"].to_list()
placeholderdf_list = df["placeholder"].to_list()

for i in range(len(unique_nodetype)):
    for j in range(len(elementdf_list)):
        if df.at[j, 'Node type'] == unique_nodetype[i]:
            elementlist[i].append(elementdf_list[j])
            namelist[i].append(namedf_list[j])
            displaynamelist[i].append(displaynamedf_list[j])
            typelist[i].append(typedf_list[j])
            valueslist[i].append(valuesdf_list[j])
            defaultlist[i].append(defaultdf_list[j])
            placeholderlist[i].append(placeholderdf_list[j])
            
#print(elementlist)
#print()
#print(namelist)
#print()
#print(displaynamelist)
#print()
#print(typelist)
#print()
#print(valueslist)
#print()
#print(defaultlist)
#print()
#print(placeholderlist)
#print()

unique_elementlist = []
unique_namelist = []
unique_displaynamelist = []
unique_typelist = []
unique_valueslist = []
unique_defaultlist = []
unique_placeholderlist = []

#init list
for i in range(len(elementlist)):
    unique_elementlist.append([])
    unique_namelist.append([])
    unique_displaynamelist.append([])
    unique_typelist.append([])
    unique_valueslist.append([])
    unique_defaultlist.append([])
    unique_placeholderlist.append([])
    
    for j in range(len(set(elementlist[i]))):
        #unique_elementlist[i].append([])
        unique_namelist[i].append([])
        unique_displaynamelist[i].append([])
        unique_typelist[i].append([])
        unique_valueslist[i].append([])
        unique_defaultlist[i].append([])
        unique_placeholderlist[i].append([])

#consolidate list
for i in range(len(elementlist)):
    tempidx = 0
    for j in range(len(elementlist[i])):
        if elementlist[i][j] not in unique_elementlist[i]: #if not duplicated just append
            unique_elementlist[i].append(elementlist[i][j])
            unique_namelist[i][tempidx].append(namelist[i][j])
            unique_displaynamelist[i][tempidx].append(displaynamelist[i][j])
            unique_typelist[i][tempidx].append(typelist[i][j])
            unique_valueslist[i][tempidx].append(valueslist[i][j])
            unique_defaultlist[i][tempidx].append(defaultlist[i][j])
            unique_placeholderlist[i][tempidx].append(placeholderlist[i][j])
            tempidx = tempidx + 1

        else: #if duplicated, need find index of the original    
            for k in range(len(unique_elementlist[i])):
                if elementlist[i][j] == unique_elementlist[i][k]:
                    unique_namelist[i][k].append(namelist[i][j])
                    unique_displaynamelist[i][k].append(displaynamelist[i][j])
                    unique_typelist[i][k].append(typelist[i][j])
                    unique_valueslist[i][k].append(valueslist[i][j])
                    unique_defaultlist[i][k].append(defaultlist[i][j])
                    unique_placeholderlist[i][k].append(placeholderlist[i][j])

#print(unique_elementlist)
#print()
#print(unique_namelist)
#print()
#print(unique_displaynamelist)
#print()
#print(unique_typelist)
#print()
#print(unique_valueslist)
#print()
#print(unique_defaultlist)
#print()
#print(unique_placeholderlist)
#print()

finalstring = ''
myfile = open('metadata-elements.json', 'w')
myfile.write('{\n')
for i in range(len(unique_nodetype)):
    myfile.write('\t"'+unique_nodetype[i]+ '":[\n')                                 #write node type
    
    for j in range(len(unique_elementlist[i])):                                     #write element name
        myfile.write('\t\t{\n')
        myfile.write('\t\t\t"name":"' + unique_elementlist[i][j] + '"')

        if pd.isna(unique_namelist[i][j][0]):
            myfile.write('\n')
        else:
            myfile.write(',\n')
                                                                                    #if has params
            myfile.write('\t\t\t"params":[\n')

            for k in range(len(unique_namelist[i][j])):
                myfile.write('\t\t\t\t{\n')
                myfile.write('\t\t\t\t\t"name":"' + unique_namelist[i][j][k] + '",\n')
                myfile.write('\t\t\t\t\t"displayName":"' + unique_displaynamelist[i][j][k] + '",\n')
                myfile.write('\t\t\t\t\t"type":"' + unique_typelist[i][j][k] + '",\n')
                if unique_typelist[i][j][k] == "dropdown":
                    myfile.write('\t\t\t\t\t"values":[\n')
                    val = re.split(',', unique_valueslist[i][j][k])
                    for v in range(len(val)):
                        myfile.write('\t\t\t\t\t\t"' + val[v].strip() + '"')
                        if v == (len(val) - 1):
                            myfile.write('\n')
                        else:
                            myfile.write(',\n')
                    
                    myfile.write('\t\t\t\t\t],\n')

                if pd.isna(unique_defaultlist[i][j][k]):
                    myfile.write('\t\t\t\t\t"default":"",\n')
                else:
                    myfile.write('\t\t\t\t\t"default":"' + str(unique_defaultlist[i][j][k]) + '",\n')
                if pd.isna(unique_placeholderlist[i][j][k]):
                    myfile.write('\t\t\t\t\t"placeholder":""\n')
                else:
                    myfile.write('\t\t\t\t\t"placeholder":"' + unique_placeholderlist[i][j][k] + '"\n')

                if k == (len(unique_namelist[i][j]) -1):
                    myfile.write('\t\t\t\t}\n')
                else:
                    myfile.write('\t\t\t\t},\n')
            
            myfile.write('\t\t\t]\n')

        if j == (len(unique_elementlist[i]) -1):
            myfile.write('\t\t}\n')
        else:
            myfile.write('\t\t},\n')

    if i == (len(unique_nodetype) -1):
        myfile.write('\t]\n')
    else:
        myfile.write('\t],\n')

myfile.write('\n}')
myfile.close()        