# -*- coding: utf-8 -*-
"""
Created on 10/17/2023

@author: Qi Qiao
"""
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
import argparse

from Ultility_Funcs_data.Recapse_Ultility import *
from Ultility_Funcs_data.Step1_HPC_GetStudyIDSource import *
from Ultility_Funcs_data.Step2_GetPerPatientData_Medicaid_HealthClaims import *
from Ultility_Funcs_data.Step3A_HPC_Get_PerMonthData_withCleanCodes import *
from Ultility_Funcs_data.Step3B_HPC_Get_PerMonthData_withCleanCodes_onlymedicare import *
from Ultility_Funcs_data.Step3C_HPC_Get_PerMonthData_withCleanCodes_onlymedicaid import *
from Ultility_Funcs_data.Step4A_Get_Cancer_SiteDateType import *
from Ultility_Funcs_data.Step4B_GetEventType_addNewothers import *
from Ultility_Funcs_data.Step5A_GetEnrollmentMonths import *
from Ultility_Funcs_data.Step5B_GetPredictionMonths import *
from Ultility_Funcs_data.Step8A_Get_PatientLevelCharateristics import *
from Ultility_Funcs_data.Step10A_Get_PerPatient_UniqueCodes_AllEnrolls import *
from Ultility_Funcs_data.Step10B_Get_PerMonth_CCSDiag_AllEnrolls import *
from Ultility_Funcs_data.Step10C_Get_PerMonth_CCSProc_AllEnrolls import *
from Ultility_Funcs_data.Step10D_Get_PerMonth_DM3SPE_AllEnrolls import *
from Ultility_Funcs_data.Step10F_Get_PerMonth_VAL2NDROOT_AllEnrolls import *
from Ultility_Funcs_data.Step11A_Get_ModelReady_SelectedGroupFeature import *
from Ultility_Funcs_data.Step11B_Get_ModelReady_BinaryCharFeatures import *
from Ultility_Funcs_data.Step11C_Get_ModelReady_TransformationFeature import *
from Ultility_Funcs_data.Step11D_Get_ModelReady_Combed_Features import *
from Ultility_Funcs_data.Step11E_merge_all import *

if __name__ == '__main__':
    ############################################################################
    #Argments parser
    ############################################################################
    my_parser = argparse.ArgumentParser(allow_abbrev=False)  #Construct the argument parser

    my_parser.add_argument("-user" , type = str , required=True, help="Username (e.g., Jane)")
    my_parser.add_argument("-numdata" , type = str , required=True, help="0 for both, 1 for only Medicare, 2 for only Medicaid or other claims")
    my_parser.add_argument("-indir" , type = str , required=False, default="./", help="Path to your input file; default is the current folder. (e.g., /home/Jane/input)")
    my_parser.add_argument("-outdir" , type = str , required=False, default="./", help="Path to your output file; default is current folder. (e.g., /home/Jane/output)")
    my_parser.add_argument("-metacsv" , type = str , required=True, default="metadata.csv", help="Name of your meta CSV file; default is metadata.csv")
    my_parser.add_argument("-mecareClaims" , type = str , required=False, default="medicare_claims_new.csv", help="Name of your Medicare claim CSV file; default is medicare_claims_new.csv")
    my_parser.add_argument("-mecareEnroll" , type = str , required=False, default="medicare_enroll_new.csv", help="Name of your Medicare enrollment CSV file; default is medicare_enroll_new.csv")
    my_parser.add_argument("-mecaidClaims" , type = str , required=False, default="medicaid_claims_new.csv", help="Name of your Medicaid claim or other insurance claim CSV file; default is medicaid_claims_new.csv")
    my_parser.add_argument("-mecaidClaims2" , type = str , required=False, default="medicaid_Rxclaims_new.csv", help="Name of your Medicaid or other insurance claim CSV file that contains drug features; default is medicaid_Rxclaims_new.csv")
    my_parser.add_argument("-mecaidEnroll" , type = str , required=False, default="medicaid_enroll_new.csv", help="Name of your Medicaid or other insurance enrollment CSV file; default is medicaid_enroll_new.csv")
    my_parser.add_argument("-mld" , type = int , required=False, help="Month length of Medicaid or other insurance enrollment (e.g., 240 if your Medicaid enrollment file has 240 months)")
    my_parser.add_argument("-mle" , type = int , required=False, help="Month length of Medicare enrollment (e.g., 240 if your Medicare enrollment file has 240 months)")
    my_parser.add_argument("-sd" , type = str , required=False, help="Start date of Medicaid enrollment (format: YYYY-MM-DD)")
    my_parser.add_argument("-se" , type = str , required=False, help="Start date of Medicare enrollment (format: YYYY-MM-DD)")
    my_parser.add_argument("-dc" , type = str , required=False, help="Drug Code, use VAL_2ND for short GNN drug grouped features, and use DM3_SPE for DM3 specific drug. (e.g., VAL_2ND or DM3_SPE)")
    ##my_parser.add_argument("-site" , type = int , required=True, help="how many site columns (e.g., use 2 if you have 'site_o1' and 'site_o2')")

    args = vars(my_parser.parse_args())       # Parse the argument
    ####################################################################################
    #Command line input or mannual input
    ####################################################################################
    user_name = args['user']
    num_data = args['numdata']
    indir = args['indir']
    outdir = args['outdir']
    metacsv = args['metacsv']
    mecareClaims = args['mecareClaims']
    mecareEnroll = args['mecareEnroll']
    mecaidClaims = args['mecaidClaims']
    mecaidClaims2 = args['mecaidClaims2']
    mecaidEnroll = args['mecaidEnroll']
    #site_num = args['site']
    month_len_medicaid= args['mld']
    month_len_medicare= args['mle']
    start_medicaid= args['sd']
    start_medicare= args['se']
    drug_code= args['dc']


    ########################
    #check parameters first#
    ########################
    check_numdata(num_data)
    check_matched_files(num_data, mecareClaims, mecareEnroll, mecaidClaims, mecaidClaims2, mecaidEnroll)

    if num_data == "0":
        check_both(month_len_medicaid, month_len_medicare, start_medicaid, start_medicare)
        int_check(month_len_medicaid)
        int_check(month_len_medicare)

    if num_data == "1":
        check_medicare1(month_len_medicaid, month_len_medicare, start_medicaid, start_medicare)
        int_check(month_len_medicare)

    if num_data == "2":
        check_medicaid2(month_len_medicaid, month_len_medicare, start_medicaid, start_medicare)
        int_check(month_len_medicaid)

    ##########################
    #start preprocessing data#
    ##########################
    if num_data == "0":
        Step1_GetStudyIDSource(user_name, indir, outdir, metacsv, mecareClaims, mecaidClaims, mecaidClaims2)
        Step2_GetPerPatientData_Medicaid_HealthClaims(user_name, indir, outdir, mecareClaims, mecaidClaims, mecaidClaims2)
        Step3A_HPC_Get_PerMonthData_withCleanCodes(user_name, indir, outdir, mecareClaims, mecaidClaims, mecaidClaims2, drug_code)
    elif num_data == "1":
        Step1_GetStudyIDSource1(user_name, indir, outdir, metacsv, mecareClaims)
        Step2_GetPerPatientData_Medicaid_HealthClaims1(user_name, indir, outdir, mecareClaims)
        Step3B_HPC_Get_PerMonthData_withCleanCodes_onlymedicare(user_name, indir, outdir, mecareClaims, drug_code)
    elif num_data == "2":
        Step1_GetStudyIDSource2(user_name, indir, outdir, metacsv, mecaidClaims, mecaidClaims2)
        Step2_GetPerPatientData_Medicaid_HealthClaims2(user_name, indir, outdir, mecaidClaims, mecaidClaims2)
        Step3C_HPC_Get_PerMonthData_withCleanCodes_onlymedicaid(user_name, indir, outdir, mecaidClaims, mecaidClaims2, drug_code)
    Step4A_Get_Cancer_SiteDateType(user_name, indir, outdir, metacsv)
    Step4B_GetEventType_addNewothers(user_name, indir, outdir, metacsv)
    ## No step4c becuase we do not have labels
    if num_data == "0":
        Step5A_GetEnrollmentMonths(user_name, indir, outdir, mecaidEnroll, month_len_medicaid, start_medicaid, mecareEnroll, month_len_medicare, start_medicare)
    elif num_data == "1":
        Step5A_GetEnrollmentMonths1(user_name, indir, outdir, mecareEnroll, month_len_medicare, start_medicare)
    elif num_data == "2":
        Step5A_GetEnrollmentMonths2(user_name, indir, outdir, mecaidEnroll, month_len_medicaid, start_medicaid)
      
    Step5B_GetPredictionMonths(user_name, indir, outdir, metacsv)
    ## skip 5C due to no label
    Step8A_Get_PatientLevelCharateristics(user_name, indir, outdir,metacsv)
    ## skip 8B_get_labels.py 8C_merge_8Aand4B.py
    Step10A_Get_PerPatient_UniqueCodes_AllEnrolls(user_name, outdir)
    Step10B_Get_PerMonth_CCSDiag_AllEnrolls(user_name, indir, outdir)
    Step10C_Get_PerMonth_CCSProc_AllEnrolls(user_name, indir, outdir)
    if drug_code == 'DM3_SPE':
        Step10D_Get_PerMonth_DM3SPE_AllEnrolls(user_name, indir, outdir)
    else:
        Step10F_Get_PerMonth_VAL2NDROOT_AllEnrolls(user_name, indir, outdir)
    Step11A_Get_ModelReady_SelectedGroupFeature(user_name, indir, outdir, drug_code)
    Step11B_Get_ModelReady_BinaryCharFeatures(user_name, outdir)
    Step11C_Get_ModelReady_TransformationFeature(user_name, outdir, drug_code)
    Step11D_Get_ModelReady_Combed_Features(user_name, outdir, drug_code)
    Step11E_merge_all(user_name, outdir, drug_code)
    
    













