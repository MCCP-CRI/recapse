#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 21:58:45 2023

@author: lucasliu
"""

from Ultility_Funcs.DataLoader1 import load_rdata
from Ultility_Funcs.DataLoader1 import load_pythondata
from Ultility_Funcs.TrainTest_Funcs import prediction, patient_level_prediction
from Ultility_Funcs.Performance_Func import compute_performance_binary,compute_month_diff_perf
import pandas as pd
from functools import reduce
import joblib
import os
import argparse


if __name__ == '__main__':
    ############################################################################
    #Argments parser
    ############################################################################
    my_parser = argparse.ArgumentParser(allow_abbrev=False)  #Construct the argument parser

    my_parser.add_argument("-fs" , type = str ,  required=True, help="Feature set (e.g., 'CCSandVAL2nd', 'CCSandDM3SPE')")
    my_parser.add_argument("-sc" , type = str ,  required=True, help="SBCE definition (e.g., use 'SBCE' if considered the First primary BC related death patients as SBCE, if not, use 'SBCE_Excluded_DeathPts')")
    my_parser.add_argument("-sm" , type = str ,  required=True, help="Selected Model (e.g.TopF_Model or Full_Model)")
    my_parser.add_argument("-indir" , type = str , required=False, default="./", help="The path to your input files of preprocessed claim data and patient-level characteristics Excel files, default is current folder. (e.g., /home/model/input)")
    my_parser.add_argument("-outdir" , type = str , required=False, default="./", help="The path to your output file, default is current folder. (e.g., /home/model/output)")
    my_parser.add_argument("-modeldir" , type = str , required=False, default="./Saved_XGBoost", help="The path to saved XGBoost model folders, default is ./Saved_XGBoost. (e.g., /home/model/Saved_XGBoost)")
    my_parser.add_argument("-inputname" , type = str ,  required=False, default="All_11E_CCSandVAL2nd.pkl", help="Name of the input PKL file (e.g. default is 'All_11E_CCSandVAL2nd.pkl')")
    my_parser.add_argument("-chrname" , type = str ,  required=False, default="8_PatientLevel_char_WithPossibleMonthsHasNoCodes.xlsx", help="The patient-level XLSX files that contains characteristics features. (e.g. default is PatientLevel_char_WithPossibleMonthsHasNoCodes.xlsx)")
    my_parser.add_argument("-method" , type = int ,  required=False, default=int(0), help="0 for both patient- and month-level prediction, 1 for only patient-level prediction, and 2 for only month-level prediction")
    my_parser.add_argument("-cutoff" , type = float ,  required=False, default="0.5", help="The cutoff used to determine SBCE patients. The cutoff ranges from 0.1 to 0.9, values exceeding one decimal place will be rounded to one decimal place (e.g., 0.6 means the predicted probability >=0.6 will be considered as SBCE patient)")

    args = vars(my_parser.parse_args())       # Parse the argument
    ####################################################################################
    #Command line input or mannual input
    ####################################################################################
    #location = 'Local' #args['loc']  
    feature_sets = args['fs']
    SBCE_col = args['sc']
    model_name = 'XGB' #args['mn']
    ds_indxes = int(3) #args['ds']
    selected_model = args['sm']
    search_alg = 'Grid' #args['ps']
    train_sample_type = 'nonobv' #args['ts']
    #path_input = args['indir']
    path_output = "prediction_results" #args['outdir']
    input_name = args['inputname']
    cutoff_ori = args['cutoff']
    method = args['method']
    outPath = args['outdir']
    inPath = args['indir']
    modelPath = args['modeldir']

    #Data dir
    data_dir1 = inPath + "/"
    data_dir2 = inPath + "/" #inpuit of chr file
    data_dir3 = modelPath + "/" +feature_sets + "/" +  SBCE_col + "/" + model_name + "/" + "DS" + str(ds_indxes) + '/' + train_sample_type + '/' +  search_alg + '/'
    data_dir4 = data_dir3 + 'Saved_Model/' + selected_model + "/"


    outdir = outPath + '/' + SBCE_col + "/" +selected_model + "/"

    if not os.path.exists(outdir):
        # Create a new directory because it does not exist
        os.makedirs(outdir)
        print("The new directory is created!")

        ####################
    # check parameters #
    ####################
    cutoff = round(cutoff_ori, 1)
    if cutoff != cutoff_ori:
        print("The cutoff value exceeding two decimal places will be rounded to one decimal places, now using cutoff of ", cutoff)
    if cutoff >= 1 or cutoff <0:
        raise ValueError("The cutoff value should be larger than 0 and smaller than 1")
    if method > 2:
        raise ValueError("Parameter -method must be 0, 1 or 2 (0 for both patient- and month-level prediction, 1 for only patient-level prediction, and 2 for only month-level prediction)")

    if not isinstance(method, int):
        raise ValueError("Parameter -method must be an integer")
    if selected_model not in ["TopF_Model", "Full_Model"]:
        raise ValueError("Wrong value for -sm, please use TopF_Model or Full_Model")
    if feature_sets not in ['CCSandVAL2nd', 'CCSandDM3SPE']:
        raise ValueError("Wrong value for -sm, please use CCSandVAL2nd or CCSandDM3SPE")
    if SBCE_col not in ['SBCE', 'SBCE_Excluded_DeathPts']:
        raise ValueError("Wrong value for -sm, please use SBCE or SBCE_Excluded_DeathPts")



    ####################################################################################################
    #1. Load data 
    ####################################################################################################
    #Load test data
    test_X1, test_ID1 = load_pythondata(data_dir1,input_name) #load_rdata(data_dir1,'test_neg_data.rda','test_neg_df',label_col)
    test_X = test_X1
    test_ID = test_ID1

    ################################################################################
    #2. Prediction
    ################################################################################       
    #Load model 
    if selected_model == "TopF_Model":
        trained_model = joblib.load(data_dir4 + model_name + "_TopFeature_model.pkl") #topFmodel
        import_features_df = pd.read_csv(data_dir4 + "importance.csv")
        import_features  = list(import_features_df['Feature'])
        test_X = test_X[import_features]
    elif selected_model == "Full_Model":
        trained_model = joblib.load(data_dir4 + model_name + "_Fullmodel.pkl") #Fullmodel

    #Prediction month-level
    #print(trained_model)
    if method == 0 or method == 2:
        pred_df_m = prediction(trained_model,test_X,test_ID,cutoff)
        pred_df_m.to_csv(outdir + 'monthlevel_prediction.csv', index = False)


    #Prediction Patient-level (3month consecutive method)
    thres_list = [cutoff]#[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
    pred_df_p_list = []
    for thres in thres_list :
        pred_df_p  = patient_level_prediction(pred_df_m,thres,pred_method="3month")
        sufix_col =  str(thres).replace('.','')
        pred_df_p.rename(columns = {'pred_label': 'pred_label_th' + sufix_col,
                                    'pred_month': 'pred_month_th' + sufix_col,
                                    'RAW_Month_Diff': 'RAW_Month_Diff_th' + sufix_col,
                                    'ABS_Month_Diff': 'ABS_Month_Diff_th' + sufix_col},
                         inplace = True)
        pred_df_p_list.append(pred_df_p)


    pred_df_p_all = reduce(lambda x, y: pd.merge(x, y, on = ['study_id',]), pred_df_p_list)
    pred_df_p_all.to_csv(outdir + 'patientlevel_prediction.csv', index = False)

    ### new added code by Q.Q.
    #Load SBCE month label patient -level
    pts_level_char_df = pd.read_excel(data_dir2 + str(chr_name))

    #pts_level_char_df['study_id'] = 'ID' + pts_level_char_df['study_id'].astype(str)
    pts_level_char_df = pts_level_char_df.astype({'study_id': 'string'})

    merged_df = pd.merge(pts_level_char_df, pred_df_p_all, on='study_id', how='outer')
    merged_df.to_csv(outdir + 'patientlevel_prediction_merged_pt_chr.csv', index = False)

    print("Prediction finished")


