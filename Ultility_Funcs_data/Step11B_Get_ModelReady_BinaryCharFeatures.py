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

def Step11B_Get_ModelReady_BinaryCharFeatures(user_name, path_output):

   ###HPC
   path_csv = str(path_output) + "/" +str(user_name) + '/8_Characteristics2/Month_Level'
   path_save = str(path_output) + "/" +str(user_name) + '/11B_ModelReady_CharFeature'
   path_ID = str(path_output) + "/" +str(user_name) + '/1_ID_Sources_Info'
   #path_site = r'/Users/qiqiao/Desktop/dp/Rewrite'
        
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
   ##Test
   #ID_Sources_data = ID_Sources_data[(ID_Sources_data['Kcr_ID']==42) | (ID_Sources_data['Kcr_ID']==110)]            
   analysis_IDs = ID_Sources_data['Kcr_ID']  
   
   ########################################################################################################################
   #1.Combine all pts binary char
   #2. Select features
   #3. Recode feature to binary columns 
   #'@Updated 10/05 added surg_prim_site_V1
   #'@Updated 10/05 added enrolled year
   ##'@updated 11/11: added "DAJCC_T" ,"DAJCC_M","DAJCC_N" 
   ##''@TODO ADD num_claims later
   ########################################################################################################################
   selected_charfeatures = ["Enrolled_year","Age","months_since_dx","Race" , "Site" , "Stage","Grade",
                               "Laterality" ,"er_stat","pr_stat",   "her2_stat",    
                               "surg_prim_site_V1",
                               "DAJCC_T" ,"DAJCC_M","DAJCC_N",
                               "reg_age_at_dx", "reg_nodes_exam", 
                               "reg_nodes_pos", "cs_tum_size", "cs_tum_ext", 
                               "cs_tum_nodes", "regional"]#, 'y_PRE_OR_POST_2ndEvent'] #y_PRE_OR_POST_2ndEvent_ExcludedDeath

                               
   other_cols = ["Enrolled_Month"]
   
   col_toconvert = ["Race","Site","Stage","Grade","Laterality","er_stat","pr_stat","her2_stat",
                      "surg_prim_site_V1"] #note regional does not need to be convert cuz it is 0 or 1
   
   #keep_feat = other_cols + selected_charfeatures
   
   frames = []
   for i in range(len(analysis_IDs)):
       curr_id = analysis_IDs.iloc[i]
       file_name = "ID" + str(curr_id) + "_MonthChar.xlsx"
       completeName = os.path.join(path_csv, file_name)
       curr_df = pd.read_excel(completeName,header=0, index_col=False)
       curr_df = curr_df.fillna(0)
       curr_df = curr_df[selected_charfeatures]
       curr_df['study_id'] = int(curr_id)
       first_column = curr_df.pop('study_id')
       curr_df.insert(0, 'study_id', first_column)
       frames.append(curr_df)
           
   all_pt_char_df = pd.concat(frames,axis=0, ignore_index=True)    
   all_pt_char_df_change = all_pt_char_df[col_toconvert] 
   ####### get dummies 
   all_pt_char_df_binary_ori = pd.get_dummies(all_pt_char_df_change.astype(str), dtype=float)
   #check columns
   frames_keep =[]
   for mmm in range(len(col_toconvert)):
     curr_col = col_toconvert[mmm]
     spike_cols = [col for col in all_pt_char_df_binary_ori.columns if curr_col in col]
     curr_df = all_pt_char_df_binary_ori[spike_cols] 
     if curr_col == 'Race':
        if 'Race_1' not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['Race_1']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "Race_2" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['Race_2']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "Race_3" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['Race_3']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        curr_df = curr_df[['Race_1', 'Race_2', 'Race_3']] 
        frames_keep.append(curr_df)

     if curr_col == 'Site':
        if 'SiteC500' not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['SiteC500']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "SiteC501" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['SiteC501']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "SiteC502" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['SiteC502']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "SiteC503" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['SiteC503']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "SiteC504" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['SiteC504']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "SiteC505" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['SiteC505']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "SiteC506" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['SiteC506']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "SiteC507" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['SiteC507']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "SiteC508" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['SiteC508']
           curr_df = pd.concat([curr_df, df_add],axis=1)            
        if "SiteC509" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['SiteC509']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        curr_df = curr_df[['SiteC501', "SiteC502", 'SiteC503', 'SiteC504', 'SiteC505', 'SiteC506', 'SiteC507','SiteC508', 'SiteC509']] 
        frames_keep.append(curr_df)
     
     if curr_col == 'Stage':
        if 'Stage_0.0' not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['Stage_0.0']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "Stage_1.0" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['Stage_1.0']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "Stage_2.0" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['Stage_2.0']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "Stage_3.0" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['Stage_3.0']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "Stage_4.0" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['Stage_4.0']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        curr_df = curr_df[["Stage_1.0", 'Stage_2.0', 'Stage_3.0']] 
        frames_keep.append(curr_df)

     if curr_col == 'Grade':
        if 'Grade_1' not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['Grade_1']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "Grade_2" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['Grade_2']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "Grade_3" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['Grade_3']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "Grade_4" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['Grade_4']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "Grade_9" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['Grade_9']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        curr_df = curr_df[['Grade_1', "Grade_2", 'Grade_3', 'Grade_4', 'Grade_9']] 
        frames_keep.append(curr_df)

     if curr_col == 'Laterality':
        if 'Laterality_1' not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['Laterality_1']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "Laterality_2" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['Laterality_2']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "Laterality_3" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['Laterality_3']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "Laterality_4" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['Laterality_4']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "Laterality_9" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['Laterality_9']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        curr_df = curr_df[['Laterality_1', "Laterality_2", 'Laterality_3', 'Laterality_4', 'Laterality_9']] 
        frames_keep.append(curr_df)

     if curr_col == 'er_stat':
        if 'er_stat_0' not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['er_stat_0']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "er_stat_1" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['er_stat_1']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "er_stat_9" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['er_stat_9']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        curr_df = curr_df[['er_stat_0', 'er_stat_1', 'er_stat_9']] 
        frames_keep.append(curr_df)         

     if curr_col == 'pr_stat':
        if 'pr_stat_0' not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['pr_stat_0']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "pr_stat_1" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['pr_stat_1']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "pr_stat_9" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['pr_stat_9']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        curr_df = curr_df[['pr_stat_0', 'pr_stat_1', 'pr_stat_9']] 
        frames_keep.append(curr_df)  

     if curr_col == 'her2_stat':
        if 'her2_stat_0' not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['her2_stat_0']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "her2_stat_1" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['her2_stat_1']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "her2_stat_9" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['her2_stat_9']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        curr_df = curr_df[['her2_stat_0', 'her2_stat_1', 'her2_stat_9']] 
        frames_keep.append(curr_df)      

     if curr_col == 'surg_prim_site_V1':
        if 'surg_prim_site_V1_0.0' not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['surg_prim_site_V1_0.0']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "surg_prim_site_V1_20.0" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['surg_prim_site_V1_20.0']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "surg_prim_site_V1_30.0" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['surg_prim_site_V1_30.0']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "surg_prim_site_V1_40.0" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['surg_prim_site_V1_40.0']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "surg_prim_site_V1_50.0" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['surg_prim_site_V1_50.0']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "surg_prim_site_V1_60.0" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['surg_prim_site_V1_60.0']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "surg_prim_site_V1_70.0" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['surg_prim_site_V1_70.0']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "surg_prim_site_V1_80.0" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['surg_prim_site_V1_80.0']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "surg_prim_site_V1_90.0" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['surg_prim_site_V1_90.0']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "surg_prim_site_V1_99.0" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['surg_prim_site_V1_99.0']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        if "surg_prim_site_V1_NA" not in spike_cols:
           df_add = pd.DataFrame(np.zeros((all_pt_char_df_binary_ori.shape[0], 1),dtype=int))
           df_add.columns= ['surg_prim_site_V1_NA']
           curr_df = pd.concat([curr_df, df_add],axis=1)
        curr_df = curr_df[['surg_prim_site_V1_0.0', 'surg_prim_site_V1_20.0', 'surg_prim_site_V1_30.0', 'surg_prim_site_V1_40.0', 'surg_prim_site_V1_50.0', 'surg_prim_site_V1_60.0', 'surg_prim_site_V1_70.0', 'surg_prim_site_V1_80.0', 'surg_prim_site_V1_90.0', 'surg_prim_site_V1_99.0','surg_prim_site_V1_NA']] 
        frames_keep.append(curr_df) 
   all_pt_char_df_binary = pd.concat(frames_keep, axis=1)     
   all_pt_char_df_keep = all_pt_char_df.drop(columns = col_toconvert)  
   frames = [all_pt_char_df_keep, all_pt_char_df_binary] 
   all_binary_char_df = pd.concat(frames,axis=1)#, ignore_index=True) 
   
   
   for i in range(len(analysis_IDs)):
       curr_id = analysis_IDs.iloc[i]
       curr_df = all_binary_char_df.loc[all_binary_char_df['study_id'] == int(curr_id)]
       file_name = "ID" + str(curr_id) + "_MonthChar.xlsx"
       completeName = os.path.join(path_save, file_name)
       curr_df.to_excel(completeName, header = True, index=False)
   
   print('Step 11B new done')
     



