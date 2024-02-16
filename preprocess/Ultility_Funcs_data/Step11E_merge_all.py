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


def Step11E_merge_all(user_name, path_output, drug_code):

   ### HPC
   if drug_code == "VAL_2ND":
      path_csv = str(path_output) + "/" +str(user_name) + '/11D_ModelReady_CombFatures_CCSandVAL2nd'
      path_save = str(path_output) + "/" +str(user_name) + '/11E_merged_All_CCSandVAL2nd'
   else:
      path_csv = str(path_output) + "/" +str(user_name) + '/11D_ModelReady_CombFatures_CCSandDM3SPE'
      path_save = str(path_output) + "/" +str(user_name) + '/11E_merged_All_CCSandDM3SPE'
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
   
   df_append = pd.DataFrame()
   for i in range(len(analysis_IDs)): #
       curr_id = analysis_IDs.iloc[i]
       file_name = "ID" + str(curr_id) + "_Comb_Features.xlsx"
       completeName = os.path.join(path_csv, file_name)
       curr_feat_df = pd.read_excel(completeName,header=0, index_col=False)
   
       #file_name = "ID" + str(curr_id) + "_MonthChar_SBCE.xlsx"
       #completeName = os.path.join(path_label, file_name)
       #curr_label_df = pd.read_excel(completeName,header=0, index_col=False)
   
       #curr_feat_df['y_PRE_OR_POST_2ndEvent'] = curr_label_df[['y_PRE_OR_POST_2ndEvent']]
       curr_feat_df['study_id'] = int(curr_id)
   
       df_append = df_append.append(curr_feat_df, ignore_index=True)
   
   
   #file_name = "All_11E_CCSandVAL2nd.csv"
   #completeName = os.path.join(path_save, file_name)
   #df_append.to_csv(completeName, index=False) 
   if drug_code == "VAL_2ND":
      file_name = "All_11E_CCSandVAL2nd.pkl"
   else:
      file_name = "All_11E_CCSandDM3SPE.pkl"
   completeName = os.path.join(path_save, file_name)
   df_append.to_pickle(completeName)
   
   print("11E done")



   
   
   
   