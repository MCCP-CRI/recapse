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

def Step11C_Get_ModelReady_TransformationFeature(user_name, path_output, drug_code):

    ###HPC
    #path_csv = r'/users/qqi227/Manual_Reviewed_Cases/Results/11A_ModelReady_GrpFeature_CCSandDM3SPE'
    if drug_code == "VAL_2ND":
        path_csv = str(path_output) + "/" +str(user_name) + '/11A_ModelReady_GrpFeature_CCSandVAL2ND'
        path_save = str(path_output) + "/" +str(user_name) + '/11C_ModelReady_TransformFeatures_CCSandVAL2nd'
    else:
        path_csv = str(path_output) + "/" +str(user_name) + '/11A_ModelReady_GrpFeature_CCSandDM3SPE'
        path_save = str(path_output) + "/" +str(user_name) + '/11C_ModelReady_TransformFeatures_CCSandDM3SPE'
    path_ID = str(path_output) + "/" +str(user_name) + '/1_ID_Sources_Info'
         
    isExist = os.path.exists(path_save)
    if not isExist:
       # Create a new directory because it does not exist
       os.makedirs(path_save)
       print("The new directory is created!")
       
    
    
        
    ################################################################################ 
    ##1. Load ID source
    ################################################################################ 
    file_name = "All_ID_Source_prediction_Months.csv"
    completeName = os.path.join(path_ID, file_name)
    ID_Sources_data = pd.read_csv(completeName, header=0, dtype='int')    
    ###Test
    #ID_Sources_data = ID_Sources_data[(ID_Sources_data['Kcr_ID']==42) | (ID_Sources_data['Kcr_ID']==110)]            
    analysis_IDs = ID_Sources_data['Kcr_ID']
    
    for i in range(len(analysis_IDs)): #
        curr_id = analysis_IDs.iloc[i]
        file_name = "ID" + str(curr_id) + "_Selected_Grp_Features.xlsx"
        completeName = os.path.join(path_csv, file_name)
        curr_df = pd.read_excel(completeName,header=0, index_col=False)
        curr_df = curr_df.fillna(0)
    
        #get the month index as the actuall month difference to the first month,  #Use interger as month sequence for easier computation
        #curr_df.dtypes
        month = curr_df["Month_Start"].astype(str)
        #month.dtypes
        curr_df['Month_index'] = "NA"
        curr_df.loc[curr_df.index[0], "Month_index"] = int(0)
        
        if month.shape[0] > 1: 
            for k in range(1, month.shape[0], 1):
                curr_month = month.iloc[0]
                curr_month_1 = month.iloc[k]
                month_gap = get_diff_month_m(curr_month_1, curr_month)
                curr_df.loc[curr_df.index[k], "Month_index"] = int(month_gap)
    
        curr_df['Month_index'] = curr_df['Month_index'].astype('int64')
        
        results_df = apply_code_transforamtion_func(curr_df)
    
        file_name = "ID" + str(curr_id) + "_Transf_Features.xlsx"
        completeName = os.path.join(path_save, file_name)
        results_df.to_excel(completeName, header = True, index=False) 
        
    
    print("Step 11C done")

  