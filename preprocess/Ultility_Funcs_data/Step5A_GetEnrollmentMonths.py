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


def Step5A_GetEnrollmentMonths(user_name, path_input, path_output, mecaidEnroll, month_len_medicaid, start_medicaid, mecareEnroll, month_len_medicare, start_medicare):
    path_csv = str(path_input) #r'/users/qqi227/Manual_Reviewed_Cases/Input_Manual_Reviewed_Cases'
    path_save = str(path_output) + "/" +str(user_name) + '/5_Enrollment_And_Prediction_Months'
    
    isExist = os.path.exists(path_save)
    if not isExist:
       # Create a new directory because it does not exist
       os.makedirs(path_save)
       print("The new directory is created!")
       
       
    #########################################################################################################
    #I. Get Medicaid 
    #mon1-mon240 (from 1/2000-12/2019)
    #########################################################################################################
    file_name = str(mecaidEnroll) #"medicaid_breast_enroll_new.csv"
    completeName = os.path.join(path_csv, file_name)
    medicaid_enrollment_df = pd.read_csv(completeName, header=0, dtype='string')
    month_len_medicaid = int(month_len_medicaid)
    #1. Get Month Columns
    month_col_names = ['mon{}'.format(j) for j in range(1, month_len_medicaid+1)] 
    month_col_indexes  = [medicaid_enrollment_df.columns.get_loc(c) for c in month_col_names if c in medicaid_enrollment_df]
    #2. Convert Month column names from mon1-mon240 to (1/2000-12/2019)
    dates = get_enroll_mon_list(start_medicaid, month_len_medicaid)
    new_col_name = ["study_id", "id_medicaid"] + dates
    medicaid_enrollment_df.columns = new_col_name
    #3. remove all NA rows (All Month columns)
    medicaid_enrollment_df = medicaid_enrollment_df.dropna(axis=0)
    #4. Get IDs
    Medicaid_IDs = medicaid_enrollment_df["study_id"].unique()
    len(Medicaid_IDs) #13902
    
    #########################################################################################################
    #II. Get Medicare 
    #Mon1-Mon324 (1/1991-12/2017)
    #GHO1-GHO324 (HMO enrollment indicator)
    #########################################################################################################
    file_name = str(mecareEnroll) #"medicare_breast_enroll_new.csv"
    completeName = os.path.join(path_csv, file_name)
    Medicare_enrollment_df = pd.read_csv(completeName, header=0, dtype='string')
    month_len_medicare = int(month_len_medicare)
    #1. Remove GHO cols
    Medicare_enrollment_df = Medicare_enrollment_df.drop(Medicare_enrollment_df.filter(like='GHO',axis=1).columns, axis=1)
    
    #2.reorder ID column to be the 1st
    #first_column = Medicare_enrollment_df.pop('study_id')
    #Medicare_enrollment_df.insert(0, 'study_id', first_column)
    
    #3. Get Month Columns
    month_col_names = ['mon{}'.format(j) for j in range(1, month_len_medicare+1)] 
    month_col_indexes  = [Medicare_enrollment_df.columns.get_loc(c) for c in month_col_names if c in Medicare_enrollment_df]
    dates = get_enroll_mon_list(start_medicare, month_len_medicare)  #1991-01-01 may need a input variable Mon1-Mon252 (1/1999-12/2019)
    new_col_name = ["study_id"] + dates
    Medicare_enrollment_df.columns = new_col_name
    #3. remove all NA rows (All Month columns)
    Medicare_enrollment_df = Medicare_enrollment_df.dropna(axis=0)
    #6. Get IDs
    Medicare_IDs = Medicare_enrollment_df["study_id"].unique()
    len(Medicare_IDs) #33446
    
    #########################################################################################################
    #1. Get Enrollment month  (the month date where enrollment = 1)
    #########################################################################################################
    analysis_Ids = np.unique(np.concatenate((Medicaid_IDs, Medicare_IDs),axis=0)).astype(int) #37469
    analysis_Ids.sort()
    enrollment_months_list = []
    
    for i in range(len(analysis_Ids)): #[0:7] [0:150]
        curr_id = analysis_Ids[i]
        #print(curr_id)
        medicaid_idx = medicaid_enrollment_df[medicaid_enrollment_df['study_id'] == str(curr_id)]
        medicare_idx = Medicare_enrollment_df[Medicare_enrollment_df['study_id'] == str(curr_id)]
        
        #Medicaid enrollment
        if len(medicaid_idx) >0:
            curr_medicaid_enroll_df = medicaid_idx.iloc[:,2:month_len_medicaid+2]        
            enroll_idx1 = curr_medicaid_enroll_df.columns[(curr_medicaid_enroll_df == str(1)).iloc[0]]
            if len(enroll_idx1) >0:
                curr_enroll_month1 = enroll_idx1
            else:
                curr_enroll_month1 = []
        else:
            curr_enroll_month1 = []
            
        #Medicare enrollment
        if len(medicare_idx) >0:
            curr_medicare_enroll_df = medicare_idx.iloc[:,1:month_len_medicare+1]        
            enroll_idx2 = curr_medicare_enroll_df.columns[(curr_medicare_enroll_df != str(0)).iloc[0]]
            if len(enroll_idx2) >0:
                #print("Yes")
                #print(curr_id)
                curr_enroll_month2 = enroll_idx2
            else:
                curr_enroll_month2 = []
        else:
            curr_enroll_month2 = []
            
        if len(curr_enroll_month1) >0 and len(curr_enroll_month2) >0:
            curr_all_enroll_months =  curr_enroll_month1.union(curr_enroll_month2)
        elif len(curr_enroll_month1) >0 and len(curr_enroll_month2) ==0:
            curr_all_enroll_months = curr_enroll_month1
        elif len(curr_enroll_month1) ==0 and len(curr_enroll_month2) >0:
            curr_all_enroll_months = curr_enroll_month2
        else:
            curr_all_enroll_months = []
        
        if len(curr_all_enroll_months)>0:
            id_list = pd.DataFrame(np.repeat(curr_id, len(curr_all_enroll_months))).reset_index(drop=True)
            enroll_mon = curr_all_enroll_months.to_frame().reset_index(drop=True)
            frames = [id_list, enroll_mon]       
            result = pd.concat(frames,axis=1)
            result.columns = ['study_id', 'Enrolled_Month']
            
            enrollment_months_list.append(result)
            
                
    all_enrollment_months_df = pd.concat(enrollment_months_list,axis=0, ignore_index=True)       
    
    ####Too large for xlsx file
    #file_name = "5_enrollment_Months.xlsx"
    #completeName = os.path.join(path_save, file_name)
    #all_enrollment_months_df.to_excel(completeName, header = True, index=False)
    
    file_name = "5_enrollment_Months.csv"
    completeName = os.path.join(path_save, file_name)
    all_enrollment_months_df.to_csv(completeName, index=False)
    
    print("Step 5A done")
    """
    ###Test
    a = pd.read_csv(completeName, header=0)
    #b = a.iloc[0:10,:]
    
    
    # selecting rows based on condition
    rslt_df = all_enrollment_months_df.loc[(all_enrollment_months_df['study_id'] == 42) | (all_enrollment_months_df['study_id'] == 110)]
    file_name = "test.csv"
    completeName = os.path.join(path_save, file_name)
    rslt_df.to_csv(completeName, index=False)
    """
    
def Step5A_GetEnrollmentMonths1(user_name, path_input, path_output, mecareEnroll, month_len_medicare, start_medicare):
    path_csv = str(path_input) #r'/users/qqi227/Manual_Reviewed_Cases/Input_Manual_Reviewed_Cases'
    path_save = str(path_output) + "/" +str(user_name) + '/5_Enrollment_And_Prediction_Months'
    
    isExist = os.path.exists(path_save)
    if not isExist:
       # Create a new directory because it does not exist
       os.makedirs(path_save)
       print("The new directory is created!")
       
    
    #########################################################################################################
    #II. Get Medicare 
    #Mon1-Mon324 (1/1991-12/2017)
    #GHO1-GHO324 (HMO enrollment indicator)
    #########################################################################################################
    file_name = str(mecareEnroll) #"medicare_breast_enroll_new.csv"
    completeName = os.path.join(path_csv, file_name)
    Medicare_enrollment_df = pd.read_csv(completeName, header=0, dtype='string')
    month_len_medicare = int(month_len_medicare)
    #1. Remove GHO cols
    Medicare_enrollment_df = Medicare_enrollment_df.drop(Medicare_enrollment_df.filter(like='GHO',axis=1).columns, axis=1)
    
    #2.reorder ID column to be the 1st
    #first_column = Medicare_enrollment_df.pop('study_id')
    #Medicare_enrollment_df.insert(0, 'study_id', first_column)
    
    #3. Get Month Columns
    month_col_names = ['mon{}'.format(j) for j in range(1, month_len_medicare+1)] 
    month_col_indexes  = [Medicare_enrollment_df.columns.get_loc(c) for c in month_col_names if c in Medicare_enrollment_df]
    dates = get_enroll_mon_list(start_medicare, month_len_medicare)  #1991-01-01 may need a input variable Mon1-Mon252 (1/1999-12/2019)
    new_col_name = ["study_id"] + dates
    Medicare_enrollment_df.columns = new_col_name
    #3. remove all NA rows (All Month columns)
    Medicare_enrollment_df = Medicare_enrollment_df.dropna(axis=0)
    #6. Get IDs
    Medicare_IDs = Medicare_enrollment_df["study_id"].unique()
    len(Medicare_IDs) #33446
    
    #########################################################################################################
    #1. Get Enrollment month  (the month date where enrollment = 1)
    #########################################################################################################
    analysis_Ids = np.unique(Medicare_IDs).astype(int) #37469
    analysis_Ids.sort()
    enrollment_months_list = []
    
    for i in range(len(analysis_Ids)): #[0:7] [0:150]
        curr_id = analysis_Ids[i]
        #print(curr_id)
        #medicaid_idx = medicaid_enrollment_df[medicaid_enrollment_df['study_id'] == str(curr_id)]
        medicare_idx = Medicare_enrollment_df[Medicare_enrollment_df['study_id'] == str(curr_id)]
        
        #Medicaid enrollment
            
        #Medicare enrollment
        if len(medicare_idx) >0:
            curr_medicare_enroll_df = medicare_idx.iloc[:,1:month_len_medicare+1]        
            enroll_idx2 = curr_medicare_enroll_df.columns[(curr_medicare_enroll_df != str(0)).iloc[0]]
            if len(enroll_idx2) >0:
                #print("Yes")
                #print(curr_id)
                curr_enroll_month2 = enroll_idx2
            else:
                curr_enroll_month2 = []
        else:
            curr_enroll_month2 = []
            

        curr_all_enroll_months = curr_enroll_month2
        
        if len(curr_all_enroll_months)>0:
            id_list = pd.DataFrame(np.repeat(curr_id, len(curr_all_enroll_months))).reset_index(drop=True)
            enroll_mon = curr_all_enroll_months.to_frame().reset_index(drop=True)
            frames = [id_list, enroll_mon]       
            result = pd.concat(frames,axis=1)
            result.columns = ['study_id', 'Enrolled_Month']
            
            enrollment_months_list.append(result)
            
                
    all_enrollment_months_df = pd.concat(enrollment_months_list,axis=0, ignore_index=True)       
    
    ####Too large for xlsx file
    #file_name = "5_enrollment_Months.xlsx"
    #completeName = os.path.join(path_save, file_name)
    #all_enrollment_months_df.to_excel(completeName, header = True, index=False)
    
    file_name = "5_enrollment_Months.csv"
    completeName = os.path.join(path_save, file_name)
    all_enrollment_months_df.to_csv(completeName, index=False)
    
    print("Step 5A only Medicare done done")


def Step5A_GetEnrollmentMonths2(user_name, path_input, path_output, mecaidEnroll, month_len_medicaid, start_medicaid):
    path_csv = str(path_input) #r'/users/qqi227/Manual_Reviewed_Cases/Input_Manual_Reviewed_Cases'
    path_save = str(path_output) + "/" +str(user_name) + '/5_Enrollment_And_Prediction_Months'
    
    isExist = os.path.exists(path_save)
    if not isExist:
       # Create a new directory because it does not exist
       os.makedirs(path_save)
       print("The new directory is created!")
       
       
    #########################################################################################################
    #I. Get Medicaid 
    #mon1-mon240 (from 1/2000-12/2019)
    #########################################################################################################
    file_name = str(mecaidEnroll) #"medicaid_breast_enroll_new.csv"
    completeName = os.path.join(path_csv, file_name)
    medicaid_enrollment_df = pd.read_csv(completeName, header=0, dtype='string')
    month_len_medicaid = int(month_len_medicaid)
    #1. Get Month Columns
    month_col_names = ['mon{}'.format(j) for j in range(1, month_len_medicaid+1)] 
    month_col_indexes  = [medicaid_enrollment_df.columns.get_loc(c) for c in month_col_names if c in medicaid_enrollment_df]
    #2. Convert Month column names from mon1-mon240 to (1/2000-12/2019)
    dates = get_enroll_mon_list(start_medicaid, month_len_medicaid)
    new_col_name = ["study_id", "id_medicaid"] + dates
    medicaid_enrollment_df.columns = new_col_name
    #3. remove all NA rows (All Month columns)
    medicaid_enrollment_df = medicaid_enrollment_df.dropna(axis=0)
    #4. Get IDs
    Medicaid_IDs = medicaid_enrollment_df["study_id"].unique()
    len(Medicaid_IDs) #13902
    
    #########################################################################################################
    #II. Get Medicare 
    #Mon1-Mon324 (1/1991-12/2017)
    #GHO1-GHO324 (HMO enrollment indicator)
    #########################################################################################################

    
    #########################################################################################################
    #1. Get Enrollment month  (the month date where enrollment = 1)
    #########################################################################################################
    analysis_Ids = np.unique(Medicaid_IDs).astype(int) #37469
    analysis_Ids.sort()
    enrollment_months_list = []
    
    for i in range(len(analysis_Ids)): #[0:7] [0:150]
        curr_id = analysis_Ids[i]
        #print(curr_id)
        medicaid_idx = medicaid_enrollment_df[medicaid_enrollment_df['study_id'] == str(curr_id)]
        #medicare_idx = Medicare_enrollment_df[Medicare_enrollment_df['study_id'] == str(curr_id)]
        
        #Medicaid enrollment
        if len(medicaid_idx) >0:
            curr_medicaid_enroll_df = medicaid_idx.iloc[:,2:month_len_medicaid+2]        
            enroll_idx1 = curr_medicaid_enroll_df.columns[(curr_medicaid_enroll_df == str(1)).iloc[0]]
            if len(enroll_idx1) >0:
                curr_enroll_month1 = enroll_idx1
            else:
                curr_enroll_month1 = []
        else:
            curr_enroll_month1 = []
            
        #Medicare enrollment

        curr_all_enroll_months = curr_enroll_month1
        
        if len(curr_all_enroll_months)>0:
            id_list = pd.DataFrame(np.repeat(curr_id, len(curr_all_enroll_months))).reset_index(drop=True)
            enroll_mon = curr_all_enroll_months.to_frame().reset_index(drop=True)
            frames = [id_list, enroll_mon]       
            result = pd.concat(frames,axis=1)
            result.columns = ['study_id', 'Enrolled_Month']
            
            enrollment_months_list.append(result)
            
                
    all_enrollment_months_df = pd.concat(enrollment_months_list,axis=0, ignore_index=True)       
    
    ####Too large for xlsx file
    #file_name = "5_enrollment_Months.xlsx"
    #completeName = os.path.join(path_save, file_name)
    #all_enrollment_months_df.to_excel(completeName, header = True, index=False)
    
    file_name = "5_enrollment_Months.csv"
    completeName = os.path.join(path_save, file_name)
    all_enrollment_months_df.to_csv(completeName, index=False)
    
    print("Step 5A only Medicaid done")
