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


def Step4B_GetEventType_addNewothers(user_name, path_input, path_output, metacsv):

    #HPC
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
    file_name = str(metacsv) #"UH3_KCRnewreviewedcases_202309.csv" "UH3_KCRnewreviewedcases_202309.csv"
    completeName = os.path.join(path_csv, file_name)
    kcr_df = pd.read_csv(completeName, header=0, dtype='string')
    
    #kcr_df.loc[ kcr_df["site_o1"] == “some_value”, "site_o1"] = 'NA'
    
    #site01-06 should be for other cancer, but we found code C500-509 in these columns, manually checked SEER, they are other cancers acutally, 
    #So manually code them as NA
    bc_codes = ['C50{}'.format(j) for j in range(0, 9+1)] 
    
    kcr_df_merge = kcr_df
    ############################################################################################
    #3. Load cancer site df
    ############################################################################################
    file_name = "4_All_cancer_site_date_df.csv"
    completeName = os.path.join(path_save, file_name)
    merged_cancer_site_df =  pd.read_csv(completeName, header=0, dtype='string')
    
    unique_IDs = merged_cancer_site_df["study_id"].unique()
    
    
    ############################################################################################
    #Get 1st,2nd, 3rd event type and date 
    #1st event:  1st primary dates
    #2nd event:  recurrence of the 1st or second primary or 1st primary bc death
    #3rd event:  subsqeunt after 2nd event
    ############################################################################################
    All_event_df = pd.DataFrame(np.zeros((len(unique_IDs), 14)))
    col_name = ["study_id","Date_1st_Event","Date_2nd_Event","Date_3rd_Event","Site_1st_Event","Site_2nd_Event","Site_3rd_Event","Type_1st_Event","Type_2nd_Event","Type_3rd_Event","Date_LC","Primary_1stBC_Death_Date","Days_1stEventTODeath","Days_1stTO2nd"]
    All_event_df.columns = col_name
    
    kcr_df_merge = kcr_df_merge[['study_id', 'PrimarySite', 'Date_LC', 'CauseOfDeath']]
    
    for i in range(len(unique_IDs)): #len(unique_IDs) 888+6
        curr_id = unique_IDs[i]
        #print(curr_id)
        All_event_df.loc[All_event_df.index[i],"study_id"] = curr_id
        #1.Get kcr info
        curr_uh3_kcr_df = kcr_df_merge.loc[kcr_df_merge['study_id'] == curr_id]
        #2.Last contact date 
        curr_last_contact_date = curr_uh3_kcr_df.loc[curr_uh3_kcr_df.index[0],"Date_LC"]
        #3.Get death info
        #curr_death_site = 
        if len(curr_uh3_kcr_df) ==1:
            curr_death_site = curr_uh3_kcr_df.loc[curr_uh3_kcr_df.index[0],"CauseOfDeath"] 
        else:
            #print('Yes')
            curr_death_site = curr_uh3_kcr_df.loc[curr_uh3_kcr_df.index[0],"CauseOfDeath"] 
            list_test = curr_uh3_kcr_df['CauseOfDeath'].tolist() 
            curr_death_site = '$$$'.join(list_test)
            
        #4. get current cancer info
        curr_cancer_df = merged_cancer_site_df.loc[merged_cancer_site_df['study_id'] == curr_id]
        #5.Get first primary info
        first_primary_info = get_cancer_info_func(curr_cancer_df, 'First_Primary')
        first_primary_site = first_primary_info[0].split('$$$')[0]
        
        #6.Check first-primary related death ### must within 2019
        if first_primary_site in curr_death_site and change_y_m_d2(curr_last_contact_date)[0:4] <= '2019':
            curr_1st_p_death_site = curr_death_site
            curr_last_contact_date = curr_last_contact_date #change_column_format3(curr_last_contact_date) QQ changed
            curr_1st_p_death_date = curr_last_contact_date#change_column_format3(curr_last_contact_date)
            curr_1st_p_death_type = "Primary1stBC_related_Death"
        else:
            curr_1st_p_death_site = 'NA'
            curr_1st_p_death_date = 'NA'
            curr_1st_p_death_type = 'NA'
            
        #7.Get First-primary related death df
        curr_death_1st_p_df = pd.DataFrame(np.zeros((1, 4), dtype=str))
        curr_death_1st_p_df.columns = ['Site', 'Date', 'Type', 'study_id']
        if curr_1st_p_death_site != 'NA':
            #print('Yes')
            curr_death_1st_p_df.loc[curr_death_1st_p_df.index[0],"study_id"] = curr_id 
            curr_death_1st_p_df.loc[curr_death_1st_p_df.index[0],"Site"] = curr_1st_p_death_site
            curr_death_1st_p_df.loc[curr_death_1st_p_df.index[0],"Date"] = curr_1st_p_death_date
            curr_death_1st_p_df.loc[curr_death_1st_p_df.index[0],"Type"] = curr_1st_p_death_type
        else:
            #print('here')
            curr_death_1st_p_df = pd.DataFrame()
            
        #5.Combine cancer info and death info
        curr_cancer_and_death_df = pd.concat([curr_cancer_df, curr_death_1st_p_df], axis = 0)
        curr_cancer_and_death_df.sort_values(by='Date', inplace = True)#, ascending = False)
        
        #6.Get all event
        #'@1stevent must be 1st primary bc dates
        curr_cancer_and_death_df1 = curr_cancer_and_death_df.loc[curr_cancer_and_death_df['Type'].str.contains('First_Primary', case=False)]
        All_event_df.loc[All_event_df.index[i],"Site_1st_Event"] = curr_cancer_and_death_df1.loc[curr_cancer_and_death_df1.index[0],"Site"]
        All_event_df.loc[All_event_df.index[i],"Date_1st_Event"] = curr_cancer_and_death_df1.loc[curr_cancer_and_death_df1.index[0],"Date"]
        All_event_df.loc[All_event_df.index[i],"Type_1st_Event"] = curr_cancer_and_death_df1.loc[curr_cancer_and_death_df1.index[0],"Type"]
        
        #'@2ndevent  could be 1st primary bc death OR 
        #'recur OR secondary primary OR merged both (happened at the same time)
        curr_cancer_and_death_df1 = curr_cancer_and_death_df.loc[curr_cancer_and_death_df['Type'].str.contains('Second_Primary|1Recur|Primary1stBC_related_Death', case=False)]
        
        curr_cancer_and_death_df1 = curr_cancer_and_death_df1.loc[~curr_cancer_and_death_df1["Type"].str.contains('First_Primary', case=False)]
        if len(curr_cancer_and_death_df1) ==0:
            All_event_df.loc[All_event_df.index[i],"Site_2nd_Event"] = 'NA'
            All_event_df.loc[All_event_df.index[i],"Date_2nd_Event"] = 'NA'
            All_event_df.loc[All_event_df.index[i],"Type_2nd_Event"] = 'NA'
            All_event_df.loc[All_event_df.index[i],"Site_3rd_Event"] = 'NA'
            All_event_df.loc[All_event_df.index[i],"Date_3rd_Event"] = 'NA'
            All_event_df.loc[All_event_df.index[i],"Type_3rd_Event"] = 'NA'
        else:
            All_event_df.loc[All_event_df.index[i],"Site_2nd_Event"] = curr_cancer_and_death_df1.loc[curr_cancer_and_death_df1.index[0],"Site"]
            All_event_df.loc[All_event_df.index[i],"Date_2nd_Event"] = curr_cancer_and_death_df1.loc[curr_cancer_and_death_df1.index[0],"Date"]
            All_event_df.loc[All_event_df.index[i],"Type_2nd_Event"] = curr_cancer_and_death_df1.loc[curr_cancer_and_death_df1.index[0],"Type"]
            secondary_date = curr_cancer_and_death_df1.loc[curr_cancer_and_death_df1.index[0],"Date"]
            
            #'@ThridEvent  #3rd event could be any subsequent diagnoses/death after 2nd event 
            #'#the diagnoses could be a recurrences or primary breast or non-breast cancers)
            curr_cancer_and_death_df1 = curr_cancer_and_death_df.loc[curr_cancer_and_death_df['Type'].str.contains('Third_Primary|Other', case=False)]
            if len(curr_cancer_and_death_df1) ==0:
                All_event_df.loc[All_event_df.index[i],"Site_3rd_Event"] = 'NA'
                All_event_df.loc[All_event_df.index[i],"Date_3rd_Event"] = 'NA'
                All_event_df.loc[All_event_df.index[i],"Type_3rd_Event"] = 'NA'
            else:
                curr_cancer_and_death_df1.sort_values(by='Date', inplace = True)#, ascending = False)
                if secondary_date > curr_cancer_and_death_df1.loc[curr_cancer_and_death_df1.index[0],"Date"]: ### 2rd early than 3rd
                    if len(curr_cancer_and_death_df1) ==1:
                        All_event_df.loc[All_event_df.index[i],"Site_3rd_Event"] = curr_cancer_and_death_df1.loc[curr_cancer_and_death_df1.index[0],"Site"]
                        All_event_df.loc[All_event_df.index[i],"Date_3rd_Event"] = curr_cancer_and_death_df1.loc[curr_cancer_and_death_df1.index[0],"Date"]
                        All_event_df.loc[All_event_df.index[i],"Type_3rd_Event"] = curr_cancer_and_death_df1.loc[curr_cancer_and_death_df1.index[0],"Type"]
                    else:
                        list_site = curr_cancer_and_death_df1['Site'].tolist() 
                        curr_death_site = '$$$'.join(list_site)
                        list_date = curr_cancer_and_death_df1['Date'].tolist() 
                        curr_death_date = '$$$'.join(list_date)
                        list_type = curr_cancer_and_death_df1['Type'].tolist() 
                        curr_death_type = '$$$'.join(list_type)
    
                        All_event_df.loc[All_event_df.index[i],"Site_3rd_Event"] = curr_death_site
                        All_event_df.loc[All_event_df.index[i],"Date_3rd_Event"] = curr_death_date
                        All_event_df.loc[All_event_df.index[i],"Type_3rd_Event"] = curr_death_type
                else:
                    All_event_df.loc[All_event_df.index[i],"Site_3rd_Event"] = 'NA'
                    All_event_df.loc[All_event_df.index[i],"Date_3rd_Event"] = 'NA'
                    All_event_df.loc[All_event_df.index[i],"Type_3rd_Event"] = 'NA'
    
    
                
        #8.Last contact date
        if not pd.isna(curr_last_contact_date):
            All_event_df.loc[All_event_df.index[i],"Date_LC"] = curr_last_contact_date #change_column_format3(curr_last_contact_date)
        else:
            All_event_df.loc[All_event_df.index[i],"Date_LC"] = curr_last_contact_date
        
        #9.Get time from 1st event to 1st primary bc related death
        All_event_df.loc[All_event_df.index[i],"Primary_1stBC_Death_Date"] = curr_1st_p_death_date
        if curr_1st_p_death_date != 'NA':
            diff_date = change_y_m_d2(curr_1st_p_death_date)
            diff_date1 = change_y_m_d2(All_event_df.loc[All_event_df.index[i],"Date_1st_Event"])
            diff_date_f = round(calculate_diff_day(diff_date , diff_date1))  
            All_event_df.loc[All_event_df.index[i],"Days_1stEventTODeath"] = int(diff_date_f)
        else:
            All_event_df.loc[All_event_df.index[i],"Days_1stEventTODeath"] = 'NA'
        
        if All_event_df.loc[All_event_df.index[i],"Date_1st_Event"] != 'NA' and All_event_df.loc[All_event_df.index[i],"Date_2nd_Event"] != 'NA':
            #print(curr_id)
            #print(All_event_df.loc[All_event_df.index[i],"Date_1st_Event"], All_event_df.loc[All_event_df.index[i],"Date_2nd_Event"])
            diff_date = change_y_m_d2(All_event_df.loc[All_event_df.index[i],"Date_2nd_Event"])
            diff_date1 = change_y_m_d2(All_event_df.loc[All_event_df.index[i],"Date_1st_Event"])
            diff_date_f = round(calculate_diff_day(diff_date , diff_date1))  
            All_event_df.loc[All_event_df.index[i],"Days_1stTO2nd"] = int(diff_date_f)
        else:
            All_event_df.loc[All_event_df.index[i],"Days_1stTO2nd"] = 'NA'
            
    
    
    
    #Include death as the type if it is the same as event date, but the event type
    curr_df = All_event_df.loc[(All_event_df['Primary_1stBC_Death_Date'] == All_event_df['Date_1st_Event']) & (All_event_df['Type_1st_Event'] != 'Primary1stBC_related_Death')]
    if len(curr_df) >0:
        if i in range(len(curr_df)):
            curr_df.loc[curr_df.index[i],'Type_1st_Event'] = str(curr_df.loc[curr_df.index[i],'Type_1st_Event']) + '$$$' + "Primary1stBC_related_Death"
        
    curr_df = All_event_df.loc[(All_event_df['Primary_1stBC_Death_Date'] == All_event_df['Date_2nd_Event']) & (All_event_df['Type_2nd_Event'] != 'Primary1stBC_related_Death')]
    if len(curr_df) >0:
        if i in range(len(curr_df)):
            curr_df.loc[curr_df.index[i],'Type_2nd_Event'] = str(curr_df.loc[curr_df.index[i],'Type_2nd_Event']) + '$$$' + "Primary1stBC_related_Death"
    
    curr_df = All_event_df.loc[(All_event_df['Primary_1stBC_Death_Date'] == All_event_df['Date_3rd_Event']) & (All_event_df['Type_3rd_Event'] != 'Primary1stBC_related_Death')]
    if len(curr_df) >0:
        if i in range(len(curr_df)):
            curr_df.loc[curr_df.index[i],'Type_3rd_Event'] = str(curr_df.loc[curr_df.index[i],'Type_3rd_Event']) + '$$$' + "Primary1stBC_related_Death"
        
        
    ####################################################################################################
    #'@NOTE:  The 2nd event (recur or 2nd primary or death) must occur 6 month (6*30 = 180 days) after 1st event
    # Exclude patients who has 2nd event within 6 month after 1st event
    ####################################################################################################
        
    ID_list = []
    for i in range(len(All_event_df)):
        curr_check = All_event_df.loc[All_event_df.index[i],'Days_1stTO2nd']
        if curr_check != 'NA':
            if int(curr_check) < 180:
                curr_id = All_event_df.loc[All_event_df.index[i],'study_id']
                ID_list.append(curr_id)
    
    
    
    final_All_event_df = All_event_df[~All_event_df['study_id'].isin(ID_list)]
    file_name = "4_All_event_df_add_subsequent.csv"
    completeName = os.path.join(path_save, file_name)
    final_All_event_df.to_csv(completeName, index=False)         
            
        
        
    print('4B')
    print('unique_IDs', len(final_All_event_df["study_id"].unique()))
    print('list_drop due to < 180: The 2nd event (recur or 2nd primary or death) must occur 6 month (6*30 = 180 days) after 1st event')
    for i in range(len(ID_list)):
        print(ID_list[i])
    
    
    print('4B done')
    
    
    
    
    
    
    
