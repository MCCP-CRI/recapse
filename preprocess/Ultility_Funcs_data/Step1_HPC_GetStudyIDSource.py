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



#user_name = str(sys.argv[1])
def Step1_GetStudyIDSource(user_name, path_input, path_output, metacsv, mecareClaims, mecaidClaims, mecaidClaims2):
    path_csv = str(path_input) #r'/users/qqi227/Manual_Reviewed_Cases/Input_Manual_Reviewed_Cases'
    path_save = str(path_output) + "/" +str(user_name) + '/1_ID_Sources_Info'
    
    isExist = os.path.exists(path_save)
    if not isExist:
       # Create a new directory because it does not exist
       os.makedirs(path_save)
       print("The new directory is created!")
       
    #######################################################################################
    #Get all study id in kcr 
    #######################################################################################
    file_name = str(metacsv) #"UH3_KCRnewreviewedcases_202309.csv"
    completeName = os.path.join(path_csv, file_name)
    kcr_df = pd.read_csv(completeName, header=0)
    kcr_ID = kcr_df["study_id"].unique() #47130 #study_id
    
    
    #######################################################################################
    #Read Medicare
    #######################################################################################
    file_name = str(mecareClaims) #"medicare_breast_claims_new.csv"
    completeName = os.path.join(path_csv, file_name)
    medicare_df = pd.read_csv(completeName, header=0)
    medicare_IDs = medicare_df["study_id"].unique()
    
    #######################################################################################
    #Read medicaid
    #######################################################################################
    file_name = str(mecaidClaims) #"medicaid_breast_claims_new.csv"
    completeName = os.path.join(path_csv, file_name)
    medicaid_health_df = pd.read_csv(completeName, header=0)
    health_ID = medicaid_health_df["study_id"].unique()
    file_name = str(mecaidClaims2) #"medicaid_breast_Rxclaims_new.csv"
    completeName = os.path.join(path_csv, file_name)
    medicaid_pharm_df = pd.read_csv(completeName, header=0)
    pharm_ID = medicaid_pharm_df["study_id"].unique()
    medicaid_IDs = np.union1d(health_ID, pharm_ID) #take the union, some pts has no health claims, some has no pharm claim
    
    ALLID_df = pd.DataFrame(np.zeros(((kcr_ID.shape[0]),3)))
    ALLID_df.columns = ["Kcr_ID","in_Medicare","in_Medicaid"]
    
    for i in range(kcr_ID.shape[0]):
        curr_id = kcr_ID[i]
        ALLID_df.iloc[i,0] = curr_id
        #in medicare
        if curr_id in medicare_IDs:
            ALLID_df.iloc[i,1] = int(1)
        else:
            ALLID_df.iloc[i,1] = int(0)
            
        #in medicaid
        if curr_id in medicaid_IDs:
            ALLID_df.iloc[i,2] = int(1)
        else:
            ALLID_df.iloc[i,2] = int(0)
            
    file_name = "All_ID_Source-all.csv"
    completeName = os.path.join(path_save, file_name)
    ALLID_df.to_csv(completeName, index=False) 
    
    file_name = "All_ID_Source-all.csv"
    completeName = os.path.join(path_save, file_name)
    df = pd.read_csv(completeName, header=0, dtype='string')
    df= df.astype(float)
    df= df.astype(int)
    
    df_keep = df[(df['in_Medicare'] != 0 ) | (df['in_Medicaid'] != 0)]
    
    
    file_name = "All_ID_Source.csv"
    completeName = os.path.join(path_save, file_name)
    df_keep.to_csv(completeName, index=False)
    
    print("Step 1 done")



def Step1_GetStudyIDSource1(user_name, path_input, path_output, metacsv, mecareClaims):
    path_csv = str(path_input) #r'/users/qqi227/Manual_Reviewed_Cases/Input_Manual_Reviewed_Cases'
    path_save = str(path_output) + "/" +str(user_name) + '/1_ID_Sources_Info'
    
    isExist = os.path.exists(path_save)
    if not isExist:
       # Create a new directory because it does not exist
       os.makedirs(path_save)
       print("The new directory is created!")
       
    #######################################################################################
    #Get all study id in kcr 
    #######################################################################################
    file_name = str(metacsv) #"UH3_KCRnewreviewedcases_202309.csv"
    completeName = os.path.join(path_csv, file_name)
    kcr_df = pd.read_csv(completeName, header=0)
    kcr_ID = kcr_df["study_id"].unique() #47130 #study_id
    
    
    #######################################################################################
    #Read Medicare
    #######################################################################################
    file_name = str(mecareClaims) #"medicare_breast_claims_new.csv"
    completeName = os.path.join(path_csv, file_name)
    medicare_df = pd.read_csv(completeName, header=0)
    medicare_IDs = medicare_df["study_id"].unique()
    
    #######################################################################################
    #Read medicaid
    #######################################################################################
    
    
    ALLID_df = pd.DataFrame(np.zeros(((kcr_ID.shape[0]),3)))
    ALLID_df.columns = ["Kcr_ID","in_Medicare","in_Medicaid"]
    
    for i in range(kcr_ID.shape[0]):
        curr_id = kcr_ID[i]
        ALLID_df.iloc[i,0] = curr_id
        #in medicare

        ALLID_df.iloc[i,1] = int(1)

        ALLID_df.iloc[i,2] = int(0)
            
    file_name = "All_ID_Source-all.csv"
    completeName = os.path.join(path_save, file_name)
    ALLID_df.to_csv(completeName, index=False) 
    
    file_name = "All_ID_Source-all.csv"
    completeName = os.path.join(path_save, file_name)
    df = pd.read_csv(completeName, header=0, dtype='string')
    df= df.astype(float)
    df= df.astype(int)
    
    df_keep = df[(df['in_Medicare'] != 0 ) | (df['in_Medicaid'] != 0)]
    
    
    file_name = "All_ID_Source.csv"
    completeName = os.path.join(path_save, file_name)
    df_keep.to_csv(completeName, index=False)
    
    print("Step 1 only medicare done")


def Step1_GetStudyIDSource2(user_name, path_input, path_output, metacsv, mecaidClaims, mecaidClaims2):
    path_csv = str(path_input) #r'/users/qqi227/Manual_Reviewed_Cases/Input_Manual_Reviewed_Cases'
    path_save = str(path_output) + "/" +str(user_name) + '/1_ID_Sources_Info'
    
    isExist = os.path.exists(path_save)
    if not isExist:
       # Create a new directory because it does not exist
       os.makedirs(path_save)
       print("The new directory is created!")
       
    #######################################################################################
    #Get all study id in kcr 
    #######################################################################################
    file_name = str(metacsv) #"UH3_KCRnewreviewedcases_202309.csv"
    completeName = os.path.join(path_csv, file_name)
    kcr_df = pd.read_csv(completeName, header=0)
    kcr_ID = kcr_df["study_id"].unique() #47130 #study_id
    
    
    #######################################################################################
    #Read Medicare
    #######################################################################################
    
    #######################################################################################
    #Read medicaid
    #######################################################################################
    file_name = str(mecaidClaims) #"medicaid_breast_claims_new.csv"
    completeName = os.path.join(path_csv, file_name)
    medicaid_health_df = pd.read_csv(completeName, header=0)
    health_ID = medicaid_health_df["study_id"].unique()
    file_name = str(mecaidClaims2) #"medicaid_breast_Rxclaims_new.csv"
    completeName = os.path.join(path_csv, file_name)
    medicaid_pharm_df = pd.read_csv(completeName, header=0)
    pharm_ID = medicaid_pharm_df["study_id"].unique()
    medicaid_IDs = np.union1d(health_ID, pharm_ID) #take the union, some pts has no health claims, some has no pharm claim
    
    ALLID_df = pd.DataFrame(np.zeros(((kcr_ID.shape[0]),3)))
    ALLID_df.columns = ["Kcr_ID","in_Medicare","in_Medicaid"]
    
    for i in range(kcr_ID.shape[0]):
        curr_id = kcr_ID[i]
        ALLID_df.iloc[i,0] = curr_id
        #in medicare

        ALLID_df.iloc[i,1] = int(0)
            
        #in medicaid

        ALLID_df.iloc[i,2] = int(1)

            
    file_name = "All_ID_Source-all.csv"
    completeName = os.path.join(path_save, file_name)
    ALLID_df.to_csv(completeName, index=False) 
    
    file_name = "All_ID_Source-all.csv"
    completeName = os.path.join(path_save, file_name)
    df = pd.read_csv(completeName, header=0, dtype='string')
    df= df.astype(float)
    df= df.astype(int)
    
    df_keep = df[(df['in_Medicare'] != 0 ) | (df['in_Medicaid'] != 0)]
    
    
    file_name = "All_ID_Source.csv"
    completeName = os.path.join(path_save, file_name)
    df_keep.to_csv(completeName, index=False)
    
    print("Step 1 only medicaid done")
