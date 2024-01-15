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

def Step11D_Get_ModelReady_Combed_Features(user_name, path_output):

   ### HPC
   path_csv1 = str(path_output) + "/" +str(user_name) + '/11A_ModelReady_GrpFeature_CCSandVAL2ND'
   path_csv2 = str(path_output) + "/" +str(user_name) + '/11B_ModelReady_CharFeature'
   path_csv3 = str(path_output) + "/" +str(user_name) + '/11C_ModelReady_TransformFeatures_CCSandVAL2nd'
   path_save = str(path_output) + "/" +str(user_name) + '/11D_ModelReady_CombFatures_CCSandVAL2nd'
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
       completeName = os.path.join(path_csv1, file_name)
       curr_feat_df = pd.read_excel(completeName,header=0, index_col=False)
       curr_feat_df = curr_feat_df.fillna(0)
       
       file_name = "ID" + str(curr_id) + "_MonthChar.xlsx"
       completeName = os.path.join(path_csv2, file_name)
       curr_charf_df = pd.read_excel(completeName,header=0, index_col=False)
       curr_charf_df = curr_charf_df.fillna(0)
       
       file_name = "ID" + str(curr_id) + "_Transf_Features.xlsx"
       completeName = os.path.join(path_csv3, file_name)
       curr_transf_df = pd.read_excel(completeName,header=0, index_col=False)
       curr_transf_df = curr_transf_df.fillna(0)
       
       curr_feat_df_keep = curr_feat_df.iloc[:,2:]
       curr_charf_df_keep = curr_charf_df.iloc[:,1:]
       curr_transf_df_keep = curr_transf_df.iloc[:,2:]
       
       df_id = pd.DataFrame(np.zeros((curr_feat_df_keep.shape[0],1)))
       df_id.columns = ['sample_id']
       df_id['sample_id'] = 'NA'
       curr_id_df = curr_feat_df.iloc[:,0:2]
       curr_id_df  = curr_id_df.astype('str')
       df_id["sample_id"] = curr_id_df[["study_id", "Month_Start"]].apply("@".join, axis=1)
       
       frames = [df_id, curr_charf_df_keep, curr_feat_df_keep, curr_transf_df_keep]
       curr_all_df = pd.concat(frames,axis=1)
       
   
       file_name = "ID" + str(curr_id) + "_Comb_Features.xlsx"
       completeName = os.path.join(path_save, file_name)
       curr_all_df.to_excel(completeName, header = True, index=False) 
       
   
   print('Step 11D done')
   
