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

def Step11A_Get_ModelReady_SelectedGroupFeature(user_name, path_input, path_output,drug_code):

    ### HPC
    path_diag = str(path_output) + "/" +str(user_name) + '/10B_CCSDiagFeature_inValidMonth'
    path_proc = str(path_output) + "/" +str(user_name) + '/10C_CCSProcFeature_inValidMonth'
    path_drug1 = str(path_output) + "/" +str(user_name) + '/10D_DM3SPEFeature_inValidMonth'
    path_drug2 = str(path_output) + "/" +str(user_name) + '/10F_VAL2NDFeature_inValidMonth'
    path_feat = str(path_input) #r'/users/qqi227/Manual_Reviewed_Cases/Results/10H_Selected_Grps'
    path_save1 = str(path_output) + "/" +str(user_name) + '/11A_ModelReady_GrpFeature_CCSandDM3SPE'
    path_save2 = str(path_output) + "/" +str(user_name) + '/11A_ModelReady_GrpFeature_CCSandVAL2ND'
    path_ID = str(path_output) + "/" +str(user_name) + '/1_ID_Sources_Info'
    #path_site = r'/Users/qiqiao/Desktop/dp/Rewrite'
    
    ################################################################################ 
    ##0. CHANGE here, for drug groups
    ################################################################################ 
    #drug_code = 'VAL_2ND' #default DM3SPEFeature, VAL_2ND --> VAL2NDFeature
    if drug_code == "DM3_SPE" :  #VAL_2ND
        path_save = path_save1
        path_drug = path_drug1
        file_name_drug = "Selected_DM3SPEDrug_Unique_Grps.xlsx"
    else:
        path_save = path_save2
        path_drug = path_drug2
        file_name_drug = "Selected_VAL2ndDrug_Unique_Grps.xlsx"
        
           
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
    
    
    ################################################################################
    #2.Load group df
    ################################################################################
    file_name = "Selected_CCSDiag_Unique_Grps.xlsx"
    completeName = os.path.join(path_feat, file_name)
    modelready_grps_df1 = pd.read_excel(completeName,header=0, index_col=False)#, dtype={'CODE': str})
    
    file_name = "Selected_CCSProc_Unique_Grps.xlsx"
    completeName = os.path.join(path_feat, file_name)
    modelready_grps_df2 = pd.read_excel(completeName,header=0, index_col=False)#, dtype={'CODE': str})
    
    ####drug
    completeName = os.path.join(path_feat, file_name_drug)
    modelready_grps_df3 = pd.read_excel(completeName,header=0, index_col=False)#, dtype={'CODE': str})
    
    
    modelready_Diag_features = modelready_grps_df1.sort_values(by=['Selected_Grps'], ignore_index=True)
    modelready_Proc_features = modelready_grps_df2.sort_values(by=['Selected_Grps'], ignore_index=True)
    modelready_Drug_features = modelready_grps_df3.sort_values(by=['Selected_Grps'], ignore_index=True)
    
    list_feat = modelready_Diag_features['Selected_Grps'].values.tolist() + modelready_Proc_features['Selected_Grps'].values.tolist() + modelready_Drug_features['Selected_Grps'].values.tolist()
    
    if drug_code == "DM3_SPE" :
        col_name_ordered = ["study_id","Month_Start","CCS_DIAG_10","CCS_DIAG_101","CCS_DIAG_102","CCS_DIAG_103","CCS_DIAG_104","CCS_DIAG_105","CCS_DIAG_106","CCS_DIAG_108","CCS_DIAG_109","CCS_DIAG_110","CCS_DIAG_114","CCS_DIAG_117","CCS_DIAG_118","CCS_DIAG_120","CCS_DIAG_121","CCS_DIAG_122","CCS_DIAG_125","CCS_DIAG_126","CCS_DIAG_127","CCS_DIAG_128","CCS_DIAG_130","CCS_DIAG_131","CCS_DIAG_133","CCS_DIAG_134","CCS_DIAG_138","CCS_DIAG_140","CCS_DIAG_141","CCS_DIAG_143","CCS_DIAG_146","CCS_DIAG_149","CCS_DIAG_151","CCS_DIAG_153","CCS_DIAG_154","CCS_DIAG_155","CCS_DIAG_157","CCS_DIAG_158","CCS_DIAG_159","CCS_DIAG_160","CCS_DIAG_161","CCS_DIAG_163","CCS_DIAG_167","CCS_DIAG_168","CCS_DIAG_173","CCS_DIAG_175","CCS_DIAG_19","CCS_DIAG_197","CCS_DIAG_198","CCS_DIAG_199","CCS_DIAG_2","CCS_DIAG_200","CCS_DIAG_203","CCS_DIAG_204","CCS_DIAG_205","CCS_DIAG_206","CCS_DIAG_207","CCS_DIAG_208","CCS_DIAG_209","CCS_DIAG_21","CCS_DIAG_211","CCS_DIAG_212","CCS_DIAG_23","CCS_DIAG_230","CCS_DIAG_231","CCS_DIAG_232","CCS_DIAG_235","CCS_DIAG_236","CCS_DIAG_237","CCS_DIAG_238","CCS_DIAG_239","CCS_DIAG_24","CCS_DIAG_242","CCS_DIAG_244","CCS_DIAG_245","CCS_DIAG_246","CCS_DIAG_247","CCS_DIAG_250","CCS_DIAG_251","CCS_DIAG_252","CCS_DIAG_253","CCS_DIAG_254","CCS_DIAG_255","CCS_DIAG_256","CCS_DIAG_257","CCS_DIAG_258","CCS_DIAG_259","CCS_DIAG_3","CCS_DIAG_4","CCS_DIAG_41","CCS_DIAG_42","CCS_DIAG_43","CCS_DIAG_44","CCS_DIAG_45","CCS_DIAG_47","CCS_DIAG_48","CCS_DIAG_49","CCS_DIAG_50","CCS_DIAG_51","CCS_DIAG_52","CCS_DIAG_53","CCS_DIAG_55","CCS_DIAG_58","CCS_DIAG_59","CCS_DIAG_62","CCS_DIAG_63","CCS_DIAG_651","CCS_DIAG_653","CCS_DIAG_657","CCS_DIAG_659","CCS_DIAG_661","CCS_DIAG_663","CCS_DIAG_7","CCS_DIAG_81","CCS_DIAG_83","CCS_DIAG_84","CCS_DIAG_85","CCS_DIAG_86","CCS_DIAG_87","CCS_DIAG_88","CCS_DIAG_89","CCS_DIAG_90","CCS_DIAG_91","CCS_DIAG_92","CCS_DIAG_93","CCS_DIAG_94","CCS_DIAG_95","CCS_DIAG_96","CCS_DIAG_97","CCS_DIAG_98","CCS_DIAG_99","CCS_DIAG_NA","CCS_PROC_130","CCS_PROC_15","CCS_PROC_155","CCS_PROC_163","CCS_PROC_165","CCS_PROC_166","CCS_PROC_167","CCS_PROC_170","CCS_PROC_171","CCS_PROC_174","CCS_PROC_177","CCS_PROC_178","CCS_PROC_179","CCS_PROC_180","CCS_PROC_182","CCS_PROC_192","CCS_PROC_193","CCS_PROC_196","CCS_PROC_197","CCS_PROC_198","CCS_PROC_200","CCS_PROC_201","CCS_PROC_202","CCS_PROC_203","CCS_PROC_205","CCS_PROC_206","CCS_PROC_207","CCS_PROC_209","CCS_PROC_211","CCS_PROC_213","CCS_PROC_214","CCS_PROC_217","CCS_PROC_218","CCS_PROC_220","CCS_PROC_222","CCS_PROC_224","CCS_PROC_226","CCS_PROC_227","CCS_PROC_228","CCS_PROC_231","CCS_PROC_232","CCS_PROC_233","CCS_PROC_234","CCS_PROC_235","CCS_PROC_236","CCS_PROC_237","CCS_PROC_239","CCS_PROC_240","CCS_PROC_241","CCS_PROC_243","CCS_PROC_38","CCS_PROC_39","CCS_PROC_54","CCS_PROC_63","CCS_PROC_67","CCS_PROC_7","CCS_PROC_70","CCS_PROC_76","CCS_PROC_998","CCS_PROC_999","CCS_PROC_NA","DM3_SPE_antibacterial","DM3_SPE_anticoagulant","DM3_SPE_antidepressant","DM3_SPE_antiemetic","DM3_SPE_antifungal","DM3_SPE_antihistamine","DM3_SPE_antiviral","DM3_SPE_anxiety","DM3_SPE_aromatase","DM3_SPE_asthma","DM3_SPE_bladder","DM3_SPE_cholesterol","DM3_SPE_diabetes","DM3_SPE_diuretic","DM3_SPE_electrolyte","DM3_SPE_gastric","DM3_SPE_HTN","DM3_SPE_laxative","DM3_SPE_muscle relaxant","DM3_SPE_NA","DM3_SPE_non-opioid","DM3_SPE_opioid","DM3_SPE_seizure","DM3_SPE_SERM","DM3_SPE_sleep","DM3_SPE_steroid","DM3_SPE_thyroid"]
    else:
        col_name_ordered = ["study_id","Month_Start","CCS_DIAG_10","CCS_DIAG_101","CCS_DIAG_102","CCS_DIAG_103","CCS_DIAG_104","CCS_DIAG_105","CCS_DIAG_106","CCS_DIAG_108","CCS_DIAG_109","CCS_DIAG_110","CCS_DIAG_114","CCS_DIAG_117","CCS_DIAG_118","CCS_DIAG_120","CCS_DIAG_121","CCS_DIAG_122","CCS_DIAG_125","CCS_DIAG_126","CCS_DIAG_127","CCS_DIAG_128","CCS_DIAG_130","CCS_DIAG_131","CCS_DIAG_133","CCS_DIAG_134","CCS_DIAG_138","CCS_DIAG_140","CCS_DIAG_141","CCS_DIAG_143","CCS_DIAG_146","CCS_DIAG_149","CCS_DIAG_151","CCS_DIAG_153","CCS_DIAG_154","CCS_DIAG_155","CCS_DIAG_157","CCS_DIAG_158","CCS_DIAG_159","CCS_DIAG_160","CCS_DIAG_161","CCS_DIAG_163","CCS_DIAG_167","CCS_DIAG_168","CCS_DIAG_173","CCS_DIAG_175","CCS_DIAG_19","CCS_DIAG_197","CCS_DIAG_198","CCS_DIAG_199","CCS_DIAG_2","CCS_DIAG_200","CCS_DIAG_203","CCS_DIAG_204","CCS_DIAG_205","CCS_DIAG_206","CCS_DIAG_207","CCS_DIAG_208","CCS_DIAG_209","CCS_DIAG_21","CCS_DIAG_211","CCS_DIAG_212","CCS_DIAG_23","CCS_DIAG_230","CCS_DIAG_231","CCS_DIAG_232","CCS_DIAG_235","CCS_DIAG_236","CCS_DIAG_237","CCS_DIAG_238","CCS_DIAG_239","CCS_DIAG_24","CCS_DIAG_242","CCS_DIAG_244","CCS_DIAG_245","CCS_DIAG_246","CCS_DIAG_247","CCS_DIAG_250","CCS_DIAG_251","CCS_DIAG_252","CCS_DIAG_253","CCS_DIAG_254","CCS_DIAG_255","CCS_DIAG_256","CCS_DIAG_257","CCS_DIAG_258","CCS_DIAG_259","CCS_DIAG_3","CCS_DIAG_4","CCS_DIAG_41","CCS_DIAG_42","CCS_DIAG_43","CCS_DIAG_44","CCS_DIAG_45","CCS_DIAG_47","CCS_DIAG_48","CCS_DIAG_49","CCS_DIAG_50","CCS_DIAG_51","CCS_DIAG_52","CCS_DIAG_53","CCS_DIAG_55","CCS_DIAG_58","CCS_DIAG_59","CCS_DIAG_62","CCS_DIAG_63","CCS_DIAG_651","CCS_DIAG_653","CCS_DIAG_657","CCS_DIAG_659","CCS_DIAG_661","CCS_DIAG_663","CCS_DIAG_7","CCS_DIAG_81","CCS_DIAG_83","CCS_DIAG_84","CCS_DIAG_85","CCS_DIAG_86","CCS_DIAG_87","CCS_DIAG_88","CCS_DIAG_89","CCS_DIAG_90","CCS_DIAG_91","CCS_DIAG_92","CCS_DIAG_93","CCS_DIAG_94","CCS_DIAG_95","CCS_DIAG_96","CCS_DIAG_97","CCS_DIAG_98","CCS_DIAG_99","CCS_DIAG_NA","CCS_PROC_130","CCS_PROC_15","CCS_PROC_155","CCS_PROC_163","CCS_PROC_165","CCS_PROC_166","CCS_PROC_167","CCS_PROC_170","CCS_PROC_171","CCS_PROC_174","CCS_PROC_177","CCS_PROC_178","CCS_PROC_179","CCS_PROC_180","CCS_PROC_182","CCS_PROC_192","CCS_PROC_193","CCS_PROC_196","CCS_PROC_197","CCS_PROC_198","CCS_PROC_200","CCS_PROC_201","CCS_PROC_202","CCS_PROC_203","CCS_PROC_205","CCS_PROC_206","CCS_PROC_207","CCS_PROC_209","CCS_PROC_211","CCS_PROC_213","CCS_PROC_214","CCS_PROC_217","CCS_PROC_218","CCS_PROC_220","CCS_PROC_222","CCS_PROC_224","CCS_PROC_226","CCS_PROC_227","CCS_PROC_228","CCS_PROC_231","CCS_PROC_232","CCS_PROC_233","CCS_PROC_234","CCS_PROC_235","CCS_PROC_236","CCS_PROC_237","CCS_PROC_239","CCS_PROC_240","CCS_PROC_241","CCS_PROC_243","CCS_PROC_38","CCS_PROC_39","CCS_PROC_54","CCS_PROC_63","CCS_PROC_67","CCS_PROC_7","CCS_PROC_70","CCS_PROC_76","CCS_PROC_998","CCS_PROC_999","CCS_PROC_NA","VAL_2ND_5-ht3 Receptor Antagonists","VAL_2ND_Ace Inhibitors","VAL_2ND_Alpha-beta Blockers","VAL_2ND_Aminopenicillins","VAL_2ND_Angiotensin Ii Receptor Antagonists","VAL_2ND_Anti-infective Agents - Misc.","VAL_2ND_Anti-infective Misc. - Combinations","VAL_2ND_Antianxiety Agents - Misc.","VAL_2ND_Antibiotics - Topical","VAL_2ND_Anticonvulsants - Misc.","VAL_2ND_Antiemetics - Anticholinergic","VAL_2ND_Antifungals - Topical","VAL_2ND_Antihistamines - Non-sedating","VAL_2ND_Antihistamines - Phenothiazines","VAL_2ND_Antihypertensive Combinations","VAL_2ND_Antimetabolites","VAL_2ND_Antineoplastic - Hormonal And Related Agents","VAL_2ND_Antiperistaltic Agents","VAL_2ND_Azithromycin","VAL_2ND_Benzodiazepines","VAL_2ND_Beta Blockers Cardio-selective","VAL_2ND_Biguanides","VAL_2ND_Bone Density Regulators","VAL_2ND_Calcium Channel Blockers","VAL_2ND_Central Muscle Relaxants","VAL_2ND_Cephalosporins - 1st Generation","VAL_2ND_Cephalosporins - 2nd Generation","VAL_2ND_Cephalosporins - 3rd Generation","VAL_2ND_Corticosteroids - Topical","VAL_2ND_Coumarin Anticoagulants","VAL_2ND_Fluoroquinolones","VAL_2ND_Glucocorticosteroids","VAL_2ND_H-2 Antagonists","VAL_2ND_Heparins And Heparinoid-like Agents","VAL_2ND_Herpes Agents","VAL_2ND_Hmg Coa Reductase Inhibitors","VAL_2ND_Imidazole-related Antifungals","VAL_2ND_Insulin","VAL_2ND_Lincosamides","VAL_2ND_Local Anesthetics - Topical","VAL_2ND_Loop Diuretics","VAL_2ND_NA","VAL_2ND_Nasal Steroids","VAL_2ND_Nitrates","VAL_2ND_Non-barbiturate Hypnotics","VAL_2ND_Nonsteroidal Anti-inflammatory Agents (nsaids)","VAL_2ND_Ophthalmic Anti-infectives","VAL_2ND_Ophthalmic Steroids","VAL_2ND_Ophthalmics - Misc.","VAL_2ND_Opioid Agonists","VAL_2ND_Opioid Combinations","VAL_2ND_Penicillin Combinations","VAL_2ND_Phenothiazines","VAL_2ND_Proton Pump Inhibitors","VAL_2ND_Selective Serotonin Reuptake Inhibitors (ssris)","VAL_2ND_Serotonin Modulators","VAL_2ND_Serotonin-norepinephrine Reuptake Inhibitors (snris)","VAL_2ND_Sympathomimetics","VAL_2ND_Tetracyclines","VAL_2ND_Thiazides And Thiazide-like Diuretics","VAL_2ND_Thyroid Hormones","VAL_2ND_Urinary Anti-infectives"]
    ########################################################################################################################
    #For each pt, generate a dataframe with all selected group feature as columns
    ########################################################################################################################
    for i in range(len(analysis_IDs)): #
        curr_id = analysis_IDs.iloc[i]
        
        file_name = "ID" + str(curr_id) + "_Month_CCS_DIAG_Feature.xlsx"
        completeName = os.path.join(path_diag, file_name)
        old_perMonth_df1 = pd.read_excel(completeName,header=0, index_col=False)
        
        file_name = "ID" + str(curr_id) + "_Month_CCS_PROC_Feature.xlsx"
        completeName = os.path.join(path_proc, file_name)
        old_perMonth_df2 = pd.read_excel(completeName,header=0, index_col=False)
        old_perMonth_df2 = old_perMonth_df2.iloc[:,3:]
        
        if drug_code == "DM3_SPE" :
            file_name = "ID" + str(curr_id) + "_Month_DM3_SPE_Feature.xlsx"
        else:
            file_name = "ID" + str(curr_id) + "_Month_VAL_2ND_Feature.xlsx"
        completeName = os.path.join(path_drug, file_name)
        old_perMonth_df3 = pd.read_excel(completeName,header=0, index_col=False)
        old_perMonth_df3 = old_perMonth_df3.iloc[:,3:]
        
        frames = [old_perMonth_df1, old_perMonth_df2, old_perMonth_df3]
        old_perMonth_df = pd.concat(frames,axis=1)#, ignore_index=True)
        #old_perMonth_df = old_perMonth_df.loc[:,~old_perMonth_df.T.duplicated(keep='first')]
        
        old_study_id =  old_perMonth_df["study_id"]
        old_Month_Start = old_perMonth_df["Month_Start"]
        
        old_feature_df = old_perMonth_df.iloc[:,3:]
        
        list_feat_all = ["study_id" , "Month_Start"] + list_feat
        
        new_perMonth_df = pd.DataFrame(np.zeros((old_feature_df.shape[0], len(list_feat_all))))
        new_perMonth_df.columns = list_feat_all
        new_perMonth_df['study_id'] = old_study_id
        new_perMonth_df["Month_Start"] = old_Month_Start
        
        old_feat = list(old_feature_df)
        for k in range(len(list_feat)):
            curr_feat = list_feat[k]
            if curr_feat in old_feat:
                new_perMonth_df[curr_feat] = old_perMonth_df[curr_feat]
        new_perMonth_df = new_perMonth_df.reindex(columns=col_name_ordered)
        file_name = "ID" + str(curr_id) + "_Selected_Grp_Features.xlsx"
        completeName = os.path.join(path_save, file_name)
        new_perMonth_df.to_excel(completeName, header = True, index=False)
    
    print('Step 11A done')
                
        
            