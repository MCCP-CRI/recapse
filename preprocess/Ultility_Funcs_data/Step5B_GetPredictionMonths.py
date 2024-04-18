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


def Step5B_GetPredictionMonths(user_name, path_input, path_output, metacsv):
    ###Mac Air
    path_csv = str(path_input) #r'/users/qqi227/Manual_Reviewed_Cases/Input_Manual_Reviewed_Cases'
    path_save = str(path_output) + "/" +str(user_name) + '/5_Enrollment_And_Prediction_Months'
    path_ID = str(path_output) + "/" +str(user_name) + '/1_ID_Sources_Info'
    
    isExist = os.path.exists(path_save)
    if not isExist:
       # Create a new directory because it does not exist
       os.makedirs(path_save)
       print("The new directory is created!")
       
    
    #########################################################################################################
    #I. Get all enrolled months
    #
    #########################################################################################################
    file_name = "5_enrollment_Months.csv"
    completeName = os.path.join(path_save, file_name)
    all_enrollment_months_df = pd.read_csv(completeName, header=0, dtype='string')
    #kcr_ID = all_enrollment_months_df["study_id"].unique() 
    
    #######################################################################################
    #II. Get all date in kcr 
    #######################################################################################
    file_name = str(metacsv) #"UH3_KCRnewreviewedcases.csv"
    completeName = os.path.join(path_csv, file_name)
    kcr_df = pd.read_csv(completeName, header=0, dtype='string')
    #kcr_ID = kcr_df["study_id"].unique() #47130 #study_id
    
    
    ################################################################################ 
    ##III. Load ID source
    ################################################################################ 
    file_name = "All_ID_Source.csv"
    completeName = os.path.join(path_ID, file_name)
    ID_Sources_data = pd.read_csv(completeName, header=0, dtype='int')    
    ##Test
    #ID_Sources_data = ID_Sources_data[(ID_Sources_data['Kcr_ID']==42) | (ID_Sources_data['Kcr_ID']==110)]            
    analysis_IDs = ID_Sources_data['Kcr_ID'] 
    
    frames = []
    ID_to_drop = []
    for i in range(len(analysis_IDs)): #len(analysis_IDs)
        curr_id = analysis_IDs.iloc[i]
        curr_enroll_month = all_enrollment_months_df.loc[all_enrollment_months_df['study_id'] == str(curr_id)]#.reset_index(drop=True)
        curr_kcr_df = kcr_df.loc[kcr_df['study_id'] == str(curr_id)]#.reset_index(drop=True)
        #####################################################
        #date1 = "2021-06-15"
        #date2 = "2021-06-20"
        #
        #if date1 < date2:
        #    print("date1 comes before date2")
        #elif date1 > date2:
        #    print("date1 comes after date2")
        #else:
        #    print("date1 and date2 are the same")
        #####################################################    
        curr_Date_dx = change_y_m_d2(curr_kcr_df.loc[curr_kcr_df.index[0],"Date_dx"])
        cutoff_date = add_months_to_date(curr_Date_dx, 6)
        keep_curr_enroll_month = curr_enroll_month.loc[curr_enroll_month['Enrolled_Month'] >= cutoff_date]
        #keep_curr_enroll_month['Date_dx'] = curr_Date_dx
        if keep_curr_enroll_month.shape[0] >0:
            frames.append(keep_curr_enroll_month)
        else:
            print("Patient does not have enough record: ", "ID is ", curr_id)
            ID_to_drop.append(int(curr_id))
    
    
    
    final_all_enrollment_months_df = pd.concat(frames,axis=0, ignore_index=True) 
    file_name = "5b_prediction_Months.csv"
    completeName = os.path.join(path_save, file_name)
    final_all_enrollment_months_df.to_csv(completeName, index=False)
    
    ###
    #final_ID_Sources_data = ID_Sources_data.drop(ID_Sources_data[ID_Sources_data.Kcr_ID.isin(ID_to_drop)].index, axis = 0, inplace = True)
    ID_Sources_data.drop(ID_Sources_data[ID_Sources_data.Kcr_ID.isin(ID_to_drop)].index, axis = 0, inplace = True)
    file_name = "All_ID_Source_prediction_Months.csv"
    completeName = os.path.join(path_ID, file_name)
    ID_Sources_data.to_csv(completeName, index=False)
    
    print("Step 5B done, new All_ID_Source_prediction_Months.csv file generated")
    
