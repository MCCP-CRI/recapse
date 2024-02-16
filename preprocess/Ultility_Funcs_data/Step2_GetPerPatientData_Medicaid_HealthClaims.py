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



def Step2_GetPerPatientData_Medicaid_HealthClaims(user_name, path_input, path_output, mecareClaims, mecaidClaims, mecaidClaims2):
   path_csv = str(path_input) #r'/users/qqi227/Manual_Reviewed_Cases/Input_Manual_Reviewed_Cases'
   path_save_ori = str(path_output)  + '/' +str(user_name) + '/2_RawClaims_perPatient'
   
   isExist = os.path.exists(path_save_ori)
   if not isExist:
      # Create a new directory because it does not exist
      os.makedirs(path_save_ori)
      print("The new directory is created!")
      
   #######################################################################################
   #Get all study id in kcr 
   #######################################################################################
   #file_name = "UH3_KCRnewreviewedcases.csv"
   #completeName = os.path.join(path_csv, file_name)
   #kcr_df = pd.read_csv(completeName, header=0, dtype='string')
   
   #######################################################################################
   #Read Medicare
   #######################################################################################
   file_name = str(mecareClaims) #"medicare_breast_claims_new.csv" 
   completeName = os.path.join(path_csv, file_name)
   medicare_df = pd.read_csv(completeName, header=0, dtype='string')
   flag = 0 ## convert date
   #medicare_df = medicare_df.rename(columns={'patient_id': 'study_id'})
   #medicare_df = medicare_df.rename(columns={'CLAIMS_DATE': 'claims_date'})
   ############################################
   # check date
   ############################################
   if flag == 1:
       medicare_df = convert_SAS_Excel_date(medicare_df, 'claims_date')
   
   #######################################################################################
   #Read medicaid
   #######################################################################################
   file_name = str(mecaidClaims) #"medicaid_breast_claims_new.csv" 
   completeName = os.path.join(path_csv, file_name)
   medicaid_health_df = pd.read_csv(completeName, header=0, dtype='string')
   #medicaid_health_df = medicaid_health_df.rename(columns={'patient_id': 'study_id'})
   
   file_name = str(mecaidClaims2) #"medicaid_breast_Rxclaims_new.csv" 
   completeName = os.path.join(path_csv, file_name)
   medicaid_pharm_df = pd.read_csv(completeName, header=0, dtype='string')
   #medicaid_pharm_df = medicaid_pharm_df.rename(columns={'patient_id': 'study_id'})
   
   #path_save = r'/users/qqi227/Rewrite-dataProcessing/Results_QQ/Medicaid_HealthClaims'
   label = 'Medicaid_HealthClaims'
   path_save = os.path.join(path_save_ori, label)
   
   isExist = os.path.exists(path_save)
   if not isExist:
      # Create a new directory because it does not exist
      os.makedirs(path_save)
      print("The new directory is created!")
   GetPerPatientData(medicaid_health_df, "medicaid_healthclaims", path_save)
   
   #path_save = r'/users/qqi227/Rewrite-dataProcessing/Results_QQ/Medicaid_PharmClaims'
   label = 'Medicaid_PharmClaims'
   path_save = os.path.join(path_save_ori, label)
   isExist = os.path.exists(path_save)
   if not isExist:
      # Create a new directory because it does not exist
      os.makedirs(path_save)
      print("The new directory is created!")
   GetPerPatientData(medicaid_pharm_df, "medicaid_pharmclaims", path_save)
   
   #path_save = r'/users/qqi227/Rewrite-dataProcessing/Results_QQ/Medicare'
   label = 'Medicare'
   path_save = os.path.join(path_save_ori, label)
   isExist = os.path.exists(path_save)
   if not isExist:
      # Create a new directory because it does not exist
      os.makedirs(path_save)
      print("The new directory is created!")
   GetPerPatientData(medicare_df, "medicare_claims", path_save)
   
   print("Step 2 done")


def Step2_GetPerPatientData_Medicaid_HealthClaims1(user_name, path_input, path_output, mecareClaims):
   path_csv = str(path_input) #r'/users/qqi227/Manual_Reviewed_Cases/Input_Manual_Reviewed_Cases'
   path_save_ori = str(path_output)  + '/' +str(user_name) + '/2_RawClaims_perPatient'
   
   isExist = os.path.exists(path_save_ori)
   if not isExist:
      # Create a new directory because it does not exist
      os.makedirs(path_save_ori)
      print("The new directory is created!")
      
   #######################################################################################
   #Get all study id in kcr 
   #######################################################################################
   #file_name = "UH3_KCRnewreviewedcases.csv"
   #completeName = os.path.join(path_csv, file_name)
   #kcr_df = pd.read_csv(completeName, header=0, dtype='string')
   
   #######################################################################################
   #Read Medicare
   #######################################################################################
   file_name = str(mecareClaims) #"medicare_breast_claims_new.csv" 
   completeName = os.path.join(path_csv, file_name)
   medicare_df = pd.read_csv(completeName, header=0, dtype='string')
   flag = 0 ## convert date
   #medicare_df = medicare_df.rename(columns={'patient_id': 'study_id'})
   #medicare_df = medicare_df.rename(columns={'CLAIMS_DATE': 'claims_date'})
   ############################################
   # check date
   ############################################
   if flag == 1:
       medicare_df = convert_SAS_Excel_date(medicare_df, 'claims_date')
   
   #######################################################################################
   #Read medicaid
   #######################################################################################
   
   
   #path_save = r'/users/qqi227/Rewrite-dataProcessing/Results_QQ/Medicare'
   label = 'Medicare'
   path_save = os.path.join(path_save_ori, label)
   isExist = os.path.exists(path_save)
   if not isExist:
      # Create a new directory because it does not exist
      os.makedirs(path_save)
      print("The new directory is created!")
   GetPerPatientData(medicare_df, "medicare_claims", path_save)
   
   print("Step 2 only Medicare done")


def Step2_GetPerPatientData_Medicaid_HealthClaims2(user_name, path_input, path_output, mecaidClaims, mecaidClaims2):
   path_csv = str(path_input) #r'/users/qqi227/Manual_Reviewed_Cases/Input_Manual_Reviewed_Cases'
   path_save_ori = str(path_output)  + '/' +str(user_name) + '/2_RawClaims_perPatient'
   
   isExist = os.path.exists(path_save_ori)
   if not isExist:
      # Create a new directory because it does not exist
      os.makedirs(path_save_ori)
      print("The new directory is created!")
      
   #######################################################################################
   #Get all study id in kcr 
   #######################################################################################
   #file_name = "UH3_KCRnewreviewedcases.csv"
   #completeName = os.path.join(path_csv, file_name)
   #kcr_df = pd.read_csv(completeName, header=0, dtype='string')
   
   #######################################################################################
   #Read Medicare
   #######################################################################################
   
   #######################################################################################
   #Read medicaid
   #######################################################################################
   file_name = str(mecaidClaims) #"medicaid_breast_claims_new.csv" 
   completeName = os.path.join(path_csv, file_name)
   medicaid_health_df = pd.read_csv(completeName, header=0, dtype='string')
   #medicaid_health_df = medicaid_health_df.rename(columns={'patient_id': 'study_id'})
   
   file_name = str(mecaidClaims2) #"medicaid_breast_Rxclaims_new.csv" 
   completeName = os.path.join(path_csv, file_name)
   medicaid_pharm_df = pd.read_csv(completeName, header=0, dtype='string')
   #medicaid_pharm_df = medicaid_pharm_df.rename(columns={'patient_id': 'study_id'})
   
   #path_save = r'/users/qqi227/Rewrite-dataProcessing/Results_QQ/Medicaid_HealthClaims'
   label = 'Medicaid_HealthClaims'
   path_save = os.path.join(path_save_ori, label)
   
   isExist = os.path.exists(path_save)
   if not isExist:
      # Create a new directory because it does not exist
      os.makedirs(path_save)
      print("The new directory is created!")
   GetPerPatientData(medicaid_health_df, "medicaid_healthclaims", path_save)
   
   #path_save = r'/users/qqi227/Rewrite-dataProcessing/Results_QQ/Medicaid_PharmClaims'
   label = 'Medicaid_PharmClaims'
   path_save = os.path.join(path_save_ori, label)
   isExist = os.path.exists(path_save)
   if not isExist:
      # Create a new directory because it does not exist
      os.makedirs(path_save)
      print("The new directory is created!")
   GetPerPatientData(medicaid_pharm_df, "medicaid_pharmclaims", path_save)

   
   print("Step 2 only Medicaid done")
      