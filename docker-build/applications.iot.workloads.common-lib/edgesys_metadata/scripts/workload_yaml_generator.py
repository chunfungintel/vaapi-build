# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 09:38:45 2022

@author: weijunan
"""

import os 
import pandas as pd
import sys

def workload_common_generator(workload_id, workload_type, harbourweb, image, image_tag, srcrepo, documentlink, version,supported_use_case):
    returnString = '  - id: '+ workload_id + '\n'\
                +'    type: '+ workload_type + '\n'\
                + '    type_details:\n'\
                + '      harbor_website: '+ harbourweb + '\n'\
                + '      image: '+ image + '\n'\
                + '      image_tag: '+ image_tag + '\n'\
                + '      src_repository: '+ srcrepo + '\n'\
                + '      documentation_link: '+ documentlink + '\n'\
                + '    version: '+ version + '\n'\
                + '    supported_use_case: '+ '\n'\
                + '      - '+ supported_use_case + '\n'
    
    return returnString

def KMPSearch(pat, txt):
    M = len(pat)
    N = len(txt)
    flag = False
 
    lps = [0]*M
    j = 0 
 
    computeLPSArray(pat, M, lps)
 
    i = 0
    while i < N:
        if pat[j] == txt[i]:
            i += 1
            j += 1
 
        if j == M:
            flag = True
            j = lps[j-1]
 
        elif i < N and pat[j] != txt[i]:
            if j != 0:
                j = lps[j-1]
            else:
                i += 1
                
    return flag
 
def computeLPSArray(pat, M, lps):
    len = 0 
    lps[0] 
    i = 1
     
    while i < M:
        if pat[i]== pat[len]:
            len += 1
            lps[i] = len
            i += 1
        else:
            
            if len != 0:
                len = lps[len-1]
 
            else:
                lps[i] = 0
                i += 1
                
# inputfile = sys.argv[1]                
inputfile = "nvr-metadata.xlsx"
# inputfile = "ifpd-metadata.xlsx"
# inputfile = "add-metadata.xlsx"
xlsx = pd.ExcelFile(inputfile)   
df = pd.read_excel(xlsx,"metadata") 

project = ''
for i in range(len(inputfile)):
    if inputfile[i] == '-':
        break
    project += inputfile[i]
    
testsuiteid_list = df['TestSuit'].to_list()
workloadname_list = df['use-case-workload-mappings name'].to_list()
wlcbench_config_sheet_list = df['wlcbench config Sheet'].to_list()
workload_container_sheet_list = df['workload container Sheet'].to_list()
workloadid_list = df['workload id'].to_list()
parameter_sheet_list = df['Parameter Sheet'].to_list()
supportedplatform_list = df['supported_platform'].to_list()
use_case_mapping_list = df['use-case-workload-mappings name'].to_list()
workload_header_list = df['workload header'].to_list()

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
USE_CASE_VARIANT
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
if inputfile == "nvr-metadata.xlsx":          
    unique_workloadname_list = workloadname_list

    unique_workloadname_list = list(dict.fromkeys(unique_workloadname_list))
    
    workloadname_list_index = []
    [workloadname_list_index.append(workloadname_list.index(unique_workloadname_list[i])) for i in range(len(unique_workloadname_list))]
    
    va_info_df = pd.read_excel(xlsx,"va-info")
    hmi_info_df = pd.read_excel(xlsx,"hmi-info")
    
    va_id_list = va_info_df['id'].to_list()
    va_detect_list = va_info_df['Detect'].to_list()
    va_classify_list = va_info_df['Classify'].to_list()
    
    hmi_id_list = hmi_info_df['id'].to_list()
    hmi_info_list = hmi_info_df['info'].to_list()    
    
    idx = 0
    finalstring = ''
    for i in range(len(unique_workloadname_list)):
        # print(i)
        name = '  - name: "'+str(unique_workloadname_list[i].strip())+'"\n'
        use_case = '    use_case: "'+project+'"\n'
        
        configsheet = wlcbench_config_sheet_list[workloadname_list_index[i]]
        wlcbench_workload_df = pd.read_excel(xlsx,configsheet)
        
        type_list = wlcbench_workload_df["type"]
        wlcbench_type = '    type: "'+type_list[0]+'"\n'
        
        use_case_yaml_url_list = wlcbench_workload_df["url"]
        url = '    use_case_yaml_url: "'+use_case_yaml_url_list[0]#+'"\n'
        use_case_yaml_list = wlcbench_workload_df["use_case_yaml"]    
        use_case_yaml_url = url + use_case_yaml_list[0]+'"\n'
        
        use_case_yaml_version_list = wlcbench_workload_df["use_case_yaml_version"]
        if str(use_case_yaml_version_list[0]) == 'nan':
            use_case_yaml_version = '    version: ""\n'
        else:
            use_case_yaml_version = '    version: "'+str(use_case_yaml_version_list[0])+'"\n'     
        
        provision_url = wlcbench_workload_df["provisioning_yaml_url"].to_list()
            
        url = '    provisioning_yaml_url: "'+str(provision_url[0])
        provisioning_yaml_list = wlcbench_workload_df["provisioning_yaml"]
        provisioning_yaml_url = url + provisioning_yaml_list[0]+'"\n'
        
        profile_sets_yaml_url_name = unique_workloadname_list[i].lower().replace(' ', '-')
        if profile_sets_yaml_url_name[-1] == '-':
            profile_sets_yaml_url_name = profile_sets_yaml_url_name[:-1]
        profile_sets_file_name = profile_sets_yaml_url_name + '-profile-sets.yaml'
        profile_sets_yaml_url_name = '    profile_sets_yaml_url_name: "' + use_case_yaml_url_list[0] + profile_sets_file_name + '"\n'
    
        finalstring += name + use_case + wlcbench_type + use_case_yaml_version + use_case_yaml_url + provisioning_yaml_url + profile_sets_yaml_url_name
        
        """
        parameters
        """
        temp_profile_list = df['Profile'].to_list()
        temp_hmi_list = df['HMI'].to_list()
        temp_vidformat_list = df['Video Format'].to_list()
        temp_infdevice_list = df['Inference Device'].to_list()
        if i != len(unique_workloadname_list)-1:
            para_range = workloadname_list_index[i+1] - workloadname_list_index[i]            
        else:
            para_range = len(testsuiteid_list) - workloadname_list_index[i]
                    
        unique_profile_list = []
        unique_hmi_list = []
        unique_vidformat_list = []
        unique_infdev_list = []
        while idx < para_range + workloadname_list_index[i]:
            unique_profile_list.append(temp_profile_list[idx])
            unique_hmi_list.append(temp_hmi_list[idx])
            unique_vidformat_list.append(temp_vidformat_list[idx])
            unique_infdev_list.append(temp_infdevice_list[idx])            
            idx += 1
        
        unique_profile_list = list(dict.fromkeys(unique_profile_list))
        unique_hmi_list = list(dict.fromkeys(unique_hmi_list))
        unique_vidformat_list = list(dict.fromkeys(unique_vidformat_list))
        unique_infdev_list = list(dict.fromkeys(unique_infdev_list))
        
        finalstring += '    parameters:\n'
        finalstring += '      - id: Decoder_Type\n'\
                        + '        display_name: Decoder Type\n'\
                        + '        type: string\n'\
                        + '        possible_values:\n'
        for j in range(len(unique_vidformat_list)):
            if unique_vidformat_list[j] != 'na':
                finalstring += '          - ' + unique_vidformat_list[j].upper() + '\n'
                
        finalstring += '      - id: Inference_Configuration\n'\
                        + '        display_name: Inference Configuration\n'\
                        + '        type: string\n'\
                        + '        possible_values:\n'
        for j in range(len(unique_profile_list)):            
            if unique_profile_list[j] != 'na':
                finalstring += '          - id: ' + unique_profile_list[j].upper() + '\n'\
                                + '            display_name: "'
                for k in range(len(va_id_list)):                    
                    if KMPSearch(unique_profile_list[j].lower(), va_id_list[k]) == True:   
                        finalstring +=  unique_profile_list[j].upper() + ' [' + va_info_df.columns[1]\
                                    + ': ' + va_detect_list[k] + ', ' + va_info_df.columns[2] + ': '
                        if ',' in va_classify_list[k]:
                            temp_classify = va_classify_list[k].split(', ')
                            for l in range(len(temp_classify)):
                                finalstring += temp_classify[l]
                                if l != len(temp_classify)-1:
                                    finalstring += ', '
                        else:
                            finalstring += va_classify_list[k]
                        
                        finalstring += ']"\n'
                    
                
        finalstring += '      - id: HMI_Configuration\n'\
                        + '        display_name: HMI Configuration\n'\
                        + '        type: string\n'\
                        + '        possible_values:\n'
        for j in range(len(unique_hmi_list)):
            if unique_hmi_list[j] != 'na':
                finalstring += '          - id: ' + unique_hmi_list[j].upper() + '\n'\
                                + '            display_name: "'                                
                for k in range(len(hmi_id_list)):  
                    if KMPSearch('"'+unique_hmi_list[j].lower()+'"', hmi_id_list[k]) == True:
                        finalstring += unique_hmi_list[j].upper() + hmi_info_list[k] + '"\n' 
                
        finalstring += '      - id: Inference_Device\n'\
                        + '        display_name: Inference Device\n'\
                        + '        type: string\n'\
                        + '        possible_values:\n'
        for j in range(len(unique_infdev_list)):
            if unique_infdev_list[j] != 'na':
                finalstring += '          - ' + unique_infdev_list[j].upper() + '\n'
        
    
        """
        check supported platform of each use_case_mapping_name
        """
        finalstring += '    supported_platform: \n'
        temp_supp_platform_list = []
        for j in range(len(workloadname_list)):        
            if str(workloadname_list[j].strip()) == str(unique_workloadname_list[i].strip()):
                temp_supp_platform_list.append(supportedplatform_list[j])
                
        temp_supp_platform_list = list(dict.fromkeys(temp_supp_platform_list))
        if not pd.isna(temp_supp_platform_list[0]):
            if ',' in temp_supp_platform_list[0]:
                temp_supp_platform_list = temp_supp_platform_list[0].split(', ')
                
        for j in range(len(temp_supp_platform_list)):
            finalstring += '      - ' + str(temp_supp_platform_list[j]) + '\n'
        
        """
        check testsuit id, workload container sheet and workload header of each use_case_mapping_name
        """
        temp_workloadid_list = []
        temp_workload_header_list = []
        temp_workload_container_sheet_list = []
        for j in range(len(workloadid_list)):
            if str(workloadname_list[j].strip()) == str(unique_workloadname_list[i].strip()):
                temp_workloadid_list.append(workloadid_list[j])
                temp_workload_header_list.append(workload_header_list[j])
                temp_workload_container_sheet_list.append(workload_container_sheet_list[j])
                
        temp_workloadid_list = list(dict.fromkeys(temp_workloadid_list))
        temp_workload_header_list = list(dict.fromkeys(temp_workload_header_list))
        temp_workload_container_sheet_list = list(dict.fromkeys(temp_workload_container_sheet_list))

        finalstring += '    workloads:\n'
        
        if temp_workload_header_list[0][:3] == 'WLH':
            for j in range(len(temp_workloadid_list)):
                containersheet = temp_workload_container_sheet_list[j]
                workload_container_df = pd.read_excel(xlsx, containersheet) 
                workload_container_version = workload_container_df['version'].tolist()[0]
                
                wlheadersheet = temp_workload_header_list[j]
                workload_header_df = pd.read_excel(xlsx, wlheadersheet) 
                wlheadername_list = workload_header_df['header name'].to_list()
                wlheaderid_list = workload_header_df['header id'].to_list()
                
                for k in range(len(wlheadername_list)):
                    finalstring += '      ' + wlheadername_list[k] + ':\n'\
                                    + '        workload_id: "' + wlheaderid_list[k] + '"\n'\
                                    + '        workload_version: "' + workload_container_version + '"\n' 
            
        else:
            for j in range(len(temp_workloadid_list)):
                containersheet = temp_workload_container_sheet_list[j]
                workload_container_df = pd.read_excel(xlsx, containersheet) 
                workload_container_version = workload_container_df['version'].tolist()[0]            
                
                finalstring += '      ' + temp_workload_header_list[j] + ':\n'\
                                + '        workload_id: "' + temp_workloadid_list[j] + '"\n'\
                                + '        workload_version: "' + workload_container_version + '"\n'
    
                   
        finalstring += '\n'
        
    with open('use_case_variant_metadata.yaml', 'w') as f:   
        f.write('use-case-variant:\n')
        f.write(finalstring) 
    
elif inputfile == "ifpd-metadata.xlsx" or inputfile == "add-metadata.xlsx":      
    unique_workloadid_list = workloadid_list
    unique_workloadname_list = workloadname_list
    
    unique_workloadid_list = list(dict.fromkeys(unique_workloadid_list))
    unique_workloadname_list = list(dict.fromkeys(unique_workloadname_list))
    
    workloadname_list_index = []
    [workloadname_list_index.append(workloadname_list.index(unique_workloadname_list[i])) for i in range(len(unique_workloadname_list))]
    
    finalstring = ''
    
    for i in range(len(unique_workloadname_list)):
        name = '  - name: "'+str(unique_workloadname_list[i].strip())+'"\n'
        use_case = '    use_case: "'+project+'"\n'
        
        configsheet = wlcbench_config_sheet_list[workloadname_list_index[i]]
        wlcbench_workload_df = pd.read_excel(xlsx,configsheet)
        
        type_list = wlcbench_workload_df["type"]
        wlcbench_type = '    type: "'+type_list[0]+'"\n'
        
        use_case_yaml_url_list = wlcbench_workload_df["url"]
        url = '    use_case_yaml_url: "'+use_case_yaml_url_list[0]#+'"\n'
        use_case_yaml_list = wlcbench_workload_df["use_case_yaml"]    
        use_case_yaml_url = url + use_case_yaml_list[0]+'"\n'
        
        use_case_yaml_version_list = wlcbench_workload_df["use_case_yaml_version"]
        if str(use_case_yaml_version_list[0]) == 'nan':
            use_case_yaml_version = '    version: ""\n'
        else:
            use_case_yaml_version = '    version: "'+str(use_case_yaml_version_list[0])+'"\n'     
        
        provision_url = wlcbench_workload_df["provisioning_yaml_url"].to_list()
            
        url = '    provisioning_yaml_url: "'+str(provision_url[0])
        provisioning_yaml_list = wlcbench_workload_df["provisioning_yaml"]
        provisioning_yaml_url = url + provisioning_yaml_list[0]+'"\n'
        
        profile_sets_yaml_url_name = unique_workloadname_list[i].lower().replace(' ', '-')
        if profile_sets_yaml_url_name[-1] == '-':
            profile_sets_yaml_url_name = profile_sets_yaml_url_name[:-1]
        profile_sets_file_name = profile_sets_yaml_url_name + '-profile-sets.yaml'
        profile_sets_yaml_url_name = '    profile_sets_yaml_url_name: "' + use_case_yaml_url_list[0] + profile_sets_file_name + '"\n'
    
        finalstring += name + use_case + wlcbench_type + use_case_yaml_version + use_case_yaml_url + provisioning_yaml_url + profile_sets_yaml_url_name
        
        finalstring += '    supported_platform: \n'
    
        """
        check supported platform of each use_case_mapping_name
        """
        temp_supp_platform_list = []
        for j in range(len(workloadname_list)):        
            if str(workloadname_list[j].strip()) == str(unique_workloadname_list[i].strip()):
                temp_supp_platform_list.append(supportedplatform_list[j])
                
        temp_supp_platform_list = list(dict.fromkeys(temp_supp_platform_list))
        if not pd.isna(temp_supp_platform_list[0]):
            if ',' in temp_supp_platform_list[0]:
                temp_supp_platform_list = temp_supp_platform_list[0].split(', ')
                
        for j in range(len(temp_supp_platform_list)):
            finalstring += '      - ' + str(temp_supp_platform_list[j]) + '\n'
        
        """
        check testsuit id, workload container sheet and workload header of each use_case_mapping_name
        """
        temp_workloadid_list = []
        temp_workload_header_list = []
        temp_workload_container_sheet_list = []
        for j in range(len(workloadid_list)):
            if str(workloadname_list[j].strip()) == str(unique_workloadname_list[i].strip()):
                temp_workloadid_list.append(workloadid_list[j])
                temp_workload_header_list.append(workload_header_list[j])
                temp_workload_container_sheet_list.append(workload_container_sheet_list[j])
                
        temp_workloadid_list = list(dict.fromkeys(temp_workloadid_list))
        temp_workload_header_list = list(dict.fromkeys(temp_workload_header_list))
        temp_workload_container_sheet_list = list(dict.fromkeys(temp_workload_container_sheet_list))

        finalstring += '    workloads:\n'
        
        workload_header_df = pd.read_excel(xlsx, temp_workload_header_list[0]) 
        wlheadername_list = workload_header_df['header name'].to_list()
        wlheaderid_list = workload_header_df['header id'].to_list()
        wlheadercontainer_list = workload_header_df['workload container Sheet'].to_list()
        
        for j in range(len(wlheadername_list)):
            finalstring += '      ' + wlheadername_list[j] + ':\n'\
                            + '        workload_id: "' + wlheaderid_list[j] + '"\n'
            containersheet = wlheadercontainer_list[j]
            workload_container_df = pd.read_excel(xlsx, containersheet) 
            workload_container_version = workload_container_df['version'].tolist()[0]
            finalstring += '        workload_version: "' + workload_container_version + '"\n'

                   
        finalstring += '\n'
        
    with open('use_case_variant_metadata.yaml', 'w') as f:   
        f.write('use-case-variant:\n')
        f.write(finalstring) 


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
PROFILE SETS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
if inputfile == "nvr-metadata.xlsx":     
    merged_testsuiteid_list = df['TestSuit'].to_list()
    temp_usecase_name_list = df['use-case-workload-mappings name'].to_list()
    merged_idx_list = []
    for i in range(len(merged_testsuiteid_list)):
        merged_testsuiteid_list[i] += ' '+temp_usecase_name_list[i]
        merged_idx_list.append(i)

    id_to_remove = []
    for i in range(len(merged_testsuiteid_list)):
        for j in range(i+1, len(merged_testsuiteid_list)):
            if merged_testsuiteid_list[i] == merged_testsuiteid_list[j]:
                id_to_remove.append(j)
                
    temp_testsuite_id_list = df['TestSuit'].to_list() 
    temp_usecase_name_list = df['use-case-workload-mappings name'].to_list()
    temp_supp_platform_list = df['supported_platform'].to_list()
    temp_para_sheet_list = df['Parameter Sheet'].to_list()
    temp_workloadheader_list = df['workload header'].to_list()
    temp_profile_list = df['Profile'].to_list()
    temp_hmi_list = df['HMI'].to_list()
    temp_vidformat_list = df['Video Format'].to_list()
    temp_infdevice_list = df['Inference Device'].to_list()

    temp_testsuite_id = []  
    temp_usecase_name = [] 
    temp_supp_platform = []
    temp_para_sheet = []
    temp_workloadheader = []
    temp_profile = []
    temp_hmi = []
    temp_vidformat = []
    temp_infdevice = []
    for i in range(len(temp_workloadheader_list)):
        if i not in id_to_remove:
            temp_testsuite_id.append(temp_testsuite_id_list[i])
            temp_usecase_name.append(temp_usecase_name_list[i])
            temp_supp_platform.append(temp_supp_platform_list[i])
            temp_para_sheet.append(temp_para_sheet_list[i])
            temp_workloadheader.append(temp_workloadheader_list[i])
            temp_profile.append(temp_profile_list[i])
            temp_hmi.append(temp_hmi_list[i])
            temp_vidformat.append(temp_vidformat_list[i])
            temp_infdevice.append(temp_infdevice_list[i])
           
    idx = 0
        
    current_wlname = unique_workloadname_list[0]
    for i in range(len(unique_workloadname_list)):
        final_string = ''
        profile_sets_yaml_url_name = unique_workloadname_list[i].lower().replace(' ', '-')
        profile_sets_file_name = profile_sets_yaml_url_name + '-profile-sets.yaml'    
        
        while idx < len(temp_testsuite_id):
            
            if temp_usecase_name[idx] == current_wlname:
                if temp_testsuite_id[idx] != 'na':
                    final_string += '  - id: ' + temp_testsuite_id[idx]+'\n'\
                                    + '    supported_platforms:\n'
                    
                    if not pd.isna(temp_supp_platform[idx]):
                        if ',' in temp_supp_platform[idx]:
                            supp_plat = temp_supp_platform[idx].split(', ')
                            for k in range(len(supp_plat)):
                                final_string += '      - '+ supp_plat[k] + '\n'
                        else:
                            supp_plat = temp_supp_platform[idx]
                            final_string += '      - '+ supp_plat + '\n'
                            
                    final_string += '    configuration:\n'
                    
                    final_string                += '      Decoder_Type: ' 
                    if temp_vidformat[idx] != 'na':
                        final_string += temp_vidformat[idx].upper() 
                    final_string += '\n'
                        
                    final_string                += '      Inference_Configuration: ' 
                    if temp_profile[idx] != 'na':
                        final_string += temp_profile[idx].upper() 
                    final_string += '\n'
                        
                    final_string                += '      HMI_Configuration: ' 
                    if temp_hmi[idx] != 'na':
                        final_string += temp_hmi[idx].upper() 
                    final_string += '\n'
                        
                    final_string                += '      Inference_Device: ' 
                    if temp_infdevice[idx] != 'na':
                        final_string += temp_infdevice[idx].upper() 
                    final_string += '\n'
                    
                    
                    parameter_sheet_df = pd.read_excel(xlsx, temp_para_sheet[idx])
                    parameter_sheet_df = parameter_sheet_df.iloc[: , 1:]
                    
                    final_string += '    workloads:\n'\
                                    + '      ' + temp_workloadheader[idx] + ':\n'\
                                    + '        parameters:\n'\
                                    + '          '+ str(parameter_sheet_df.columns[0]) +': ' + temp_testsuite_id[idx] + '\n'
                                                
                    for j in range(1, len(parameter_sheet_df.columns)):
                        final_string += '          '+ parameter_sheet_df.columns[j] +': ' + str(parameter_sheet_df.at[5,parameter_sheet_df.columns[j]]) +'\n'
                                
                    final_string += '\n'
            else:
                current_wlname = temp_usecase_name[idx]
                break

            idx += 1

        with open(profile_sets_file_name, 'w') as f:
            f.write('profile_sets:\n')
            f.write(final_string)    

elif inputfile == "ifpd-metadata.xlsx":      
    merged_usecasename_list = df['use-case-workload-mappings name'].to_list()
    temp_supp_plat_list = df['supported_platform'].to_list()
    merged_idx_list = []
    for i in range(len(merged_usecasename_list)):
        merged_usecasename_list[i] += ' '+temp_supp_plat_list[i]
        merged_idx_list.append(i)

    id_to_remove = []
    for i in range(len(merged_usecasename_list)):
        for j in range(i+1, len(merged_usecasename_list)):
            if merged_usecasename_list[i] == merged_usecasename_list[j]:
                id_to_remove.append(j)
 
    id_to_remove = list(dict.fromkeys(id_to_remove))

    temp_testsuite_id_list = df['TestSuit'].to_list() 
    temp_usecase_name_list = df['use-case-workload-mappings name'].to_list()
    temp_workloadheader_list = df['workload header'].to_list()
    temp_para_sheet_list = df['Parameter Sheet'].to_list()
    temp_supp_platform_list = df['supported_platform'].to_list()
    temp_profilesets_sheet_list = df['profile sets sheet'].to_list()    
    
    temp_testsuite_id = []  
    temp_usecase_name = [] 
    temp_workloadheader = []
    temp_para_sheet = []
    temp_supp_platform = []
    temp_profilesets_sheet = []
    
    for i in range(len(temp_workloadheader_list)):
        if i not in id_to_remove:
            temp_testsuite_id.append(temp_testsuite_id_list[i])
            temp_usecase_name.append(temp_usecase_name_list[i])
            temp_workloadheader.append(temp_workloadheader_list[i])
            temp_para_sheet.append(temp_para_sheet_list[i])
            temp_supp_platform.append(temp_supp_platform_list[i])
            temp_profilesets_sheet.append(temp_profilesets_sheet_list[i])
                
    for i in range(len(temp_profilesets_sheet)):
        finalstring = ''
        if temp_profilesets_sheet[i] != 'skip':
            profile_sets_file_name = temp_usecase_name[i].lower().replace(' ', '-') + '-profile-sets.yaml'
            profile_sets_df = pd.read_excel(xlsx, temp_profilesets_sheet[i])
            workload_header_df = pd.read_excel(xlsx, temp_workloadheader[i])
            parameter_sheet_df = pd.read_excel(xlsx, temp_para_sheet[i])
            parameter_sheet_df = parameter_sheet_df.iloc[: , 1:]
            
            numofparameters = len(parameter_sheet_df.columns)
            numofcolumns = len(profile_sets_df.columns)

            for j in range(numofcolumns):

                finalstring += '- id: ' + profile_sets_df.columns[j] + '\n'\
                                + '    supported_platforms:\n'
                if ',' in temp_supp_platform[i]:
                    supported_plat = temp_supp_platform[i].split(', ')
                    for k in range(len(supported_plat)):
                        finalstring += '      - ' + supported_plat[k] + '\n'
                else:
                    finalstring += '      - ' + temp_supp_platform[i] + '\n'
                    
                finalstring += '    workloads:\n'
                workloadheader_list = workload_header_df['header name'].to_list()
                testsuitname_list = profile_sets_df[profile_sets_df.columns[j]].to_list()
                
                for k in range(len(workloadheader_list)):
                    finalstring += '      ' + workloadheader_list[k] + ':\n'\
                                    + '        parameters:\n'

                    for l in range(numofparameters):
                        if parameter_sheet_df.columns[l] == 'testsuit':
                            finalstring += '          ' + parameter_sheet_df.columns[l] + ': ' + testsuitname_list[k] + '\n'
                        else:
                            finalstring += '          ' + parameter_sheet_df.columns[l] + ': ' + str(parameter_sheet_df.at[5, parameter_sheet_df.columns[l]]) + '\n'
        
                finalstring += '\n'
        
        with open(profile_sets_file_name, 'w') as f:
            f.write('profile_sets:\n')
            f.write(finalstring)
            
            
elif inputfile == "add-metadata.xlsx":     
    merged_usecasename_list = df['use-case-workload-mappings name'].to_list()
    temp_supp_plat_list = df['supported_platform'].to_list()
    merged_idx_list = []
    for i in range(len(merged_usecasename_list)):
        merged_usecasename_list[i] += ' '+temp_supp_plat_list[i]
        merged_idx_list.append(i)

    id_to_remove = []
    for i in range(len(merged_usecasename_list)):
        for j in range(i+1, len(merged_usecasename_list)):
            if merged_usecasename_list[i] == merged_usecasename_list[j]:
                id_to_remove.append(j)    
    id_to_remove = list(dict.fromkeys(id_to_remove))
        
    temp_testsuite_id_list = df['TestSuit'].to_list() 
    temp_usecase_name_list = df['use-case-workload-mappings name'].to_list()
    temp_workloadheader_list = df['workload header'].to_list()
    temp_para_sheet_list = df['Parameter Sheet'].to_list()
    temp_supp_platform_list = df['supported_platform'].to_list()
    temp_profilesets_sheet_list = df['profile sets sheet'].to_list()    
    
    temp_testsuite_id = []  
    temp_usecase_name = [] 
    temp_workloadheader = []
    temp_para_sheet = []
    temp_supp_platform = []
    temp_profilesets_sheet = []
    
    for i in range(len(temp_workloadheader_list)):
        if i not in id_to_remove:
            temp_testsuite_id.append(temp_testsuite_id_list[i])
            temp_usecase_name.append(temp_usecase_name_list[i])
            temp_workloadheader.append(temp_workloadheader_list[i])
            temp_para_sheet.append(temp_para_sheet_list[i])
            temp_supp_platform.append(temp_supp_platform_list[i])
            temp_profilesets_sheet.append(temp_profilesets_sheet_list[i])

    for i in range(len(temp_profilesets_sheet)):
        finalstring = ''
        if temp_profilesets_sheet[i] != 'skip':
            profile_sets_file_name = temp_usecase_name[i].lower().replace(' ', '-') + '-profile-sets.yaml'
            profile_sets_df = pd.read_excel(xlsx, temp_profilesets_sheet[i])
            workload_header_df = pd.read_excel(xlsx, temp_workloadheader[i])

            numofcolumns = len(profile_sets_df.columns)
            
            for j in range(numofcolumns):

                finalstring += '- id: ' + profile_sets_df.columns[j] + '\n'\
                                + '    supported_platforms:\n'
                if ',' in temp_supp_platform[i]:
                    supported_plat = temp_supp_platform[i].split(', ')
                    for k in range(len(supported_plat)):
                        finalstring += '      - ' + supported_plat[k] + '\n'
                else:
                    finalstring += '      - ' + temp_supp_platform[i] + '\n'
                    
                finalstring += '    workloads:\n'
                workloadheader_list = workload_header_df['header name'].to_list()
                
                profileset_column_list = profile_sets_df[profile_sets_df.columns[j]].to_list()
                for k in range(len(profileset_column_list)):
                    profileset_col = profileset_column_list[k].split(', ')
                    finalstring += '      ' + profileset_col[0] + ':\n'\
                                    + '        parameters:\n'
                                    
                    parameter_sheet_df = pd.read_excel(xlsx, profileset_col[2])
                    parameter_sheet_df = parameter_sheet_df.iloc[: , 1:]
                    numofparameters = len(parameter_sheet_df.columns)
                    
                    for l in range(numofparameters):
                        if parameter_sheet_df.columns[l] == 'testsuit':
                            finalstring += '          ' + parameter_sheet_df.columns[l] + ': ' + profileset_col[1] + '\n'
                        else:
                            finalstring += '          ' + parameter_sheet_df.columns[l] + ': ' + str(parameter_sheet_df.at[5, parameter_sheet_df.columns[l]]) + '\n'
                
        
                finalstring += '\n'

        with open(profile_sets_file_name, 'w') as f:
            f.write('profile_sets:\n')
            f.write(finalstring)            
            

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
WORKLOAD METADATA
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

testsuiteid_list = df['TestSuit'].to_list()
workloadname_list = df['use-case-workload-mappings name'].to_list()
wlcbench_config_sheet_list = df['wlcbench config Sheet'].to_list()
workload_container_sheet_list = df['workload container Sheet'].to_list()
workloadid_list = df['workload id'].to_list()
parameter_sheet_list = df['Parameter Sheet'].to_list()
supportedplatform_list = df['supported_platform'].to_list()
kpi_sheet_list = df['KPI Sheet'].to_list()

unique_workloadid_list = workloadid_list
unique_workloadname_list = workloadname_list

unique_workloadid_list = list(dict.fromkeys(unique_workloadid_list))
unique_workloadname_list = list(dict.fromkeys(unique_workloadname_list))

workloadid_list_index = []
[workloadid_list_index.append([]) for i in range(len(unique_workloadid_list))]

workload_meta_count = len(workloadid_list_index)

workloadname_list_index = []
[workloadname_list_index.append([]) for i in range(len(unique_workloadname_list))]

for i in range(len(unique_workloadid_list)):
    for j in range(len(workloadid_list)):
        if unique_workloadid_list[i] == workloadid_list[j]:
            workloadid_list_index[i].append(j) 

for i in range(len(unique_workloadname_list)):
    for j in range(len(workloadname_list)):
        if unique_workloadname_list[i] == workloadname_list[j]:
            workloadname_list_index[i].append(j)

workloadid_list_index = workloadname_list_index

if inputfile == "nvr-metadata.xlsx" or inputfile == "ifpd-metadata.xlsx":
    
    final_list = []
    finalstring = ''
    [final_list.append([]) for i in range(len(unique_workloadname_list))]
    
    temp_config_list = []
    temp_container_list = []
    [temp_config_list.append([]) for i in range(len(unique_workloadname_list))]
    [temp_container_list.append([]) for i in range(len(unique_workloadname_list))]
    for i in range(len(workloadname_list_index)):
        for j in range(len(workloadname_list_index[i])):
            temp_config_list[i].append(wlcbench_config_sheet_list[workloadid_list_index[i][j]])###
            temp_container_list[i].append(workload_container_sheet_list[workloadid_list_index[i][j]])###
    
    final_list = []
    [final_list.append([]) for i in range(len(unique_workloadname_list))]
    
    kpi_sheet_list = df['KPI Sheet'].to_list()
    
    finalstring = ''
    for i in range(len(final_list)):
        workload_id = workloadid_list[workloadname_list_index[i][0]]
        
        containersheet = temp_container_list[i][0]
        workload_common_df = pd.read_excel(xlsx, containersheet)
        
        workload_type = workload_common_df["type"][0]    
        harbourweb = workload_common_df["harbour_web"][0]
        image = workload_common_df["image"][0]
        image_tag = workload_common_df["image_tag"][0]
        srcrepo = workload_common_df["source_repository"][0]
        documentlink = '""' if pd.isna(workload_common_df["documentation_link"][0]) else workload_common_df["documentation_link"][0]
        version = workload_common_df["version"][0]
        supported_use_case = project
        finalstring += workload_common_generator(workload_id, workload_type, harbourweb, image, image_tag, srcrepo, documentlink, version, supported_use_case)        
               
        
        finalstring += '    supported_platform:\n'
        
        temp_supportedplatform_list = []
        temp_supportedplatform_list.append(supportedplatform_list[workloadname_list_index[i][0]])
    
        for j in range(len(workloadname_list_index[i])):     

            if supportedplatform_list[workloadname_list_index[i][j]] != temp_supportedplatform_list[0]:
                temp_supportedplatform_list.append(supportedplatform_list[workloadname_list_index[i][j]])
            
        temp_supportedplatform_list = list(dict.fromkeys(temp_supportedplatform_list))

        if ',' in temp_supportedplatform_list[0]:
            temp_supportedplatform_list = temp_supportedplatform_list[0].split(', ')

        for j in range(len(temp_supportedplatform_list)):
            finalstring += '      - ' + str(temp_supportedplatform_list[j]) + '\n'
        
        finalstring += '    parameters:\n'    
        parameter_sheet = pd.read_excel(xlsx,parameter_sheet_list[workloadname_list_index[i][0]]) 
        parameter_sheet_columns = parameter_sheet.columns.to_list()
        parameter_sheet_columns.remove('id')
        for j in range(len(parameter_sheet_columns)):
            finalstring += '      - id: ' + parameter_sheet_columns[j] + '\n'\
                            + '        display_name: ' + parameter_sheet[parameter_sheet_columns[j]][0] + '\n'\
                            + '        type: ' + parameter_sheet[parameter_sheet_columns[j]][1] + '\n'
            if parameter_sheet[parameter_sheet_columns[j]][1].strip() == 'number':
                finalstring += '        min: ' + str(parameter_sheet[parameter_sheet_columns[j]][3]) + '\n'\
                                + '        max: ' + str(parameter_sheet[parameter_sheet_columns[j]][4]) + '\n'\
                                + '        default: ' + str(parameter_sheet[parameter_sheet_columns[j]][5]) + '\n'
                
            elif parameter_sheet[parameter_sheet_columns[j]][1].strip() == 'string':     
                try:
                    possible_values = []
                    if not pd.isna(parameter_sheet[parameter_sheet_columns[j]][2]):
                        if parameter_sheet[parameter_sheet_columns[j]][2][0] == '#':
                            sheetandcolumn = parameter_sheet[parameter_sheet_columns[j]][2].replace('#','')
                            sheetandcolumn = sheetandcolumn.split(',')                    
                            sheet = sheetandcolumn[0]
                            col = sheetandcolumn[1]
                            
                            
                            temp_df = pd.read_excel(xlsx,sheet) 
                            col_list = df[col].to_list()
                            for k in range(len(workloadname_list_index[i])):
                                possible_values.append(col_list[workloadname_list_index[i][k]])
                                
                            finalstring += '        possible_values:\n' 
                            
                            possible_values = list(dict.fromkeys(possible_values))

                            for k in range(len(possible_values)):
                                if possible_values[k] != 'na':
                                    finalstring += '          - ' + possible_values[k] + '\n'
                            
                    elif pd.isna(parameter_sheet[parameter_sheet_columns[j]][2]):     

                        possible_values.append(parameter_sheet[parameter_sheet_columns[j]][5])
                                    
                    if possible_values[0] != 'na':
                        finalstring += '        default_value: ' + possible_values[0] + '\n'      
                    
                except:
                    print("Exception Error")
                else:
                    print("")
                    
        finalstring += '    kpi_metrices:\n'
        kpi = []
        alias = []
        unit_temp = []
        unit = []
        for j in range(len(workloadname_list_index[i])):
            kpi_sheet = kpi_sheet_list[workloadname_list_index[i][j]]        
            temp_kpi_df = pd.read_excel(xlsx,kpi_sheet)   
            temp_kpi_df = temp_kpi_df.iloc[: , 1:]         
            kpi_list = temp_kpi_df.columns.to_list()
    
            for k in range(len(kpi_list)):
                kpi.append(kpi_list[k].strip())
                alias.append(temp_kpi_df.loc[1][kpi_list[k]])
                unit_temp.append(temp_kpi_df.loc[2][kpi_list[k]])
    
            kpi = list(dict.fromkeys(kpi))
            alias = list(dict.fromkeys(alias))
            unit_temp = list(dict.fromkeys(unit_temp))
        
        for j in range(len(alias)):
            for k in range(len(unit_temp)):
                if not pd.isna(unit_temp[k]):                
                    if KMPSearch(unit_temp[k].lower(), alias[j].lower()) == True:
                        unit.append(unit_temp[k])
                        
                else:
                    unit.append("null")
    
        for j in range(len(kpi)):
            finalstring += '      - id: ' + kpi[j] + '\n' + '        alias: ' + alias[j] + '\n'\
                            + '        unit: ' + unit[j] + '\n'
            
        finalstring += '    test_suites:\n'
        
        temp_testsuiteid_list = []
        for j in range(len(workloadname_list_index[i])):    
            if testsuiteid_list[workloadname_list_index[i][j]] != 'na':        
                temp_testsuiteid_list.append(testsuiteid_list[workloadname_list_index[i][j]])

        temp_testsuiteid_list = list(dict.fromkeys(temp_testsuiteid_list))          
        for j in range(len(temp_testsuiteid_list)):
            finalstring += '      - id: ' + testsuiteid_list[workloadname_list_index[i][j]] + '\n'\
                            + '        ess_pipeline_json: "ess-' + testsuiteid_list[workloadname_list_index[i][j]] + '.json"\n'
            
        finalstring += '\n'
        
    with open('workload_metadata.yaml', 'w') as f:    
        f.write('workloads:\n')
        f.write(finalstring)    

elif inputfile == "add-metadata.xlsx":
    
    unique_workloadid_list = list(dict.fromkeys(df['workload id'].to_list()))
    
    workloadid_list_index = []
    [workloadid_list_index.append([]) for i in range(len(unique_workloadid_list))]
    for i in range(len(unique_workloadid_list)):
        for j in range(len(workloadid_list)):
            if unique_workloadid_list[i] == workloadid_list[j]:
                workloadid_list_index[i].append(j)
    
    temp_config_list = []
    temp_container_list = []
    temp_para_sheet_list = []
    temp_workloadid_list = []
    temp_kpisheet_list = []
    [temp_config_list.append([]) for i in range(len(unique_workloadid_list))]
    [temp_container_list.append([]) for i in range(len(unique_workloadid_list))]
    [temp_para_sheet_list.append([]) for i in range(len(unique_workloadid_list))]
    [temp_workloadid_list.append([]) for i in range(len(unique_workloadid_list))]
    [temp_kpisheet_list.append([]) for i in range(len(unique_workloadid_list))]
    for i in range(len(workloadid_list_index)):
        for j in range(len(workloadid_list_index[i])):
            temp_config_list[i].append(wlcbench_config_sheet_list[workloadid_list_index[i][j]])
            temp_container_list[i].append(workload_container_sheet_list[workloadid_list_index[i][j]])
            temp_para_sheet_list[i].append(parameter_sheet_list[workloadid_list_index[i][j]])
            temp_workloadid_list[i].append(testsuiteid_list[workloadid_list_index[i][j]])
            temp_kpisheet_list[i].append(kpi_sheet_list[workloadid_list_index[i][j]])

    
    finalstring = ''
    for i in range(len(unique_workloadid_list)):
        workload_id = workloadid_list[workloadid_list_index[i][0]]
        
        containersheet = temp_container_list[i][0]
        workload_common_df = pd.read_excel(xlsx, containersheet)
        
        workload_type = workload_common_df["type"][0]    
        harbourweb = workload_common_df["harbour_web"][0]
        image = workload_common_df["image"][0]
        image_tag = workload_common_df["image_tag"][0]
        if image_tag == 'na':
            image_tag = ''
        srcrepo = workload_common_df["source_repository"][0]
        if srcrepo == 'na':
            srcrepo = ''
        documentlink = '""' if pd.isna(workload_common_df["documentation_link"][0]) else workload_common_df["documentation_link"][0]
        version = workload_common_df["version"][0]
        supported_use_case = project
        finalstring += workload_common_generator(workload_id, workload_type, harbourweb, image, image_tag, srcrepo, documentlink, version, supported_use_case)        
               
        
        finalstring += '    supported_platform:\n'
        
        temp_supportedplatform_list = []
        temp_supportedplatform_list.append(supportedplatform_list[workloadid_list_index[i][0]])
    
        for j in range(len(workloadid_list_index[i])):     

            if supportedplatform_list[workloadid_list_index[i][j]] != temp_supportedplatform_list[0]:
                temp_supportedplatform_list.append(supportedplatform_list[workloadid_list_index[i][j]])
            
        temp_supportedplatform_list = list(dict.fromkeys(temp_supportedplatform_list))

        if ',' in temp_supportedplatform_list[0]:
            temp_supportedplatform_list = temp_supportedplatform_list[0].split(', ')

        for j in range(len(temp_supportedplatform_list)):
            finalstring += '      - ' + str(temp_supportedplatform_list[j]) + '\n'
        
        finalstring += '    parameters:\n'    
        parameter_sheet = pd.read_excel(xlsx,parameter_sheet_list[workloadid_list_index[i][0]])
        parameter_sheet = parameter_sheet.iloc[:, 1:]
        parameter_sheet_columns = parameter_sheet.columns.to_list()
        temp_workloadid_list[i] = list(dict.fromkeys(temp_workloadid_list[i]))
        
        for j in range(len(parameter_sheet_columns)):
            finalstring += '      - id: ' + parameter_sheet_columns[j] + '\n'\
                            + '        display_name: ' + parameter_sheet[parameter_sheet_columns[j]][0] + '\n'\
                            + '        type: ' + parameter_sheet[parameter_sheet_columns[j]][1] + '\n'
            if parameter_sheet[parameter_sheet_columns[j]][1].strip() == 'number':
                finalstring += '        min: ' + str(parameter_sheet[parameter_sheet_columns[j]][3]) + '\n'\
                                + '        max: ' + str(parameter_sheet[parameter_sheet_columns[j]][4]) + '\n'\
                                + '        default: ' + str(parameter_sheet[parameter_sheet_columns[j]][5]) + '\n'
            
            
            elif parameter_sheet[parameter_sheet_columns[j]][1].strip() == 'string':     

                    if not pd.isna(parameter_sheet[parameter_sheet_columns[j]][2]):
                        if parameter_sheet[parameter_sheet_columns[j]][2][0] == '#':
                            sheetandcolumn = parameter_sheet[parameter_sheet_columns[j]][2].replace('#','')
                            
                            if sheetandcolumn == 'metadata,TestSuit':

                                finalstring += '        possible_values:\n'
                                
                                for k in range(len(temp_workloadid_list[i])):
                                    if temp_workloadid_list[i][k] != 'na':
                                        finalstring += '          - ' + temp_workloadid_list[i][k] + '\n'
                                        
                                if temp_workloadid_list[i][0] != 'na':
                                    finalstring += '        default_value: ' + temp_workloadid_list[i][0] + '\n'
                            
                    elif pd.isna(parameter_sheet[parameter_sheet_columns[j]][2]):     
                        finalstring += '        default_value: ' + str(parameter_sheet[parameter_sheet_columns[j]][5]) + '\n'
                                            
        finalstring += '    kpi_metrices:\n'
        kpi = []
        alias = []
        unit_temp = []
        unit = []
        for j in range(len(workloadid_list_index[i])):
            kpi_sheet = kpi_sheet_list[workloadid_list_index[i][j]]        
            temp_kpi_df = pd.read_excel(xlsx,kpi_sheet)   
            temp_kpi_df = temp_kpi_df.iloc[: , 1:]         
            kpi_list = temp_kpi_df.columns.to_list()
    
            for k in range(len(kpi_list)):
                kpi.append(kpi_list[k].strip())
                alias.append(temp_kpi_df.loc[1][kpi_list[k]])
                unit_temp.append(temp_kpi_df.loc[2][kpi_list[k]])
    
            kpi = list(dict.fromkeys(kpi))
            alias = list(dict.fromkeys(alias))
            unit_temp = list(dict.fromkeys(unit_temp))
        
        
        for j in range(len(alias)):
            for k in range(len(unit_temp)):
                if not pd.isna(unit_temp[k]):   
                    if KMPSearch(unit_temp[k].lower(), alias[j].lower()) == True:
                        unit.append(unit_temp[k])                        
                        
                else:
                    unit.append("null")

        for j in range(len(kpi)):
            finalstring += '      - id: ' + kpi[j] + '\n' + '        alias: ' + alias[j] + '\n'\
                            + '        unit: ' + unit[j] + '\n'
            
        finalstring += '    test_suites:\n'
        
        temp_testsuiteid_list = []
        for j in range(len(workloadid_list_index[i])):    
            if testsuiteid_list[workloadid_list_index[i][j]] != 'na':        
                temp_testsuiteid_list.append(testsuiteid_list[workloadid_list_index[i][j]])

        temp_testsuiteid_list = list(dict.fromkeys(temp_testsuiteid_list))          
        for j in range(len(temp_testsuiteid_list)):
            finalstring += '      - id: ' + testsuiteid_list[workloadid_list_index[i][j]] + '\n'\
                            + '        ess_pipeline_json: "ess-' + testsuiteid_list[workloadid_list_index[i][j]] + '.json"\n'
            
        finalstring += '\n'
        
    with open('workload_metadata.yaml', 'w') as f:    
        f.write('workloads:\n')
        f.write(finalstring)    
        
      