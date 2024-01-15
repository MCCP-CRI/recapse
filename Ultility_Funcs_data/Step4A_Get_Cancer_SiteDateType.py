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


def Step4A_Get_Cancer_SiteDateType(user_name, path_input, path_output, metacsv):

    ### HPC
    path_csv = str(path_input) #r'/users/qqi227/Manual_Reviewed_Cases/Input_Manual_Reviewed_Cases'
    path_save = str(path_output) + "/" +str(user_name) + '/4_Recurr_Dates_Info'
    path_ID = str(path_output) + "/" +str(user_name) + '/1_ID_Sources_Info'
    
    isExist = os.path.exists(path_save)
    if not isExist:
       # Create a new directory because it does not exist
       os.makedirs(path_save)
       print("The new directory is created!")
       
    #######################################################################################
    #Get all study id in kcr 
    #######################################################################################
    file_name = str(metacsv) #"UH3_KCRnewreviewedcases_202309.csv" "UH3_KCRnewreviewedcases_202309.csv" #"UH3_KCRnewreviewedcases.csv"
    completeName = os.path.join(path_csv, file_name)
    kcr_df = pd.read_csv(completeName, header=0, dtype='string')#, parse_dates=[19, 22, 25]) #dtype='string', 
    #### get site num
    col_list = list(kcr_df.columns.values)
    site_num = int(sum('site_o' in s for s in col_list))
    if site_num >6:
        site_num = 6
 
    #site01-06 should be for other cancer, but we found code C500-509 in these columns, manually checked SEER, they are other cancers acutally, 
    #So manually code them as NA
    bc_codes = ['C50{}'.format(j) for j in range(0, 9+1)] 
    
    #for kkk in range(1,int(site_num)+1,1):
    #    site_name = 'site_o' + str(kkk)
    #    kcr_df.loc[kcr_df[site_name] in bc_codes, site_name] = 'NA'
    
    #kcr_df.loc[~kcr_df.site_o1.isin(bc_codes), 'site_o1'] = ''
    
    #uh3_kcr_df[which(uh3_kcr_df[,"site_o1"] %in% bc_codes),"site_o1"] <- NA
    #Found none in the following
    # uh3_kcr_df[which(uh3_kcr_df[,"site_o2"] %in% bc_codes),"site_o2"]
    # uh3_kcr_df[which(uh3_kcr_df[,"site_o3"] %in% bc_codes),"site_o3"]
    # uh3_kcr_df[which(uh3_kcr_df[,"site_o4"] %in% bc_codes),"site_o4"]
    # uh3_kcr_df[which(uh3_kcr_df[,"site_o5"] %in% bc_codes),"site_o5"]
    # uh3_kcr_df[which(uh3_kcr_df[,"site_o6"] %in% bc_codes),"site_o6"]
    
    ###########################################################################
    ###########   2. Analysis IDs                                   ###########  
    ###########################################################################
    unique_IDs = kcr_df["study_id"].unique()
    
    seq_list = ["First","Second","Third","Fourth","Fifth","Sixth"]
    seq = {
      "First": ['0','1'],
      "Second": ['2'],
      "Third": ['3'],
      'Fourth': ['4'],
      'Fifth': ['5'],
      'Sixth': ['6']
    }
    
    
    frames_all = []
    for i in range(len(unique_IDs)): #len(unique_IDs)
        #print(unique_IDs[i])
        curr_id = unique_IDs[i]
        curr_df = kcr_df.loc[kcr_df['study_id'] == curr_id]
        
        #i = 15#276#41
        #curr_id = unique_IDs[i]
        #curr_df = kcr_df.loc[kcr_df['study_id'] == curr_id]
        
        frames = []
        #1. get 1st,2nd,3rd and 4th... primary site and dates
        primary_df = pd.DataFrame(np.zeros((6,4)))
        primary_df.columns = ["Site","Date","Type", 'study_id']
        
        
        for ii in range(6):
            name = seq_list[ii]
            curr_seq = seq[name]   
            res = get_primary_site_date_func(curr_df, curr_seq, name, curr_id)
            curr_type = name + '_Primary'
            primary_df.iloc[ii,0] = res[0]
            primary_df.iloc[ii,1] = res[1]
            primary_df.iloc[ii,2] = res[2]
            primary_df.iloc[ii,3] = res[3]
            
        #primary_df_1 = primary_df[(primary_df.iloc[:,:] != 0).any(1)]    
        frames.append(primary_df)   
            
        #2.Get 1st primary BC recurrence if there is one  
        primary_df_1recur = pd.DataFrame(np.zeros((1,4)))
        primary_df_1recur.columns = ["Site","Date","Type", 'study_id']
        res = get_primary_site_date_func1(curr_df, seq[seq_list[0]] , seq_list[0], curr_id)
        primary_df_1recur.iloc[0,0] = res[0]
        primary_df_1recur.iloc[0,1] = res[1]
        primary_df_1recur.iloc[0,2] = res[2]
        primary_df_1recur.iloc[0,3] = res[3]
    
        frames.append(primary_df_1recur)           
        
        #3.Get Other cancer info
        #n_sites = 2 #6 #change
        other_df = pd.DataFrame(np.zeros((site_num,4)))
        other_df.columns = ["Site","Date","Type", 'study_id']        
        
        for ii in range(site_num):      
            curr_ii = "site_o" + str(ii+1)
            curr_other_site = curr_df.loc[curr_df.index[0],curr_ii]
            if not pd.isna(curr_other_site):
                if curr_other_site not in bc_codes:
                    curr_other_site = curr_other_site
                    curr_date = "date_o" + str(ii+1)
                    curr_other_site_date = curr_df.loc[curr_df.index[0],curr_date]
                    curr_type = 'Other'
                    curr_id_f = curr_id
                else:
                    curr_other_site = int(0)
                    curr_other_site_date = int(0)
                    curr_type = int(0)
                    curr_id_f = int(0)
            else: 
                curr_other_site = int(0)
                curr_other_site_date = int(0)
                curr_type = int(0)
                curr_id_f = int(0)
            
            other_df.iloc[ii, 0] = curr_other_site
            other_df.iloc[ii, 1] = curr_other_site_date
            other_df.iloc[ii, 2] = curr_type
            other_df.iloc[ii, 3] = curr_id_f
            
        frames.append(other_df)
        
        curr_df_all = pd.concat(frames,axis=0, ignore_index=True)   
        curr_df_all_keep = curr_df_all[(curr_df_all.iloc[:,:] != 0).any(1)]
        
        frames_all.append(curr_df_all_keep)
        
    
    final_df_all = pd.concat(frames_all,axis=0, ignore_index=True)   
    
    
    ############################################################################################
    #4.If there are pts who primary cancer is not breast cancer, then exclude
    ############################################################################################
    #first check (none)
    ID_drop = []
    pri_1st_df = final_df_all[final_df_all['Type'] == "First_Primary"]
    for i in range(pri_1st_df.shape[0]):
        curr_site= pri_1st_df.loc[pri_1st_df.index[i],"Site"]
        if curr_site not in bc_codes : #bc_codes
            curr_id = pri_1st_df.loc[pri_1st_df.index[i],"study_id"]
            ID_drop.append(curr_id)
    #ID_drop = ['1']
    final_df_all_keep1 = final_df_all[~final_df_all['study_id'].isin(ID_drop)]
    ############################################################################################
    #5. Exclude pt has no 1st primay cancer info
    ############################################################################################
    #first check (none)
    ID_drop = []
    check_list = ['First_Primary']
    for i in range(len(unique_IDs)): #len(unique_IDs)
        #print(unique_IDs[i])
        curr_id = unique_IDs[i]
        curr_df = final_df_all_keep1.loc[final_df_all_keep1['study_id'] == curr_id]
        
        test = curr_df['Type'].isin(check_list)
        if not test.any():
            #print(curr_id)
            #first check (none)
            ID_drop.append(curr_id)
        
    final_df_all_keep2 = final_df_all_keep1[~final_df_all_keep1['study_id'].isin(ID_drop)]
    
    unique_IDs_keep = final_df_all_keep2["study_id"].unique()
    
    
    ############################################################################################
    #'@NOTE 6. Merge two date and site, if the time is the same
    ############################################################################################
    frames = []
    
    for i in range(len(unique_IDs_keep)): #
        #print(unique_IDs[i])
        curr_id = unique_IDs_keep[i]
        curr_df = final_df_all_keep2.loc[final_df_all_keep2['study_id'] == curr_id]
        
        if len(curr_df) ==1:
            frames.append(curr_df)
        else:
            curr_df = curr_df.groupby(curr_df['Date'].ne(curr_df['Date'].shift()).cumsum(), as_index=False).agg({'Site': '$$$'.join, 'Type':'$$$'.join, 'study_id': 'first', 'Date': 'first'})
            frames.append(curr_df)
    
    final_df_all_keep3 = pd.concat(frames,axis=0, ignore_index=True) 
    #print(final_df_all_keep3)
    #final_df_all_keep3 = change_column_format2(final_df_all_keep3, 'Date')
    
    
    file_name = "4_All_cancer_site_date_df.csv"
    completeName = os.path.join(path_save, file_name)
    final_df_all_keep3.to_csv(completeName, index=False)
    
    
    print('4A')
    print('unique_IDs', len(final_df_all_keep3["study_id"].unique()))
    print('drop', ID_drop)
    print('4A done')
    
    