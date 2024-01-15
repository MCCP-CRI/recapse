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

def Step10A_Get_PerPatient_UniqueCodes_AllEnrolls(user_name, path_output):
    ####HPC
    path_csv = str(path_output) + "/" +str(user_name) + '/3_Get_PerMonthData_withCleanCodes'
    path_save = str(path_output) + "/" +str(user_name) + '/10A_PerPatient_UniqueCodes'
    path_ID = str(path_output) + "/" +str(user_name) + '/1_ID_Sources_Info'
    path_all_enrollmon = str(path_output) + "/" +str(user_name) + '/5_Enrollment_And_Prediction_Months'
    path_save_new_csv = str(path_output) + "/" +str(user_name) + '/10A_PerPatient_monthly_record'
    
    isExist = os.path.exists(path_save)
    if not isExist:
       # Create a new directory because it does not exist
       os.makedirs(path_save)
       print("The new directory is created!")
     
    ################################################################################ 
    ##4. Load ID source
    ################################################################################ 
    file_name = "All_ID_Source_prediction_Months.csv"
    completeName = os.path.join(path_ID, file_name)
    ID_Sources_data = pd.read_csv(completeName, header=0, dtype='int')    
    ##Test
    #ID_Sources_data = ID_Sources_data[(ID_Sources_data['Kcr_ID']==42) | (ID_Sources_data['Kcr_ID']==110)]            
    analysis_IDs = ID_Sources_data['Kcr_ID']   
     
    for i in range(len(analysis_IDs)):
        curr_id = analysis_IDs.iloc[i]
        #print(curr_id)   
        #per month df
        file_name = "ID" + str(curr_id) + "_perMonth_Data.xlsx"
        completeName = os.path.join(path_csv, file_name)
        curr_file = pd.read_excel(completeName,header=0, index_col=False)   
        
        curr_final = curr_file.drop(["study_id" , "Month_Start","Month_End"], axis=1)
        
        curr_columns = pd.DataFrame(list(curr_final))
        curr_columns.columns = ['Unique_code']
        
        if len(curr_columns) >0:
            #print('yes')
            file_name = "ID" + str(curr_id) + "_UniqueCodes.xlsx"
            completeName = os.path.join(path_save, file_name)
            curr_columns.to_excel(completeName, header = True, index=False)
        else:
            print("Remove patients: ", curr_id)
        
    print('10A UniqueCodes done')   
        
    ###get all enrolled month
    file_name = "5b_prediction_Months.csv"  #5_enrollment_Months
    completeName = os.path.join(path_all_enrollmon, file_name)
    enrolled_month_all = pd.read_csv(completeName, header=0) 
    
    isExist = os.path.exists(path_save_new_csv)
    if not isExist:
       # Create a new directory because it does not exist
       os.makedirs(path_save_new_csv)
       print("The new directory is created!")
       
    ##### per patients
    xlsx_files = glob.glob(os.path.join(path_csv, "*.xlsx"))
    #xlsx_files ='D:\R\Cancer_test\python_test_12_22\data_12_7\ID1024_Month_CCS_DIAG_Feature.xlsx'
    for f in xlsx_files:
        #print(f)
        data_ori = pd.read_excel(f,header=0, index_col=False)
        curr_id = f.split("ID")[1]
        curr_id = curr_id.split("_")[0]
        #print(curr_id)
        if int(curr_id) in analysis_IDs.values:
            #print('Yes')
            curr_file = enrolled_month_all.loc[enrolled_month_all['study_id'] == int(curr_id)].reset_index(drop=True)
            curr_file.columns = ['study_id', "Month_Start"]
            curr_df = pd.merge(curr_file, data_ori, on="Month_Start", how="left")
            curr_df = curr_df.drop(['study_id_y'], axis=1)
            curr_df = curr_df.rename(columns={'study_id_x': 'study_id'})
            
            start_date = pd.DataFrame(curr_df['Month_Start'].values.reshape(curr_df.shape[0],1))
            end_date = get_end_date(start_date)
            curr_df["Month_End"] = end_date
            curr_df = curr_df.fillna(0)
            #####save the per month csv file with matched enroll month with kcr Enrollment file
            file_name = "ID" + curr_id+"_"+"perMonth_Data.xlsx"
            completeName = os.path.join(path_save_new_csv, file_name)
            curr_df.to_excel(completeName, header = True, index=False)
            
    
    print('10A per patients done')    
    
    
    
            