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
from .Recapse_Ultility import *
import datetime


def Step3C_HPC_Get_PerMonthData_withCleanCodes_onlymedicaid(user_name, path_input, path_output, mecaidClaims, mecaidClaims2, drug_code):

    path_ID = str(path_output) + "/" +str(user_name) + '/1_ID_Sources_Info'
    path_save = str(path_output) + "/" +str(user_name) + '/3_Get_PerMonthData_withCleanCodes'
    path_csv_ori = str(path_input) #r'/users/qqi227/Manual_Reviewed_Cases/Input_Manual_Reviewed_Cases'
    
    isExist = os.path.exists(path_save)
    if not isExist:
       # Create a new directory because it does not exist
       os.makedirs(path_save)
       print("The new directory is created!")
    
    #######################
    # drug list
    # NDC_drug_cols2 = ["NDC_CD","PROD_SRVC_ID"] for 0
    # NDC_drug_cols2 = [1,"PROD_SRVC_ID"] for 1
    #######################
    if drug_code == "VAL_2ND":
        flag_NDC_drug_cols2 = 1
    else:
        flag_NDC_drug_cols2 = 0
    
    #######################################################################################
    #Read Medicare
    #######################################################################################
    #file_name = str(mecareClaims) #"medicare_breast_claims_new.csv" "medicare_breast_claims_new.csv"
    #completeName = os.path.join(path_csv_ori, file_name)
    #medicare_df = pd.read_csv(completeName, header=0, dtype='string')
    
    #######################################################################################
    #Read medicaid
    #######################################################################################
    file_name = str(mecaidClaims) #"medicaid_breast_claims_new.csv" "medicaid_breast_claims_new.csv"
    completeName = os.path.join(path_csv_ori, file_name)
    medicaid_health_df = pd.read_csv(completeName, header=0, dtype='string')
    
    file_name = str(mecaidClaims2) #"medicaid_breast_Rxclaims_new.csv" "medicaid_breast_Rxclaims_new.csv"
    completeName = os.path.join(path_csv_ori, file_name)
    medicaid_pharm_df = pd.read_csv(completeName, header=0, dtype='string')
    
    ###### Get all the columns
    medicaid_columns_list_health = list(medicaid_health_df.columns)
    medicaid_columns_list_pharm = list(medicaid_pharm_df.columns)
    #medicare_columns_list = list(medicare_df.columns)
    
    
    #######################################################################################
    #load ID
    #######################################################################################
    file_name = "All_ID_Source.csv"
    completeName = os.path.join(path_ID, file_name)
    ID_df = pd.read_csv(completeName, header=0)#, dtype='string')
    ID_df = ID_df.drop(ID_df[(ID_df["in_Medicare"] == 0) & (ID_df["in_Medicaid"] == 0)].index)
    
    #get analysis ID by source
    analysis_ID = ID_df['Kcr_ID'].unique()
    #analysis_ID.columns = ['Kcr_ID']
    
    ##Use &、|、~ (not and, or, not)
    #medicare_only_ID = pd.DataFrame(ID_df[(ID_df["in_Medicare"] == 1) & (ID_df["in_Medicaid"] == 0)].iloc[:,0])
    #medicaid_only_ID = pd.DataFrame(ID_df[(ID_df["in_Medicare"] == 0) & (ID_df["in_Medicaid"] == 1)].iloc[:,0])
    #both_ID = pd.DataFrame(ID_df[(ID_df["in_Medicare"] == 1) & (ID_df["in_Medicaid"] == 1)].iloc[:,0])
    
    path_medicaid_heath = str(path_output)  + '/' +str(user_name) +  '/2_RawClaims_perPatient/Medicaid_HealthClaims'
    path_medicaid_pharm = str(path_output)  + '/' +str(user_name) + '/2_RawClaims_perPatient/Medicaid_PharmClaims'
    #path_medicare = str(path_output)  + '/' +str(user_name) + '/2_RawClaims_perPatient/Medicare'
    
    
    #analysis_ID=['42', '110']
    
    for i in range(len(analysis_ID)): #len(analysis_ID)
        curr_id = str(int(analysis_ID[i]))
        #print(curr_id)
        data_res = read_allClaims(curr_id, path_medicaid_heath, path_medicaid_pharm, medicaid_columns_list_health, medicaid_columns_list_pharm)
         
        #1. Read all raw claims, if not aval, return NULL
        medicaid_health_df = data_res[0]
        medicaid_pharm_df  = data_res[1]
        #medicare_df        = data_res[2]
        
        ############################################
        # check date
        ############################################
        #if flag == 1:
        #    medicare_df = convert_SAS_Excel_date(medicare_df, 'claims_date')
    
        #2. Clean codes in raw claims
        #2.1 Medicaid Codes columns
        ICD_diag_cols1   =["CDE_DIAG_PRIM","CDE_DIAG_2","CDE_DIAG_3","CDE_DIAG_4"] #ICD 9 or ICD10
        HCPCS_proc_cols1 =["CDE_PROC_PRIM"]                                       #HCPCS
        AHFS_drug_cols1  =["CDE_THERA_CLS_AHFS"]
        NDC_drug_cols1  =["CDE_NDC"]
        
        all_medicaid_health_cols =ICD_diag_cols1 + HCPCS_proc_cols1
        all_medicaid_pharms_cols =AHFS_drug_cols1 + NDC_drug_cols1
        
        ######################################
        # check if all the columns exist
        ######################################
        all_medicaid_health_cols_f = []
        for kkk in range(len(all_medicaid_health_cols)):
            if all_medicaid_health_cols[kkk] in medicaid_columns_list_health:
                all_medicaid_health_cols_f.append(all_medicaid_health_cols[kkk]) 
        all_medicaid_health_cols = all_medicaid_health_cols_f        
         
        all_medicaid_pharms_cols_f = []
        for kkk in range(len(all_medicaid_pharms_cols)):
            if all_medicaid_pharms_cols[kkk] in medicaid_columns_list_pharm:
                all_medicaid_pharms_cols_f.append(all_medicaid_pharms_cols[kkk]) 
        all_medicaid_pharms_cols = all_medicaid_pharms_cols_f
        
        cleaned_medicaid_health_df = clean_codes_inPerPtsData(medicaid_health_df,all_medicaid_health_cols,ICD_diag_cols1,HCPCS_proc_cols1,"","")
        cleaned_medicaid_pharm_df  = clean_codes_inPerPtsData(medicaid_pharm_df,all_medicaid_pharms_cols,"","",NDC_drug_cols1, AHFS_drug_cols1)
        cleaned_medicaid_health_df = change_y_m_d(cleaned_medicaid_health_df, 'medicaid')
        cleaned_medicaid_pharm_df = change_y_m_d(cleaned_medicaid_pharm_df, 'medicaid')
        
        #2.2 Medicare Code cols
    
        
        #2.Get all aval dates
        if not cleaned_medicaid_health_df.empty:
            unique_dates1 = cleaned_medicaid_health_df["DTE_FIRST_SVC"].unique()
        if not cleaned_medicaid_pharm_df.empty:
            unique_dates2 = cleaned_medicaid_pharm_df["DTE_FIRST_SVC"].unique()
        #if not cleaned_medicare_df.empty:
        #    unique_dates3 = cleaned_medicare_df["claims_date"].unique()  
        if cleaned_medicaid_health_df.empty and cleaned_medicaid_pharm_df.empty:
            print("The sample or record that cause the error: ",curr_id)
            raise ValueError("There are samples or records that do not belong to Medicaid or other enrollment, please clean up the metadata file")
            
        
        #if not cleaned_medicaid_health_df.empty and not cleaned_medicaid_pharm_df.empty and not cleaned_medicare_df.empty:
        #    all_unique_dates = np.unique(np.concatenate((unique_dates1,unique_dates2,unique_dates3),axis=0))
        if not cleaned_medicaid_health_df.empty and cleaned_medicaid_pharm_df.empty and cleaned_medicare_df.empty:
            all_unique_dates = np.unique(unique_dates1)
        elif cleaned_medicaid_health_df.empty and not cleaned_medicaid_pharm_df.empty and cleaned_medicare_df.empty:
            all_unique_dates = np.unique(unique_dates2)
        #elif cleaned_medicaid_health_df.empty and cleaned_medicaid_pharm_df.empty and not cleaned_medicare_df.empty:
        #    all_unique_dates = np.unique(unique_dates3)
        elif not cleaned_medicaid_health_df.empty and not cleaned_medicaid_pharm_df.empty and cleaned_medicare_df.empty:
            all_unique_dates = np.unique(np.concatenate((unique_dates1,unique_dates2),axis=0))
        #elif not cleaned_medicaid_health_df.empty and cleaned_medicaid_pharm_df.empty and not cleaned_medicare_df.empty:
        #    all_unique_dates = np.unique(np.concatenate((unique_dates1,unique_dates3),axis=0))
        #elif cleaned_medicaid_health_df.empty and not cleaned_medicaid_pharm_df.empty and not cleaned_medicare_df.empty:
        #    all_unique_dates = np.unique(np.concatenate((unique_dates2,unique_dates3),axis=0))
        #else:
        #    
        
        start_date = pd.DataFrame(list(set([old_date[0]+ '-' +old_date[1] + "-01"  for old_date in [date.split('-') for date in all_unique_dates] ])))
        start_date = start_date.sort_values(0)
        end_date = get_end_date(start_date)
        ### get continus time series
        start = all_unique_dates[0].split('-')[0] + '-' +all_unique_dates[0].split('-')[1] +'-01'
        start_1 = all_unique_dates[-1].split('-')[0] + '-' +all_unique_dates[-1].split('-')[1] +'-01'
        start_date_all = get_date_series(start, start_1)
        end_date_all = get_end_date(start_date_all)
        
        start_date = start_date_all
        end_date   = end_date_all
    
        #5. Get unique code per month
        unique_codes_PerMonth_list = []
        
        for k in range(len(start_date)): #
            mon = start_date.iloc[k,0]
            end = end_date.iloc[k,0] 
            
            curr_month_df1_Health = get_claims_inDateRange(cleaned_medicaid_health_df,"DTE_FIRST_SVC",mon, end)
            curr_month_df1_Pharm  = get_claims_inDateRange(cleaned_medicaid_pharm_df,"DTE_FIRST_SVC",mon, end)
            #curr_month_df2        = get_claims_inDateRange(cleaned_medicare_df,"claims_date",mon, end)
            df_empty = pd.DataFrame()
            curr_unique_ICD_DIAG  = get_uniquecodes_perMonth("DIAG_ICD",curr_month_df1_Health,df_empty,ICD_diag_cols1,[])
            curr_unique_ICD_PROC  = get_uniquecodes_perMonth("PROC_ICD",curr_month_df1_Health,df_empty,[],[])
            curr_unique_HCPC_PROC = get_uniquecodes_perMonth("PROC_HCPCS",curr_month_df1_Health,df_empty,HCPCS_proc_cols1,[])
            curr_unique_NDC_DRUG  = get_uniquecodes_perMonth("DRUG_NDC",curr_month_df1_Pharm,df_empty,NDC_drug_cols1,[])
            curr_unique_AHFS_DRUG = get_uniquecodes_perMonth("DRUG_AHFS",curr_month_df1_Pharm,df_empty,AHFS_drug_cols1,[])
            curr_unique_all_codes = curr_unique_ICD_DIAG + curr_unique_ICD_PROC + curr_unique_HCPC_PROC + curr_unique_NDC_DRUG + curr_unique_AHFS_DRUG
            unique_codes_PerMonth_list.append(curr_unique_all_codes)
            
        #6. unique code all months   
        all_unique_codes = sorted(list(set(unlist(unique_codes_PerMonth_list))))
        
        #7. Unique code per month df (Row: month, Col: one code)
     
        perMonth_df = pd.DataFrame(np.zeros((len(start_date),int(len(all_unique_codes)+3) )))
        perMonth_df.columns = ["study_id","Month_Start","Month_End"] + all_unique_codes
        perMonth_df["study_id"] = int(curr_id)
            
        for k in range(len(start_date_all)):
            perMonth_df.loc[perMonth_df.index[k], "Month_Start"] = str(start_date.iloc[k,0])
            perMonth_df.loc[perMonth_df.index[k], "Month_End"] = str(end_date.iloc[k,0])
            curr_codes = unique_codes_PerMonth_list[k]
            if len(curr_codes) >0 :
                for kk in range(len(curr_codes)):
                    perMonth_df.loc[perMonth_df.index[k], curr_codes[kk]] = int(1)
        
        file_name = "ID" + curr_id+"_"+"perMonth_Data.xlsx"
        completeName = os.path.join(path_save, file_name)
        perMonth_df.to_excel(completeName, header = True, index=False)
    
    
    print("Step 3C only medcaid done")
    
    
