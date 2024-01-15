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


def Step8A_Get_PatientLevelCharateristics(user_name, path_input, path_output, metacsv):
    ###HPC
    path_csv = str(path_input) #r'/users/qqi227/Manual_Reviewed_Cases/Input_Manual_Reviewed_Cases'
    path_save = str(path_output) + "/" +str(user_name) + '/8_Characteristics2/Patient_Level'
    path_ID = str(path_output) + "/" +str(user_name) + '/1_ID_Sources_Info'
    path_all_enrollmon = str(path_output) + "/" +str(user_name) + '/5_Enrollment_And_Prediction_Months'
    #path_site = r'/Users/qiqiao/Desktop/dp/Rewrite'
    
    isExist = os.path.exists(path_save)
    if not isExist:
       # Create a new directory because it does not exist
       os.makedirs(path_save)
       print("The new directory is created!")
       
       
    #######################
    # Medicaid
    ######################
    file_name = str(metacsv) #"UH3_KCRnewreviewedcases_202309.csv"
    completeName = os.path.join(path_csv, file_name)
    kcr_data = pd.read_csv(completeName, header=0)
    kcr_data = kcr_data.fillna('NA')
    #kcr_data.columns = ["CauseOfDeath","censusTract2010","csExtension","CSLymphNodes","csLymphNodesEval","CSTumorSize","CSTumorSizeExtEval","Grade","Laterality","PrimarySite","RXSummChemo","RXSummHormone","RXSummRadiation","RXSummSurgPrimSite","Year_Diag","Race1","APPAL","DiagAge","study_id","Date_LC","date_lc_sunrise","recur_index","review_1recur_dt","recur_method","recur_laterality","Date_dx","date_Birth","CentralSequenceNumber","SEERSummStg2000","ajccstage","er_stat","pr_stat","her2_stat","RegNodesExamined","RegNodesPositive","RuralUrbanContin2013","vitalStat","County","RUCA2010","TNMClinT","TNMClinN","TNMClinM","TNMPathT","TNMPathN","TNMPathM","site_o1","site_o2","date_o1","date_o2","sequence_o1","sequence_o2"]
    
    #Recode race
    kcr_data = recode_Race_func(kcr_data)
    #list(kcr_data)
    kcr_data = recode_SPS_func(kcr_data)
    
    #########################################################################################################
    #Compute DAJCC_T, DAJCC_M, DAJCC_N
    #########################################################################################################
    kcr_data = get_DAJCC_var_funtion(kcr_data,'DAJCC_T', "TNMPathT","TNMClinT")
    kcr_data = get_DAJCC_var_funtion(kcr_data,'DAJCC_M', "TNMPathM","TNMClinM")
    kcr_data = get_DAJCC_var_funtion(kcr_data,'DAJCC_N', "TNMPathN","TNMClinN")
    
    #convert DAJCC variable to numeric code
    kcr_data = convert_DAJCC_var_function(kcr_data, "DAJCC_T")
    kcr_data = convert_DAJCC_var_function(kcr_data, "DAJCC_N")
    kcr_data = convert_DAJCC_var_function(kcr_data, "DAJCC_M")
    #list(kcr_data)
    
    ################################################################################ 
    ##4. Load ID source
    ################################################################################ 
    file_name = "All_ID_Source_prediction_Months.csv" #"All_ID_Source.csv"
    completeName = os.path.join(path_ID, file_name)
    ID_Sources_data = pd.read_csv(completeName, header=0, dtype='int')    
              
    ################################################################################ 
    #7. BC codes
    ################################################################################ 
    bc_codes = ['C50{}'.format(j) for j in range(0, 9+1)] 
    
    ################################################################################ 
    #8. All cancer site df
    ################################################################################ 
    #file_name = "4_All_event_df.xlsx"
    #completeName = os.path.join(path_site, file_name)
    #All_cancer_site_date_data = pd.read_excel(completeName,header=0, index_col=False, dtype='string')       
    
    #########################################################################################################
    #### 6.  get charastersitc for final anlaysis IDs
    #########################################################################################################            
    pts_level_char_df1 = get_pts_level_char_func(ID_Sources_data, kcr_data)
    file_name = "8_PatientLevel_char_WithPossibleMonthsHasNoCodes.xlsx"
    completeName = os.path.join(path_save, file_name)
    pts_level_char_df1.to_excel(completeName, header = True, index=False)
           
    #################################################################################
    #Data dir
    ################################################################################ 
    path_save2 = str(path_output) + "/" +str(user_name) + '/8_Characteristics2/Month_Level'  
    #path_monthly_xlsx = r'/Users/qqi227/Desktop/dp/Rewrite/3_Get_PerMonthData_withCleanCodes'   
    isExist = os.path.exists(path_save2)
    if not isExist:
       # Create a new directory because it does not exist
       os.makedirs(path_save2)
       print("The new directory is created!")    
        
    
    ################################################################################
    #1.Load patient level char
    ################################################################################    
    patient_level_char_df = pts_level_char_df1
    
    ###get all enrolled month
    file_name = "5b_prediction_Months.csv" #"5_enrollment_Months.csv"  #5_enrollment_Months
    completeName = os.path.join(path_all_enrollmon, file_name)
    enrolled_month_all = pd.read_csv(completeName, header=0)
         
    analysis_IDs = ID_Sources_data['Kcr_ID'] 
    
    for i in range(len(analysis_IDs)):
        curr_id = analysis_IDs.iloc[i]
        #print(curr_id)
        curr_file = enrolled_month_all.loc[enrolled_month_all['study_id'] == curr_id]   
        
        #Patient level char
        curr_pt_level_df = patient_level_char_df.loc[patient_level_char_df["study_id"] == curr_id]
        
        #process only if pt has per month df and has patient level char df
        if len(curr_file) >0 and len(curr_pt_level_df) >0:
            #date of birth
            curr_dob = curr_pt_level_df.loc[curr_pt_level_df.index[0],"date_Birth"]
            curr_dob = change_y_m_d2(curr_dob)
            
            date_dx = curr_pt_level_df.loc[curr_pt_level_df.index[0],"Date_dx"]
            date_dx = change_y_m_d2(date_dx)
            
            #construct per patient month level data
            curr_month_level_char_df = pd.DataFrame(np.zeros((len(curr_file), 23)))
            name_list = ["Enrolled_year","Age","months_since_dx",
                                                "Race", "Site", "Stage","Grade","Laterality",
                                                "er_stat","pr_stat","her2_stat",
                                                "surg_prim_site_V1","surg_prim_site_V2",
                                                "DAJCC_T","DAJCC_M","DAJCC_N",
                                                "reg_age_at_dx","reg_nodes_exam","reg_nodes_pos",
                                                "cs_tum_size","cs_tum_ext","cs_tum_nodes",
                                                "regional"]
            curr_month_level_char_df.columns = name_list
            
            enrolled_month_df = curr_file[["Enrolled_Month"]].reset_index(drop=True)
            frames = [enrolled_month_df, curr_month_level_char_df]
            curr_month_level_char_df = pd.concat(frames,axis=1)#, ignore_index=True)
            
            #add features (This are the same across all rows)
            feature_cols = ["Race","Site","Stage","Grade","Laterality",
                          "er_stat","pr_stat","her2_stat","surg_prim_site_V1","surg_prim_site_V2",
                          "DAJCC_T","DAJCC_M","DAJCC_N",
                          "reg_age_at_dx","reg_nodes_exam","reg_nodes_pos",
                          "cs_tum_size","cs_tum_ext","cs_tum_nodes","regional"]
      
            curr_pt_level_df_new = pd.DataFrame(np.repeat(curr_pt_level_df.values, len(curr_month_level_char_df), axis=0))
            curr_pt_level_df_new.columns = list(curr_pt_level_df)
            curr_month_level_char_df[feature_cols] = curr_pt_level_df_new[feature_cols]
    
            curr_yr = enrolled_month_df['Enrolled_Month'].str[:4]
            curr_month_level_char_df["Enrolled_year"] = curr_yr
    
            #for each month row, add feature
            for k in range(len(curr_month_level_char_df)):
                #print(k)
                curr_date = curr_month_level_char_df.loc[curr_month_level_char_df.index[k],"Enrolled_Month"]
                curr_month_level_char_df.loc[curr_month_level_char_df.index[k],"Age"] = calculate_age(curr_date, curr_dob)
                curr_month_level_char_df.loc[curr_month_level_char_df.index[k],"months_since_dx"] = get_diff_month(curr_date, date_dx)
                
            file_name = "ID" + str(curr_id) + "_MonthChar.xlsx"
            completeName = os.path.join(path_save2, file_name)
            curr_month_level_char_df.to_excel(completeName, header = True, index=False)
                
    
    print("Step 8A done")    
        
            