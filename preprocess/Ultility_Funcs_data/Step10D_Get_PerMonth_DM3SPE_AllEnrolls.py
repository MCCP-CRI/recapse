import os
import glob
import csv
import matplotlib.pyplot as plt
import numpy as np
#import cupy as cp
import pandas as pd
import seaborn as sn
from sklearn import metrics
import sys
#from IPython.display import display
from Ultility_Funcs_data.Recapse_Ultility import *
from datetime import date
from datetime import datetime
from dateutil import relativedelta

####Mac Pro
#path_csv = r'/Users/qqi227/Desktop/dp/Rewrite/TestingdataforUH3-Dec162020'
#path_save = r'/Users/qqi227/Desktop/dp/Rewrite/8_Characteristics2/Patient_Level'
#path_ID = r'/users/qqi227/Desktop/dp/Rewrite/1_ID_Sources_Info'
##path_site = r'/Users/qqi227/Desktop/dp/Rewrite'

def Step10D_Get_PerMonth_DM3SPE_AllEnrolls(user_name, path_input, path_output):

    ###HPC
    path_column_code = str(path_output) + "/" +str(user_name) +'/10A_PerPatient_UniqueCodes'
    path_save = str(path_output) + "/" +str(user_name) + '/10D_DM3SPEFeature_inValidMonth'
    path_code = str(path_input) #r'/users/qqi227/Manual_Reviewed_Cases/Input_Manual_Reviewed_Cases'
    path_csv = str(path_output) + "/" +str(user_name) + '/10A_PerPatient_monthly_record'
    
    
    isExist = os.path.exists(path_save)
    if not isExist:
       # Create a new directory because it does not exist
       os.makedirs(path_save)
       print("The new directory is created!")
       
       
    ################################################################################
    #1.Load group df
    ################################################################################
    file_name = "Unique_Drug_And_Groups_inALLClaims.xlsx"
    completeName = os.path.join(path_code, file_name)
    drug_grp_df = pd.read_excel(completeName,header=0, index_col=False, dtype={'CODE': str})
    
    #reformat 
    code_type = 'DM3_SPE'
    drug_grp_df.loc[drug_grp_df['TYPE'] == 'DRUG_THERA_CLS_AHFS', 'TYPE'] = "DRUG_AHFS"  #change code type name
    curr_df = drug_grp_df['specific_group']
    curr_df = curr_df.fillna('NA')
    curr_df = 'DM3_SPE_' + curr_df
    drug_grp_df['specific_group'] = curr_df
    drug_grp_df = drug_grp_df.rename(columns={'specific_group': code_type})
       
    
    ##### per patients
    xlsx_files = glob.glob(os.path.join(path_csv, "*.xlsx"))
    #xlsx_files ='D:\R\Cancer_test\python_test_12_22\data_12_7\ID1024_Month_CCS_DIAG_Feature.xlsx'
    for f in xlsx_files:
        #print(f)
        curr_df = pd.read_excel(f,header=0, index_col=False)
        curr_id = f.split("ID")[1]
        curr_id = curr_id.split("_")[0]
        
        if len(list(curr_df)) >3:
            #print('yes')
            code_names = list(curr_df)[3:]
            
            ###get unique code
            curr_drug_AHFS_codes = get_codes_func(code_names,"DRUG_AHFS")
            curr_drug_NDC_codes = get_codes_func(code_names, "DRUG_NDC") #
            frames = [curr_drug_AHFS_codes, curr_drug_NDC_codes]
            unique_codes_df = pd.concat(frames,axis=0, ignore_index=True)
            
            if unique_codes_df.empty:
                #print('DataFrame is empty!')
                curr_grp_feature_df = curr_df.iloc[:,0:3] 
            else:
                unique_codes_df = find_listofcode_grp_func(unique_codes_df,code_type,drug_grp_df)   
                curr_grp_feature_df = create_grp_feature_df_func(unique_codes_df, code_type, curr_df)
                curr_grp_feature_df = curr_grp_feature_df.groupby(curr_grp_feature_df.columns, axis=1).sum()
                #curr_grp_feature_df = curr_grp_feature_df[curr_grp_feature_df.columns[::-1]]
                first_column = curr_grp_feature_df.pop('Month_End')
                curr_grp_feature_df.insert(0, 'Month_End', first_column)
                first_column = curr_grp_feature_df.pop('Month_Start')
                curr_grp_feature_df.insert(0, 'Month_Start', first_column)
                first_column = curr_grp_feature_df.pop('study_id')
                curr_grp_feature_df.insert(0, 'study_id', first_column)
             
        file_name = "ID" + curr_id+"_Month_"+ code_type +"_Feature.xlsx"
        completeName = os.path.join(path_save, file_name)
        curr_grp_feature_df.to_excel(completeName, header = True, index=False)
    print("10D done")
        
        
        
    
        
        