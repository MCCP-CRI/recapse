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
import datetime
from datetime import date
from dateutil import relativedelta
import xlrd
from dateutil.relativedelta import relativedelta, MO
import warnings

def change_column_format(kcr_df, column_name):
    for i in range(len(kcr_df)):
        date = kcr_df.loc[kcr_df.index[i],column_name]
        #print(date)
        if date != 'NA':
            #print(date)
            list_date = []
            list_date.append(date)
            new_list = [datetime.datetime.strptime(x,'%m/%d/%y').strftime('%Y-%m-%d') for x in list_date]
            new_date = new_list[0]
            kcr_df.loc[kcr_df.index[i],column_name] = new_date
    return kcr_df

def change_column_format2(kcr_df, column_name):
    for i in range(len(kcr_df)):
        date = kcr_df.loc[kcr_df.index[i],column_name]
        #print(date)
        if not pd.isna(date):
            if len(date) < 10:
                #print(date)
                list_date = []
                list_date.append(date)
                new_list = [datetime.datetime.strptime(x,'%m/%d/%y').strftime('%m/%d/%Y') for x in list_date]
                new_date = new_list[0]
                kcr_df.loc[kcr_df.index[i],column_name] = new_date
    return kcr_df

def change_column_format3(date):
    if len(date) <10:
        list_date = []
        list_date.append(date)
        new_list = [datetime.datetime.strptime(x,'%m/%d/%y').strftime('%m/%d/%Y') for x in list_date]
        new_date = new_list[0]
    else:
        new_date = date
    return new_date
    
    
def convert_SAS_Excel_date(df, col_name):
    #e.g. col_name = 'claims_date'
    for i in range(df.shape[0]):
        curr_date = int(df.loc[df.index[i],col_name]) + int(21916)
        #xl_date = 37165
        # Calling the xldate_as_datetime() function to
        # convert the specified excel serial date into
        # datetime.datetime object
        datetime_date = xlrd.xldate_as_datetime(curr_date, 0)
        
        # Calling the datetime_date.date() function to convert
        # the above returned datetime.datetime object into
        # datetime.date object
        date_object = datetime_date.date()
        
        # Calling the isoformat() function to convert the
        # above returned datetime.date object into the
        # ISO format date string
        string_date = date_object.isoformat()
        
        # Getting the converted date string as output
        #print(string_date)
        convert_date = datetime.datetime.strptime(string_date, "%Y-%m-%d").strftime("%m/%d/%Y")
        df.loc[df.index[i],col_name] = convert_date
    return df


def mtn(x):
    months = {'jan': '01','feb': '02','mar': '03','apr':  '04','may':  '05','jun':'06','jul':'07','aug':'08','sep':'09','oct':'10','nov':'11','dec':'12'
        }
    a = x.strip()[:3].lower()
    return months[a]

def reformat_codes_func(code, min_length):
    if code =='nan' or code =='':
        updated_code = code
    else:
        nchar_code = len(str(code))
        num_0_needed = min_length - nchar_code
        prepend_string = "0"*num_0_needed
        updated_code = prepend_string + str(code)
    
    return updated_code

def get_end_date(start_date):  
    ####input is a dataframe with a shape of (X, 1)  
    end_date = []
    for i in range(len(start_date)):
        yr, mon, _ = start_date.iloc[i,0].split("-")
        if mon < '09':
            mon = "0" + str(int(mon)+1)
        elif mon == '09':
            mon = '10'
        elif mon >= '10' and mon < '12':
            mon = str(int(mon)+1)
        else:
            mon = "01"
            yr = str(int(yr)+1)
        end = yr + '-' +mon + "-01" 
        end_date.append(end)
    end_date = pd.DataFrame(end_date)
    return end_date


def get_end_date2(start_date):    
    yr, mon, _ = start_date.split("-")
    if mon < '09':
        mon = "0" + str(int(mon)+1)
    elif mon == '09':
        mon = '10'
    elif mon >= '10' and mon < '12':
        mon = str(int(mon)+1)
    else:
        mon = "01"
        yr = str(int(yr)+1)
    end = yr + '-' +mon + "-01" 
    return end

def get_date_series(start, end):    
    ###input is a string
    date_series = pd.DataFrame(pd.date_range(str(start),str(end), freq='MS').strftime("%Y-%m-%d"))#.tolist()
    return pd.DataFrame(date_series)

def change_y_m_d(df, types):
    if df.empty:
        df = pd.DataFrame()
    else:
        # format
        format = '%m/%d/%Y'
        if types == 'medicare':
            check_date = df['claims_date']
            for i in range(len(check_date)):
                # convert from string format to datetime format
                # and get the date
                date = check_date.iloc[i]
                new_date = str(datetime.datetime.strptime(date, format).date())
                df.iloc[i,1] = new_date
        else:
            check_date = df['DTE_FIRST_SVC']
            for i in range(len(check_date)):
                # convert from string format to datetime format
                # and get the date
                date = check_date.iloc[i]
                new_date = str(datetime.datetime.strptime(date, format).date())
                df.iloc[i,2] = new_date
    return df

def change_y_m_d2(date):

    format = '%m/%d/%Y'
    new_date = str(datetime.datetime.strptime(date, format).date())
    return new_date  


def add_months_to_date(curr_date, add_months):  ###string date as input
    # adding months to a particular date
    #print('date : ' + str(date(2020, 5, 15)))
    yr = int(curr_date.split("-")[0])
    mon = int(curr_date.split("-")[1])
    day = int(curr_date.split("-")[2])
    new_date = str(date(yr, mon, day) + relativedelta(months= int(add_months)))
    yr = str(new_date.split("-")[0])
    mon = str(new_date.split("-")[1])
    new_date = str(yr) + "-" + str(mon) + "-01"
    #print('new date is : '+str(new_date))
    return new_date    #str(new_date)


def calculate_age(today, born):
    #today = date.today()
    born = date(int(born.split('-')[0]), int(born.split('-')[1]), int(born.split('-')[2])) 
    today = date(int(today.split('-')[0]), int(today.split('-')[1]), int(today.split('-')[2])) 
    delta = today -born
    age = delta.days/365
    #return today.year - born.year - ((today.month, today.day) < (born.month, born.day)) 
    return age 

def calculate_diff_day(today, date_1st):
    #today = date.today()
    date_1st = date(int(date_1st.split('-')[0]), int(date_1st.split('-')[1]), int(date_1st.split('-')[2])) 
    today = date(int(today.split('-')[0]), int(today.split('-')[1]), int(today.split('-')[2])) 
    delta = today - date_1st
    days = delta.days
    #return today.year - born.year - ((today.month, today.day) < (born.month, born.day)) 
    return days


def get_diff_month(month_start, date_dx):
    month_start = date(int(month_start.split('-')[0]), int(month_start.split('-')[1]), int(month_start.split('-')[2])) 
    date_dx = date(int(date_dx.split('-')[0]), int(date_dx.split('-')[1]), int(date_dx.split('-')[2])) 
    delta = month_start - date_dx
    res_months = delta.days/30
    # Get the relativedelta between two dates
    #delta = relativedelta.relativedelta(month_start, date_dx)
    # get months difference
    #res_months = delta.months + (delta.years * 12)
    return res_months

#### per month
def get_diff_month_m(month_start, date_dx):
    month_start = date(int(month_start.split('-')[0]), int(month_start.split('-')[1]), int(month_start.split('-')[2])) 
    date_dx = date(int(date_dx.split('-')[0]), int(date_dx.split('-')[1]), int(date_dx.split('-')[2])) 

    # Get the relativedelta between two dates
    delta = relativedelta(month_start, date_dx)
    # get months difference
    res_months = delta.months + (delta.years * 12)
    return res_months

def get_enroll_mon_list(start_date, length):
    ### 01/2000 - 12/2019 --> 240 months
    ###01/1991 - 12/2017 ---> 324 months
   dates = []
   dates.append(start_date)
   yr = int(start_date.split("-")[0])
   mon = 1
   for i in  range(int(length)-1):
       mon = mon +1
       if mon <=9:
           date = str(yr)+"-"+"0"+str(mon) +"-01"
       elif mon >=10 and mon <=12:
           date = str(yr)+"-"+str(mon) +"-01"
       
       if mon >12:
           yr +=1
           mon =1
           if mon <=9:
               date = str(yr)+"-"+"0"+str(mon) +"-01"
           elif mon >=10 and mon <=12:
               date = str(yr)+"-"+str(mon) +"-01"
       dates.append(date)
   return dates


def get_claims_inDateRange(in_data, time_col, start_date, end_date):
    if in_data.empty:
        curr_df = pd.DataFrame()
    else:      
        curr_df = in_data[(in_data[time_col] >= start_date) & (in_data[time_col] < end_date)] #
    return curr_df


def remove_string_nan(df_code):
    code_wonan = []
    for m in range(df_code.shape[0]):
        for n in range(df_code.shape[1]):
            mm = df_code.iloc[m,n]
            if mm != 'nan':
                code_wonan.append(mm)
    return code_wonan

def unlist(lists):
    new_list =[]
    for item in lists:
        new_list += item
    return new_list


def get_uniquecodes_perMonth(code_type, in_data1,in_data2,code_cols1,code_cols2):
    if in_data1.empty:
        code1 = []
    else:
        code1 = in_data1[code_cols1] #.to_numpy().reshape(code1.shape[0]*code1.shape[1],1)#.tolist()#.astype(str)
        code1 = remove_string_nan(code1)
    if in_data2.empty:
        code2 = []
    else:
        code2 = in_data2[code_cols2]
        code2 = remove_string_nan(code2)
    all_codes = code1 +code2
    if len(all_codes) >0:
        all_codes = [code_type + "_" + str(code) for code in all_codes ]
    return all_codes


def get_uniquecodes_onetype(data, col, Type, claim):
    #code_data = data
    code_data = data.loc[:, col]
    code_data.columns = col
    
    frames = []
    #unique_code_df_columns = ["CODE", "TYPE", "CLAIM"]
    for i in range(len(list(code_data))): #
        #print(i)
        unique_code= code_data.iloc[:,i].dropna().unique()
        if Type == "DRUG_NDC" and claim == 'Medicare':
            unique_code = [int(i) for i in unique_code]
            lens = len(unique_code)
        else:
            lens = unique_code.shape[0]
        #print(unique_code)#@.shape)
        unique_code_df_1 = pd.DataFrame(np.zeros(((lens,1))))
        unique_code_df_1.columns = ["CODE"]#, "TYPE", "CLAIM"]
        unique_code_df_1['CODE'] = pd.DataFrame(unique_code)
        frames.append(unique_code_df_1)
    unique_code_df =  pd.concat(frames ,axis=0, ignore_index=True)
    final_code_list= unique_code_df.iloc[:,0].dropna().unique()
    
    unique_code_df_f = pd.DataFrame(np.zeros(((final_code_list.shape[0],3))))
    unique_code_df_f.columns = ["CODE", "TYPE", "CLAIM"]
    unique_code_df_f['CODE'] = pd.DataFrame(final_code_list)
    unique_code_df_f['TYPE'] = str(Type)
    unique_code_df_f['CLAIM'] = str(claim)
    return unique_code_df_f
    
def get_studyIDsource(kcr_df, medicare_df, medicaid_health_df, medicaid_pharm_df):
    kcr_ID = kcr_df["study_id"].unique() #47130
    medicare_IDs = medicare_df["study_id"].unique()
    health_ID = medicaid_health_df["study_id"].unique()
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
    return ALLID_df
    
def GetPerPatientData(data_df, Name, path_save):
    health_ID = data_df["study_id"].unique() 
    for i in range(health_ID.shape[0]):
        curr_df = data_df.loc[data_df['study_id'] == health_ID[i]]
        file_name = "ID"+ str(health_ID[i])+"_all_"+str(Name)+".xlsx"
        completeName = os.path.join(path_save, file_name)
        #curr_df.to_csv(completeName, index=False)
        curr_df.to_excel(completeName, header = True, index=False)
    print(Name, "done") 



def read_allClaims(patient_ID,path_medicaid_heath, path_medicaid_pharm, path_medicare, medicaid_columns_list_health, medicaid_columns_list_pharm, medicare_columns_list):
    #Codes columns for medicaid
    medicaid_diag_cols = ["CDE_DIAG_PRIM","CDE_DIAG_2","CDE_DIAG_3","CDE_DIAG_4"] #ICD 9 or ICD10
    medicaid_diag_cols_f = []
    for kkk in range(len(medicaid_diag_cols)):
        if medicaid_diag_cols[kkk] in medicaid_columns_list_health:
            medicaid_diag_cols_f.append(medicaid_diag_cols[kkk])
    medicaid_diag_cols = medicaid_diag_cols_f
    
    medicaid_proc_cols = ["CDE_PROC_PRIM"]                                        #HCPCS
    medicaid_proc_cols_f = []
    for kkk in range(len(medicaid_proc_cols)):
        if medicaid_proc_cols[kkk] in medicaid_columns_list_health:
            medicaid_proc_cols_f.append(medicaid_proc_cols[kkk])
    medicaid_proc_cols = medicaid_proc_cols_f
    
    medicaid_drug_cols = ["CDE_THERA_CLS_AHFS", "CDE_NDC"]
    medicaid_drug_cols_f = []
    for kkk in range(len(medicaid_drug_cols)):
        if medicaid_drug_cols[kkk] in medicaid_columns_list_pharm:
            medicaid_drug_cols_f.append(medicaid_drug_cols[kkk])
    medicaid_drug_cols = medicaid_drug_cols_f
    
    #Codes columns for medicare
    medicare_diag_cols = ['DGNS_CD{}'.format(i) for i in range(1, 25+1)]  #ICD9 or ICD10
    medicare_diag_cols_f = []
    for kkk in range(len(medicare_diag_cols)):
        if medicare_diag_cols[kkk] in medicare_columns_list:
            medicare_diag_cols_f.append(medicare_diag_cols[kkk])
    medicare_diag_cols = medicare_diag_cols_f
    
    medicare_proc_cols_2 = ["HCPCS_CD"]                       #HCPCS
    medicare_proc_cols_1 = ['PRCDR_CD{}'.format(i) for i in range(1, 25+1)]  #ICD9 or ICD10
    medicare_proc_cols = medicare_proc_cols_1 + medicare_proc_cols_2
    medicare_proc_cols_f = []
    for kkk in range(len(medicare_proc_cols)):
        if medicare_proc_cols[kkk] in medicare_columns_list:
            medicare_proc_cols_f.append(medicare_proc_cols[kkk])
    medicare_proc_cols = medicare_proc_cols_f
    
    medicare_drug_cols = ["NDC_CD","PROD_SRVC_ID"] 
    medicare_drug_cols_f = []
    for kkk in range(len(medicare_drug_cols)):
        if medicare_drug_cols[kkk] in medicare_columns_list:
            medicare_drug_cols_f.append(medicare_drug_cols[kkk])
    medicare_drug_cols = medicare_drug_cols_f
    
    medicare_drug_related = ["GNN","BN"]
    medicare_drug_related_f = []
    for kkk in range(len(medicare_drug_related)):
        if medicare_drug_related[kkk] in medicare_columns_list:
            medicare_drug_related_f.append(medicare_drug_related[kkk])
    medicare_drug_related = medicare_drug_related_f


    #1.read original health_claims to get proc and diag codes
    xlsx_files = glob.glob(os.path.join(path_medicaid_heath, "*.xlsx"))
    split_ID = [a.split('ID')[1] for a in xlsx_files]
    IDs_has_health_files = [a.split('_')[0] for a in split_ID]
    
    if patient_ID in IDs_has_health_files:
        file_name = "ID" + str(patient_ID)+ "_all_medicaid_healthclaims.xlsx"
        completeName = os.path.join(path_medicaid_heath, file_name)
        medicaid_health_df = pd.read_excel(completeName,header=0, index_col=False, dtype='object')
        lst = ["study_id", "Id_medicaid", "DTE_FIRST_SVC"] +medicaid_diag_cols + medicaid_proc_cols
        medicaid_health_df = medicaid_health_df.filter(lst)
        check_date = pd.DataFrame(medicaid_health_df['DTE_FIRST_SVC']).iloc[0,0]
        if not "/" in check_date:
            print("Convert date medicaid health")
            check_date = pd.DataFrame(medicaid_health_df['DTE_FIRST_SVC'])
            for k in range(len(check_date)):
                #print(k)
                day = check_date.iloc[k,0][0:2]
                mon = mtn(check_date.iloc[k,0][2:5])
                year = check_date.iloc[k,0][5:]
                newdate = mon + "/" + day + "/" +year 
                medicaid_health_df.iloc[k,2] = newdate
    else:
        medicaid_health_df = pd.DataFrame()
    
    #2.get original pharmcy_claims to get drug codes    
    xlsx_files = glob.glob(os.path.join(path_medicaid_pharm, "*.xlsx"))
    split_ID = [a.split('ID')[1] for a in xlsx_files]
    IDs_has_health_files = [a.split('_')[0] for a in split_ID]
    
    if patient_ID in IDs_has_health_files:
        file_name = "ID" + str(patient_ID)+ "_all_medicaid_pharmclaims.xlsx"
        completeName = os.path.join(path_medicaid_pharm, file_name)
        medicaid_pharm_df = pd.read_excel(completeName,header=0, index_col=False, dtype='object')       
        lst = ["study_id", "Id_medicaid", "DTE_FIRST_SVC"] +medicaid_drug_cols
        medicaid_pharm_df = medicaid_pharm_df.filter(lst)
        check_date = pd.DataFrame(medicaid_pharm_df['DTE_FIRST_SVC']).iloc[0,0]
        if not "/" in check_date:
            #print("Convert date for medicaid pharm")
            check_date = pd.DataFrame(medicaid_pharm_df['DTE_FIRST_SVC'])
            for k in range(len(check_date)):
                #print(k)
                day = check_date.iloc[k,0][0:2]
                mon = mtn(check_date.iloc[k,0][2:5])
                year = check_date.iloc[k,0][5:]
                newdate = mon + "/" + day + "/" +year 
                medicaid_pharm_df.iloc[k,2] = newdate
    else:
        medicaid_pharm_df = pd.DataFrame()
        
     
    #3.Get original medicare_claims    
    xlsx_files = glob.glob(os.path.join(path_medicare, "*.xlsx"))
    split_ID = [a.split('ID')[1] for a in xlsx_files]
    IDs_has_health_files = [a.split('_')[0] for a in split_ID]
    
    #patient_ID = IDs_has_health_files[0]
    
    if patient_ID in IDs_has_health_files:
        file_name = "ID" + str(patient_ID)+ "_all_medicare_claims.xlsx"
        completeName = os.path.join(path_medicare, file_name)
        medicare_df = pd.read_excel(completeName,header=0, index_col=False, dtype='object')       
        lst = ["study_id","claims_date"] + medicare_diag_cols + medicare_proc_cols + medicare_drug_cols + medicare_drug_related
        medicare_df = medicare_df.filter(lst)
        check_date = pd.DataFrame(medicare_df['claims_date']).iloc[0,0]
        if not "/" in check_date:
            #print("Convert date for medicare")
            check_date = pd.DataFrame(medicare_df['claims_date'])
            for k in range(len(check_date)):
                #print(k)
                day = check_date.iloc[k,0][0:2]
                mon = mtn(check_date.iloc[k,0][2:5])
                year = check_date.iloc[k,0][5:]
                newdate = mon + "/" + day + "/" +year 
                medicare_df.iloc[k,1] = newdate
    else:
        medicare_df = pd.DataFrame()
    
    data_loaded = [medicaid_health_df,medicaid_pharm_df,medicare_df]
    return data_loaded



def clean_code_func2(list_of_codes, list_of_code_types):
    list_of_codes = list_of_codes.astype(str)
    #1.repalce any codes with non-alphanumeric characters with ""
    updated_list_of_codes = [''.join(filter(str.isalnum, a)) for a in list_of_codes]
    #2.replace decimal with ""
    updated_list_of_codes = [string.replace(".", "" ) for string in updated_list_of_codes]
    #3. replace space with ""
    updated_list_of_codes = [string.replace(" ", "" ) for string in updated_list_of_codes]
    #4. For each code, 
  #   #if HCPCS, reformat codes less than 5 char long
  #   #if ICD, reformat codes less than 3 char long
  #   #if DRUG_NDC or DRUG_THERA_CLS_AHFS, remove leading 0s

    for m in range(len(updated_list_of_codes)):
            curr_code = updated_list_of_codes[m]
            curr_nchar = len(curr_code)
            curr_type =  list_of_code_types[m].upper()
            if curr_code =='nan' or curr_code =='':
                pass
            elif "HCPC" in curr_type:
                if curr_nchar <5:
                    #print("Yes")
                    curr_code = reformat_codes_func(curr_code,5)
            elif "ICD" in curr_type:
                if curr_nchar <3:
                    #print("Yes")
                    curr_code = reformat_codes_func(curr_code,3)
            elif "NDC" or "AHFS" in curr_type:
                curr_code = str(int(curr_code)) #delete leading zeros
                
            updated_list_of_codes[m] = curr_code 
    return pd.Series(updated_list_of_codes)

def clean_codes_inPerPtsData(in_data, all_code_cols, ICD_cols,HCPCS_cols,NDC_cols = "", AHFS_cols = ""):     
    if in_data.empty:
        in_data = pd.DataFrame()
    else:
        for j in range(len(all_code_cols)):
            curr_col = all_code_cols[j]
            curr_codes_list = in_data[curr_col]
            if curr_col in ICD_cols:
                curr_codes_type_list = ["ICD"] * len(curr_codes_list)
            elif curr_col in HCPCS_cols:
                curr_codes_type_list = ["HCPC"] * len(curr_codes_list)
            elif curr_col in NDC_cols:
                curr_codes_type_list = ["NDC"] * len(curr_codes_list)
            elif curr_col in AHFS_cols:
                curr_codes_type_list = ["AHFS"] * len(curr_codes_list)
            #print(curr_codes_type_list)           
            in_data[curr_col] = clean_code_func2(curr_codes_list, curr_codes_type_list)
    return in_data

def recode_Race_func(kcr_data):
    kcr_data['Race_Recoded'] = "NA"
    kcr_data.loc[kcr_data.Race1 == 1, 'Race_Recoded'] = 1
    kcr_data.loc[kcr_data.Race1 == 2, 'Race_Recoded'] = 2
    kcr_data.loc[kcr_data.Race_Recoded =='NA', 'Race_Recoded'] = 3
    kcr_data = kcr_data.drop(['Race1'], axis=1)
    return kcr_data

def recode_SurgPrimSite_func_v1(kcr_data, col_name):
    #df[~df['A'].isin([3, 6])]
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([0]), col_name] = 0
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([19]), col_name] = 19
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([20,21,22,23,24]), col_name] = 20
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([30]), col_name] = 30
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([40,41,42]), col_name] = 40
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([50,51,52,53,54,55,56,57,58,59,63]), col_name] = 50
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([60,61,62,64,65,66,67,68,69,73,74]), col_name] = 60
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([70,71,72]), col_name] = 70
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([80]), col_name] = 80
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([90]), col_name] = 90
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([99]), col_name] = 99

    SurgPrimSite_values = kcr_data[col_name] 
    return SurgPrimSite_values

def recode_SurgPrimSite_func_v2(kcr_data, col_name):
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([0]), col_name] = 0
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([19]), col_name] = 19
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([20,21,22,23,24]), col_name] = 20
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([30]), col_name] = 30
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([40]), col_name] = 40
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([41]), col_name] = 41
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([42]), col_name] = 42
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([50]), col_name] = 50
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([51,53,54,55,56]), col_name] = 51
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([52,57,58,59,63]), col_name] = 52
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([60]), col_name] = 60
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([61,64,65,66,67]), col_name] = 61
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([62,68,69,73,74]), col_name] = 62
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([70]), col_name] = 70
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([71]), col_name] = 71
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([72]), col_name] = 72
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([80]), col_name] = 80
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([90]), col_name] = 90
    kcr_data.loc[kcr_data['RXSummSurgPrimSite'].isin([99]), col_name] = 99

    SurgPrimSite_values = kcr_data[col_name] 
    return SurgPrimSite_values

def recode_SPS_func(kcr_data):
    kcr_data['RXSummSurgPrimSite_RecodedV1'] = 'NA'
    kcr_data['RXSummSurgPrimSite_RecodedV2'] = 'NA'
    kcr_data['RXSummSurgPrimSite_RecodedV1'] = recode_SurgPrimSite_func_v1(kcr_data, 'RXSummSurgPrimSite_RecodedV1')
    kcr_data['RXSummSurgPrimSite_RecodedV2'] = recode_SurgPrimSite_func_v2(kcr_data, 'RXSummSurgPrimSite_RecodedV2')
    kcr_data = kcr_data.drop(['RXSummSurgPrimSite'], axis=1)
    return kcr_data


def updated_SEERSummStg2000_func(kcr_data, new_kcr_data2):
    ###match two datafram
    new_kcr_data2 = new_kcr_data2.set_index('study_id')
    new_kcr_data2 = new_kcr_data2.reindex(index=kcr_data['study_id'])
    new_kcr_data2 = new_kcr_data2.reset_index()
    kcr_data['DerivedSS2000'] = new_kcr_data2['DerivedSS2000']
    kcr_data = kcr_data.fillna('NA')

    #Get comb SEERSummStg
    #1. for not missing original SEER stage, use "SEERSummStg2000 ('SEERSummStg2000’ only captures SEER summary stage from the years 2001-2003. )
    #2. for missing original SEER stage, use "DerivedSS2000 (‘DerivedSS2000’ was added for the summary stage between the years 2004-2015. )
    #No such information was captured for the year 2000.
    kcr_data['Comb_SEERSummStg'] = 'NA'
    kcr_data.loc[kcr_data['SEERSummStg2000'] != 'NA', 'Comb_SEERSummStg'] = kcr_data.loc[kcr_data['SEERSummStg2000'] != 'NA', 'SEERSummStg2000']
    kcr_data.loc[kcr_data['SEERSummStg2000'] == 'NA', 'Comb_SEERSummStg'] = kcr_data.loc[kcr_data['SEERSummStg2000'] == 'NA', "DerivedSS2000"]
    kcr_data = kcr_data.drop(["SEERSummStg2000","DerivedSS2000"], axis=1)
    return kcr_data


def updated_TNM_func(kcr_data, new_kcr_data3):
    new_kcr_data3 = new_kcr_data3.fillna('NA')
    new_kcr_data3 = new_kcr_data3.set_index('study_id')
    new_kcr_data3 = new_kcr_data3.reindex(index=kcr_data['study_id'])
    new_kcr_data3 = new_kcr_data3.reset_index()

    kcr_data['TNMPathT'] = new_kcr_data3['TNMPathT']
    kcr_data['TNMPathN'] = new_kcr_data3['TNMPathN']
    kcr_data['TNMPathM'] = new_kcr_data3['TNMPathM']
    kcr_data['TNMClinT'] = new_kcr_data3['TNMClinT']
    kcr_data['TNMClinN'] = new_kcr_data3['TNMClinN']
    kcr_data['TNMClinM'] = new_kcr_data3['TNMClinM']
    return kcr_data

def get_DAJCC_var_funtion(kcr_data, col_name, pathology_results_col, clinical_results_col):
    kcr_data[col_name] = 'NA'
    for i in range(len(kcr_data)):
        curr_val = kcr_data.loc[kcr_data.index[i], pathology_results_col] 
        if curr_val == "88" or curr_val == "pX" or curr_val == "NA":
            curr_val = kcr_data.loc[kcr_data.index[i], clinical_results_col] 
            if curr_val == "88" or curr_val == "pX" or curr_val == "NA":
                curr_val = 'NA'
        kcr_data.loc[kcr_data.index[i], col_name]  = curr_val
    return kcr_data

def convert_DAJCC_var_function(kcr_data, var_name):
    in_values = kcr_data.loc[:,var_name]
    
    if var_name == 'DAJCC_M':
        for i in range(len(in_values)):
            curr_val = in_values[i] 
            curr_val = curr_val.replace('I+', '')
            curr_val = curr_val.replace('c', '')
            curr_val = curr_val.replace('p', '')
            if curr_val == 'NA':
                replace_val = '88'                
            elif curr_val == "X":
                replace_val = '99'
            elif curr_val == "0":
                replace_val = '00'
            elif curr_val == "1":
                replace_val = '10'
            elif curr_val == "1A":
                replace_val = '11'
            elif curr_val == "1B":
                replace_val = '12'
            elif curr_val == "1C":
                replace_val = '13'
            elif curr_val == "1 NOS":
                replace_val = '19'
            else:
                replace_val = '88'
            kcr_data.loc[kcr_data.index[i], var_name] = replace_val
    elif var_name == 'DAJCC_T':
        for i in range(len(in_values)):
            curr_val = in_values[i] 
            curr_val = curr_val.replace('c', '')
            curr_val = curr_val.replace('p', '')
            if curr_val == 'NA':
                replace_val = '88' 
            elif "ISD" in curr_val or "2D" in curr_val:
                replace_val = '88'
            elif curr_val == "X": 
                replace_val =  "99"
            elif curr_val == "0": 
                replace_val =  "00"
            elif curr_val == "A": 
                replace_val =  "01"
            elif curr_val == "IS": 
                replace_val =  "05"
            elif curr_val == "ISPU": 
                replace_val =  "06"
            elif curr_val == "ISPD": 
                replace_val =  "07"
            elif curr_val == "1": 
                replace_val =  "10"
            elif curr_val =="1MI" or curr_val == "1MIC": 
                replace_val =  "11"
            elif curr_val == "1 NOS": 
                replace_val =  "19"
            elif curr_val == "1A": 
                replace_val =  "12"
            elif curr_val == "1A1": 
                replace_val =  "13"
            elif curr_val == "1A2": 
                replace_val =  "14"
            elif curr_val == "1B": 
                replace_val =  "15"
            elif curr_val == "1B1": 
                replace_val =  "16"
            elif curr_val == "1B2": 
                replace_val =  "17"
            elif curr_val == "1C": 
                replace_val =  "18"
            elif curr_val == "2": 
                replace_val =  "20"
            elif curr_val == "2 NOS": 
                replace_val =  "29"
            elif curr_val == "2A": 
                replace_val =  "21"
            elif curr_val == "2B": 
                replace_val =  "22"
            elif curr_val == "2C": 
                replace_val =  "23"
            elif curr_val == "3": 
                replace_val =  "30"
            elif curr_val == "3 NOS": 
                replace_val =  "39"
            elif curr_val == "3A": 
                replace_val =  "31"
            elif curr_val == "3B": 
                replace_val =  "32"
            elif curr_val == "3C": 
                replace_val =  "33" 
            elif curr_val == "4": 
                replace_val =  "40"
            elif curr_val == "4 NOS": 
                replace_val =  "49"
            elif curr_val == "4A": 
                replace_val =  "41"
            elif curr_val == "4B": 
                replace_val =  "42"
            elif curr_val == "4C": 
                replace_val =  "43"
            elif curr_val == "4D": 
                replace_val =  "44"
            elif curr_val == "1A NOS": 
                replace_val =  "80"
            elif curr_val == "1B NOS": 
                replace_val =  "81"
            else:
                replace_val = '88'
            kcr_data.loc[kcr_data.index[i], var_name] = replace_val
    elif var_name == 'DAJCC_N':
        for i in range(len(in_values)):
            curr_val = in_values[i] 
            curr_val = curr_val.replace('c', '')
            curr_val = curr_val.replace('p', '')
            if curr_val == 'NA':
                replace_val = '88' 
            elif curr_val == "X": 
                replace_val =  "99"
            elif curr_val == "0": 
                replace_val =  "00"
            elif curr_val == "0I-": 
                replace_val =  "01"
            elif curr_val == "0I+": 
                replace_val =  "02"
            elif curr_val == "0M-": 
                replace_val =  "03"
            elif curr_val == "0M+": 
                replace_val =  "04"
            elif curr_val == "1": 
                replace_val =  "10"
            elif curr_val == "1 NOS": 
                replace_val =  "19"
            elif curr_val == "1A": 
                replace_val =  "11"
            elif curr_val == "1B": 
                replace_val =  "12"
            elif curr_val == "1C": 
                replace_val =  "13"
            elif curr_val == "1MI": 
                replace_val =  "18"
            elif curr_val == "2": 
                replace_val =  "20"
            elif curr_val == "2 NOS": 
                replace_val =  "29"
            elif curr_val == "2A": 
                replace_val =  "21"
            elif curr_val == "2B": 
                urr_val =  "22"
            elif curr_val == "2C": 
                replace_val =  "23" 
            elif curr_val == "3": 
                replace_val =  "30"
            elif curr_val == "3 NOS": 
                replace_val =  "39"
            elif curr_val == "3A": 
                replace_val =  "31"
            elif curr_val == "3B": 
                replace_val =  "32"
            elif curr_val == "3C": 
                replace_val =  "33"
            else:
                replace_val = '88'
            kcr_data.loc[kcr_data.index[i], var_name] = replace_val
    return kcr_data


def get_pts_level_char_func(ID_Sources_data, kcr_data):
    flag_update = 0
    char_df = pd.DataFrame(np.zeros((len(ID_Sources_data), 29)))
    if flag_update ==1:
        char_df.columns = ["study_id","Medicaid_OR_Medicare",
                           "Diagnosis_Year", "Date_dx","Race","Site",
                           "Stage", #"BestStageGrp",
                           "Comb_SEERSummStg","regional","Laterality",
                           "Grade","er_stat","pr_stat","surg_prim_site_V1","surg_prim_site_V2","her2_stat",
                           "radiation","reg_age_at_dx","reg_nodes_exam","reg_nodes_pos",
                           "cs_tum_size","cs_tum_ext","chemo","hormone","cs_tum_nodes",
                           "date_Birth",
                           "DAJCC_T","DAJCC_M","DAJCC_N"] #, "Site_1st_Event"
    else:
        char_df.columns = ["study_id","Medicaid_OR_Medicare",
                           "Diagnosis_Year", "Date_dx","Race","Site",
                           "Stage", #"BestStageGrp",
                           "SEERSummStg2000","regional","Laterality",
                           "Grade","er_stat","pr_stat","surg_prim_site_V1","surg_prim_site_V2","her2_stat",
                           "radiation","reg_age_at_dx","reg_nodes_exam","reg_nodes_pos",
                           "cs_tum_size","cs_tum_ext","chemo","hormone","cs_tum_nodes",
                           "date_Birth",
                           "DAJCC_T","DAJCC_M","DAJCC_N"] #, "Site_1st_Event"
    
    
    for i in range(len(ID_Sources_data)):
        #print(i)
        curr_id = ID_Sources_data.iloc[i,0]
        char_df.loc[char_df.index[i],"study_id"] = curr_id
        
        #in medicare or medicaid
        curr_ID_source = ID_Sources_data.iloc[[i],:]
        
        #in medicare or medicaid
        if curr_ID_source.loc[curr_ID_source.index[0],"in_Medicare"] ==1 and curr_ID_source.loc[curr_ID_source.index[0],"in_Medicaid"] ==1:
            char_df.loc[char_df.index[i],"Medicaid_OR_Medicare"] = "Both"
        elif curr_ID_source.loc[curr_ID_source.index[0],"in_Medicare"] ==1:
            char_df.loc[char_df.index[i],"Medicaid_OR_Medicare"] = "Medicare"
        elif curr_ID_source.loc[curr_ID_source.index[0],"in_Medicaid"] ==1:
            char_df.loc[char_df.index[i],"Medicaid_OR_Medicare"] = "Medicaid"
        else:
            char_df.loc[char_df.index[i],"Medicaid_OR_Medicare"] = "None"
    
        #Event data
        #curr_event = All_cancer_site_date_data.loc[All_cancer_site_date_data["study_id"] == str(curr_id)]
        
        #1st event site and year,due to merging effect, we need to do the following
        #1.get frist primary site, 
        #curr_event = curr_event.loc[curr_event.index[0], "Site_1st_Event"]
        #curr_1stevent_type = curr_event.split("$$$")[0]
        
        #make sure it is in bc_code
        #curr_1stprimary_site <- curr_1stprimary_site[which(curr_1stprimary_site %in% bc_codes)] 
        #char_df.loc[char_df.index[i],"Site_1st_Event"] = curr_1stevent_type
    
        #Event data
        curr_kcr = kcr_data.loc[kcr_data["study_id"] == curr_id]
        char_df.loc[char_df.index[i],"Diagnosis_Year"] = curr_kcr.loc[curr_kcr.index[0],"Year_Diag"]
        char_df.loc[char_df.index[i],"Site"] = curr_kcr.loc[curr_kcr.index[0],"PrimarySite"]
        char_df.loc[char_df.index[i],"date_Birth"] = curr_kcr.loc[curr_kcr.index[0],"date_Birth"]
        char_df.loc[char_df.index[i],"Race"] = curr_kcr.loc[curr_kcr.index[0],"Race_Recoded"]
        
        curr_BestStageGrp = curr_kcr.loc[curr_kcr.index[0],"ajccstage"]  #"BestStageGrp"
        if curr_BestStageGrp == 'NA':
            char_df.loc[char_df.index[i],"Stage"] = 'NA'
        #elif curr_BestStageGrp >= 0 and curr_BestStageGrp < 2:
        #    char_df.loc[char_df.index[i],"Stage"] = int(0)
        #elif curr_BestStageGrp >= 10 and curr_BestStageGrp < 30:
        #    char_df.loc[char_df.index[i],"Stage"] = int(1)
        #elif curr_BestStageGrp >= 30 and curr_BestStageGrp < 50:
        #    char_df.loc[char_df.index[i],"Stage"] = int(2)
        #elif curr_BestStageGrp >= 50 and curr_BestStageGrp < 70:
        #    char_df.loc[char_df.index[i],"Stage"] = int(3)
        #elif curr_BestStageGrp >= 70 and curr_BestStageGrp < 80:
        #    char_df.loc[char_df.index[i],"Stage"] = int(4)
        #else:
        #    char_df.loc[char_df.index[i],"Stage"] = 'NA'
        elif int(curr_BestStageGrp) > 4:
            char_df.loc[char_df.index[i],"Stage"] = 'NA'
        else:
            char_df.loc[char_df.index[i],"Stage"] = int(curr_BestStageGrp)
            
        char_df.loc[char_df.index[i],"Grade"] = curr_kcr.loc[curr_kcr.index[0],"Grade"]
        char_df.loc[char_df.index[i],"Date_dx"] = curr_kcr.loc[curr_kcr.index[0],"Date_dx"]
        char_df.loc[char_df.index[i],"Laterality"] = curr_kcr.loc[curr_kcr.index[0],"Laterality"]
        char_df.loc[char_df.index[i],"er_stat"] = curr_kcr.loc[curr_kcr.index[0],"er_stat"]
        char_df.loc[char_df.index[i],"pr_stat"] = curr_kcr.loc[curr_kcr.index[0],"pr_stat"]
        char_df.loc[char_df.index[i],"her2_stat"] = curr_kcr.loc[curr_kcr.index[0],"her2_stat"]
        char_df.loc[char_df.index[i],"surg_prim_site_V1"] = curr_kcr.loc[curr_kcr.index[0],"RXSummSurgPrimSite_RecodedV1"]
        char_df.loc[char_df.index[i],"surg_prim_site_V2"] = curr_kcr.loc[curr_kcr.index[0],"RXSummSurgPrimSite_RecodedV2"]
    
        char_df.loc[char_df.index[i],"radiation"] = curr_kcr.loc[curr_kcr.index[0],"RXSummRadiation"]
        char_df.loc[char_df.index[i],"chemo"] = curr_kcr.loc[curr_kcr.index[0],"RXSummChemo"]
        char_df.loc[char_df.index[i],"hormone"] = curr_kcr.loc[curr_kcr.index[0],"RXSummHormone"]
    
        char_df.loc[char_df.index[i],"reg_nodes_exam"] = curr_kcr.loc[curr_kcr.index[0],"RegNodesExamined"]
        char_df.loc[char_df.index[i],"reg_nodes_pos"] = curr_kcr.loc[curr_kcr.index[0],"RegNodesPositive"]
        char_df.loc[char_df.index[i],"cs_tum_size"] = curr_kcr.loc[curr_kcr.index[0],"CSTumorSize"]
        char_df.loc[char_df.index[i],"cs_tum_ext"] = curr_kcr.loc[curr_kcr.index[0],"CSTumorSizeExtEval"]
        char_df.loc[char_df.index[i],"reg_age_at_dx"] = curr_kcr.loc[curr_kcr.index[0],"DiagAge"]
        char_df.loc[char_df.index[i],"cs_tum_nodes"] = curr_kcr.loc[curr_kcr.index[0],"CSLymphNodes"]
    
        char_df.loc[char_df.index[i],"DAJCC_T"] = curr_kcr.loc[curr_kcr.index[0],"DAJCC_T"]
        char_df.loc[char_df.index[i],"DAJCC_M"] = curr_kcr.loc[curr_kcr.index[0],"DAJCC_M"]
        char_df.loc[char_df.index[i],"DAJCC_N"] = curr_kcr.loc[curr_kcr.index[0],"DAJCC_N"]
        
        if flag_update ==1:
            char_df.loc[char_df.index[i],"Comb_SEERSummStg"] = curr_kcr.loc[curr_kcr.index[0],"Comb_SEERSummStg"]
            #Local or regional
            curr_seer_stage = curr_kcr.loc[curr_kcr.index[0],"Comb_SEERSummStg"]
        else:
            char_df.loc[char_df.index[i],"SEERSummStg2000"] = curr_kcr.loc[curr_kcr.index[0],"SEERSummStg2000"]
            #Local or regional
            curr_seer_stage = curr_kcr.loc[curr_kcr.index[0],"SEERSummStg2000"]
        if curr_seer_stage == "NA":
            char_df.loc[char_df.index[i],"regional"] = "NA"
        else:
            if int(curr_seer_stage) in [2, 3, 4, 5]:
                char_df.loc[char_df.index[i],"regional"] = int(1)
            else:
                char_df.loc[char_df.index[i],"regional"] = int(0)
    return char_df
                

def get_codes_func(code_names, code_type):
    code_names = pd.DataFrame(code_names)
    code_names.columns = ['codes']
    #code_type = 'DIAG_ICD'
    contain_values = code_names[code_names['codes'].str.contains(code_type)]
    return contain_values


def find_listofcode_grp_func(unique_codes_df, code_type, diag_grp_df):
    unique_codes_df['GRPs'] = 'NA'
    GRPs = []
    for i in range(unique_codes_df.shape[0]):
        #print(i)
        curr_code = unique_codes_df.loc[unique_codes_df.index[i],"codes"]
        strings = "_"
        curr_code = curr_code.split(strings)[2]
        #curr_code ='testme'
        code_df = diag_grp_df.loc[diag_grp_df['CODE'] == curr_code]
        if code_df.empty:
            grp = code_type + "_NA"
        else:
            grp = code_df.loc[code_df.index[0],code_type]
        GRPs.append(grp)
    unique_codes_df['GRPs'] = pd.DataFrame(GRPs)
    return unique_codes_df


def create_grp_feature_df_func(unique_codes_df, code_type, curr_df):
    list_first3 = ["study_id", "Month_Start", "Month_End"]
    list_codes = unique_codes_df['codes'].tolist()
    list_final_codes = unique_codes_df['GRPs'].tolist()
    keep_column = list_first3 + list_codes
    final_column = list_first3 + list_final_codes
    curr_grp_feature_df = curr_df[keep_column]
    curr_grp_feature_df.columns =final_column
    return curr_grp_feature_df


def add_time_since_func(curr_df):
    time_since_df = pd.DataFrame(np.zeros((curr_df.shape[0], curr_df.shape[1])))
    col_name = curr_df.columns
    col_name_new = ["time_since_" + s for s in col_name]
    time_since_df.columns = col_name_new
    time_since_df = time_since_df.rename(columns={"time_since_study_id": "study_id", "time_since_Month_Start": "Month_Start", "time_since_Month_index": "Month_index"})
    time_since_df['study_id'] = curr_df['study_id']
    time_since_df['Month_Start'] = curr_df['Month_Start']
    time_since_df['Month_index'] = curr_df['Month_index']
    time_since_df['Month_index'] = time_since_df['Month_index'].astype('int64')
    
    #time_since_df.dtypes
    for k in range(2,curr_df.shape[1]-1): ### do not include month_index column
        curr_month_df = pd.DataFrame(curr_df.iloc[:,k])
        label =curr_month_df.columns[0]
        new_label = "time_since_" + label
        if (curr_month_df[label] == 0).all():
            time_since_df[new_label] = int(-1)
        else:
            most_recent_month = -999
            for kk in range(curr_df.shape[0]):
                if curr_month_df.loc[curr_month_df.index[kk], label] == 0 and most_recent_month == -999:
                    time_since_df.loc[time_since_df.index[kk], new_label] = int(-1)
                elif curr_month_df.loc[curr_month_df.index[kk], label] > 0 :
                    time_since_df.loc[time_since_df.index[kk], new_label] = int(0)
                    most_recent_month = int(curr_df.loc[curr_df.index[kk], 'Month_index'])
                elif curr_month_df.loc[curr_month_df.index[kk], label] == 0 and most_recent_month != -999:
                    most_recent_month_curr = int(curr_df.loc[curr_df.index[kk], 'Month_index'])
                    month_count = int(most_recent_month_curr - most_recent_month)
                    time_since_df.loc[time_since_df.index[kk], new_label] = int(month_count)
                    #most_recent_month = most_recent_month_curr
    return time_since_df



def add_time_until_func(curr_df):
    time_until_df = pd.DataFrame(np.zeros((curr_df.shape[0], curr_df.shape[1])))
    col_name = curr_df.columns
    col_name_new = ["time_until_" + s for s in col_name]
    time_until_df.columns = col_name_new
    time_until_df = time_until_df.rename(columns={"time_until_study_id": "study_id", "time_until_Month_Start": "Month_Start", "time_until_Month_index": "Month_index"})
    time_until_df['study_id'] = curr_df['study_id']
    time_until_df['Month_Start'] = curr_df['Month_Start']
    time_until_df['Month_index'] = curr_df['Month_index']
    time_until_df['Month_index'] = time_until_df['Month_index'].astype('int64')
    
    #time_until_df.dtypes
    for k in range(2,curr_df.shape[1]-1):
        curr_month_df = pd.DataFrame(curr_df.iloc[:,k])
        label =curr_month_df.columns[0]
        new_label = "time_until_" + label
        if (curr_month_df[label] == 0).all():
            time_until_df[new_label] = int(-1)
        else:
            soonest_future_month = -999
            for kk in range(curr_df.shape[0]-1,-1,-1):
                if curr_month_df.loc[curr_month_df.index[kk], label] == 0 and soonest_future_month == -999:
                    time_until_df.loc[time_until_df.index[kk], new_label] = int(-1)
                elif curr_month_df.loc[curr_month_df.index[kk], label] > 0 :
                    time_until_df.loc[time_until_df.index[kk], new_label] = int(0)
                    soonest_future_month = int(curr_df.loc[curr_df.index[kk], 'Month_index'])
                elif curr_month_df.loc[curr_month_df.index[kk], label] == 0 and soonest_future_month != -999:
                    soonest_future_month_curr = int(curr_df.loc[curr_df.index[kk], 'Month_index'])
                    month_count = abs(int(soonest_future_month_curr - soonest_future_month))
                    time_until_df.loc[time_until_df.index[kk], new_label] = int(month_count)
                    #soonest_future_month = soonest_future_month_curr
    return time_until_df


def add_cumul_ratio_func(curr_df):
    cumul_ratio_df = pd.DataFrame(np.zeros((curr_df.shape[0], curr_df.shape[1])))
    col_name = curr_df.columns
    col_name_new = ["cumul_ratio_" + s for s in col_name]
    cumul_ratio_df.columns = col_name_new
    cumul_ratio_df = cumul_ratio_df.rename(columns={"cumul_ratio_study_id": "study_id", "cumul_ratio_Month_Start": "Month_Start", "cumul_ratio_Month_index": "Month_index"})
    cumul_ratio_df['study_id'] = curr_df['study_id']
    cumul_ratio_df['Month_Start'] = curr_df['Month_Start']
    cumul_ratio_df['Month_index'] = curr_df['Month_index']
    cumul_ratio_df['Month_index'] = cumul_ratio_df['Month_index'].astype('int64')
    
    #cumul_ratio_df.dtypes
    for k in range(2,curr_df.shape[1]-1):
        curr_month_df = pd.DataFrame(curr_df.iloc[:,k])
        label =curr_month_df.columns[0]
        new_label = "cumul_ratio_" + label
        if (curr_month_df[label] == 0).all():
            cumul_ratio_df[new_label] = int(-1)
        else:
            curr_cum_count = 0 #inital cumalitive count as 0 
            for kk in range(curr_df.shape[0]):
                curr_month_index = int(curr_df.loc[curr_df.index[kk], 'Month_index']) + 1
                curr_cum_count = curr_cum_count + curr_month_df.loc[curr_month_df.index[kk], label]
                cumul_ratio_df.loc[cumul_ratio_df.index[kk], new_label] = float(curr_cum_count/curr_month_index)
                    #curr_cum_count = curr_cum_count_curr
    return cumul_ratio_df


def apply_code_transforamtion_func(curr_df):   
    time_since_df = add_time_since_func(curr_df)
    time_until_df = add_time_until_func(curr_df)
    cumul_ratio_df = add_cumul_ratio_func(curr_df)
    
    time_since_df = time_since_df.iloc[:,0:-1]
    time_until_df = time_until_df.iloc[:,2:-1]
    cumul_ratio_df = cumul_ratio_df.iloc[:,2:-1]
    
    frames=[time_since_df, time_until_df, cumul_ratio_df]
    curr_transf_df = pd.concat(frames,axis=1)
    
    return curr_transf_df


def get_primary_site_date_func(curr_df, curr_seq, name, curr_id):
    
    test = curr_df['CentralSequenceNumber'].isin(curr_seq)
    if test.any():
        #print('Yes', name)
        test = pd.DataFrame(test)
        index = test.index[test['CentralSequenceNumber'] == True]
        curr_df_df = curr_df.loc[index]
        curr_site = curr_df_df.loc[curr_df_df.index[0],'PrimarySite']
        curr_date = curr_df_df.loc[curr_df_df.index[0],'Date_dx']
        curr_type = name + '_Primary'
        curr_id = curr_id
        
    else:
        curr_site = int(0)
        curr_date = int(0)
        curr_type = int(0)
        curr_id = int(0)

    return [curr_site, curr_date, curr_type, curr_id]



def get_primary_site_date_func1(curr_df, curr_seq, name, curr_id):
    
    test = curr_df['CentralSequenceNumber'].isin(curr_seq)
    if test.any():
        #print('Yes', name)
        test = pd.DataFrame(test)
        index = test.index[test['CentralSequenceNumber'] == True]
        curr_df_df = curr_df.loc[index]
        curr_date = curr_df_df.loc[curr_df_df.index[0],'review_1recur_dt'] #review_1recur_dt Date_1Recur
        if not pd.isna(curr_date):
            curr_site = curr_df_df.loc[curr_df_df.index[0],'PrimarySite']
            curr_date = curr_df_df.loc[curr_df_df.index[0],'review_1recur_dt']
            curr_type = '1Recur'
            curr_id = curr_id
        else:
            curr_site = int(0)
            curr_date = int(0)
            curr_type = int(0)
            curr_id = int(0)
        
    else:
        curr_site = int(0)
        curr_date = int(0)
        curr_type = int(0)
        curr_id = int(0)

    return [curr_site, curr_date, curr_type, curr_id]

def get_cancer_info_func(curr_cancer_df, type_name):
    
        if len(curr_cancer_df) > 1:
            curr_cancer_df = curr_cancer_df.loc[curr_cancer_df['Type'].str.contains(type_name, case=False)]
        site = curr_cancer_df.loc[curr_cancer_df.index[0],"Site"] 
        type1 = curr_cancer_df.loc[curr_cancer_df.index[0],"Type"] 
        date = curr_cancer_df.loc[curr_cancer_df.index[0],"Date"] 
        return [site, type1, date]



def read_allClaims1(patient_ID, path_medicare, medicare_columns_list):
    #Codes columns for medicaid
        #NA
    
    #Codes columns for medicare
    medicare_diag_cols = ['DGNS_CD{}'.format(i) for i in range(1, 25+1)]  #ICD9 or ICD10
    medicare_diag_cols_f = []
    for kkk in range(len(medicare_diag_cols)):
        if medicare_diag_cols[kkk] in medicare_columns_list:
            medicare_diag_cols_f.append(medicare_diag_cols[kkk])
    medicare_diag_cols = medicare_diag_cols_f
    
    medicare_proc_cols_2 = ["HCPCS_CD"]                       #HCPCS
    medicare_proc_cols_1 = ['PRCDR_CD{}'.format(i) for i in range(1, 25+1)]  #ICD9 or ICD10
    medicare_proc_cols = medicare_proc_cols_1 + medicare_proc_cols_2
    medicare_proc_cols_f = []
    for kkk in range(len(medicare_proc_cols)):
        if medicare_proc_cols[kkk] in medicare_columns_list:
            medicare_proc_cols_f.append(medicare_proc_cols[kkk])
    medicare_proc_cols = medicare_proc_cols_f
    
    medicare_drug_cols = ["NDC_CD","PROD_SRVC_ID"] 
    medicare_drug_cols_f = []
    for kkk in range(len(medicare_drug_cols)):
        if medicare_drug_cols[kkk] in medicare_columns_list:
            medicare_drug_cols_f.append(medicare_drug_cols[kkk])
    medicare_drug_cols = medicare_drug_cols_f
    
    medicare_drug_related = ["GNN","BN"]
    medicare_drug_related_f = []
    for kkk in range(len(medicare_drug_related)):
        if medicare_drug_related[kkk] in medicare_columns_list:
            medicare_drug_related_f.append(medicare_drug_related[kkk])
    medicare_drug_related = medicare_drug_related_f


    #1.read original health_claims to get proc and diag codes
    #NA
        
     
    #3.Get original medicare_claims    
    xlsx_files = glob.glob(os.path.join(path_medicare, "*.xlsx"))
    split_ID = [a.split('ID')[1] for a in xlsx_files]
    IDs_has_health_files = [a.split('_')[0] for a in split_ID]
    
    #patient_ID = IDs_has_health_files[0]
    
    if patient_ID in IDs_has_health_files:
        file_name = "ID" + str(patient_ID)+ "_all_medicare_claims.xlsx"
        completeName = os.path.join(path_medicare, file_name)
        medicare_df = pd.read_excel(completeName,header=0, index_col=False, dtype='object')       
        lst = ["study_id","claims_date"] + medicare_diag_cols + medicare_proc_cols + medicare_drug_cols + medicare_drug_related
        medicare_df = medicare_df.filter(lst)
        check_date = pd.DataFrame(medicare_df['claims_date']).iloc[0,0]
        if not "/" in check_date:
            #print("Convert date for medicare")
            check_date = pd.DataFrame(medicare_df['claims_date'])
            for k in range(len(check_date)):
                #print(k)
                day = check_date.iloc[k,0][0:2]
                mon = mtn(check_date.iloc[k,0][2:5])
                year = check_date.iloc[k,0][5:]
                newdate = mon + "/" + day + "/" +year 
                medicare_df.iloc[k,1] = newdate
    else:
        medicare_df = pd.DataFrame()
    
    data_loaded = [medicare_df]
    return data_loaded


def read_allClaims2(patient_ID,path_medicaid_heath, path_medicaid_pharm, medicaid_columns_list_health, medicaid_columns_list_pharm):
    #Codes columns for medicaid
    medicaid_diag_cols = ["CDE_DIAG_PRIM","CDE_DIAG_2","CDE_DIAG_3","CDE_DIAG_4"] #ICD 9 or ICD10
    medicaid_diag_cols_f = []
    for kkk in range(len(medicaid_diag_cols)):
        if medicaid_diag_cols[kkk] in medicaid_columns_list_health:
            medicaid_diag_cols_f.append(medicaid_diag_cols[kkk])
    medicaid_diag_cols = medicaid_diag_cols_f
    
    medicaid_proc_cols = ["CDE_PROC_PRIM"]                                        #HCPCS
    medicaid_proc_cols_f = []
    for kkk in range(len(medicaid_proc_cols)):
        if medicaid_proc_cols[kkk] in medicaid_columns_list_health:
            medicaid_proc_cols_f.append(medicaid_proc_cols[kkk])
    medicaid_proc_cols = medicaid_proc_cols_f
    
    medicaid_drug_cols = ["CDE_THERA_CLS_AHFS", "CDE_NDC"]
    medicaid_drug_cols_f = []
    for kkk in range(len(medicaid_drug_cols)):
        if medicaid_drug_cols[kkk] in medicaid_columns_list_pharm:
            medicaid_drug_cols_f.append(medicaid_drug_cols[kkk])
    medicaid_drug_cols = medicaid_drug_cols_f
    
    #Codes columns for medicare
    #NA


    #1.read original health_claims to get proc and diag codes
    xlsx_files = glob.glob(os.path.join(path_medicaid_heath, "*.xlsx"))
    split_ID = [a.split('ID')[1] for a in xlsx_files]
    IDs_has_health_files = [a.split('_')[0] for a in split_ID]
    
    if patient_ID in IDs_has_health_files:
        file_name = "ID" + str(patient_ID)+ "_all_medicaid_healthclaims.xlsx"
        completeName = os.path.join(path_medicaid_heath, file_name)
        medicaid_health_df = pd.read_excel(completeName,header=0, index_col=False, dtype='object')
        lst = ["study_id", "Id_medicaid", "DTE_FIRST_SVC"] +medicaid_diag_cols + medicaid_proc_cols
        medicaid_health_df = medicaid_health_df.filter(lst)
        check_date = pd.DataFrame(medicaid_health_df['DTE_FIRST_SVC']).iloc[0,0]
        if not "/" in check_date:
            print("Convert date medicaid health")
            check_date = pd.DataFrame(medicaid_health_df['DTE_FIRST_SVC'])
            for k in range(len(check_date)):
                #print(k)
                day = check_date.iloc[k,0][0:2]
                mon = mtn(check_date.iloc[k,0][2:5])
                year = check_date.iloc[k,0][5:]
                newdate = mon + "/" + day + "/" +year 
                medicaid_health_df.iloc[k,2] = newdate
    else:
        medicaid_health_df = pd.DataFrame()
    
    #2.get original pharmcy_claims to get drug codes    
    xlsx_files = glob.glob(os.path.join(path_medicaid_pharm, "*.xlsx"))
    split_ID = [a.split('ID')[1] for a in xlsx_files]
    IDs_has_health_files = [a.split('_')[0] for a in split_ID]
    
    if patient_ID in IDs_has_health_files:
        file_name = "ID" + str(patient_ID)+ "_all_medicaid_pharmclaims.xlsx"
        completeName = os.path.join(path_medicaid_pharm, file_name)
        medicaid_pharm_df = pd.read_excel(completeName,header=0, index_col=False, dtype='object')       
        lst = ["study_id", "Id_medicaid", "DTE_FIRST_SVC"] +medicaid_drug_cols
        medicaid_pharm_df = medicaid_pharm_df.filter(lst)
        check_date = pd.DataFrame(medicaid_pharm_df['DTE_FIRST_SVC']).iloc[0,0]
        if not "/" in check_date:
            #print("Convert date for medicaid pharm")
            check_date = pd.DataFrame(medicaid_pharm_df['DTE_FIRST_SVC'])
            for k in range(len(check_date)):
                #print(k)
                day = check_date.iloc[k,0][0:2]
                mon = mtn(check_date.iloc[k,0][2:5])
                year = check_date.iloc[k,0][5:]
                newdate = mon + "/" + day + "/" +year 
                medicaid_pharm_df.iloc[k,2] = newdate
    else:
        medicaid_pharm_df = pd.DataFrame()
        
     
    #3.Get original medicare_claims    
    
    
    data_loaded = [medicaid_health_df,medicaid_pharm_df]
    return data_loaded

##### errors
class CustomError(Exception):
    pass

def int_check(parameter):
    if not isinstance(parameter, int):
        raise ValueError("Parameter -mld or -mle must be an integer")
    # Rest of the function logic

def check_both(month_len_medicaid, month_len_medicare, start_medicaid, start_medicare):
    if month_len_medicaid is None:
        raise ValueError("Month length of Medicaid or other insurance enrollment is required by -mld parameter")
    if month_len_medicare is None:
        raise ValueError("Month length of Medicare is required by -mle parameter")
    if start_medicaid is None:
        raise ValueError("Start date of Medicaid or other insurance enrollment is required by -sd parameter")
    if start_medicare is None:
        raise ValueError("Start date of Medicare enrollment is required by -se parameter")

def check_medicare1(month_len_medicaid, month_len_medicare, start_medicaid, start_medicare):
    if month_len_medicaid is not None and month_len_medicare is None:
        raise ValueError("Wrong parameter, use -mle instead of -mld for the month length of Medicare. Or use -numdata 2 for Medicaid or other insurance enrollment")
    if month_len_medicare is None:
        raise ValueError("Month length of Medicare is required by -mle parameter")
    if start_medicaid is not None and start_medicare is None:
        raise ValueError("Wrong parameter, use -se instead of -sd for the start date of Medicare enrollment. Or use -numdata 2 for Medicaid or other insurance enrollment")
    if start_medicare is None:
        raise ValueError("Start date of Medicare enrollment is required by -se parameter")

def check_matched_files(num_data, mecareClaims, mecareEnroll, mecaidClaims, mecaidClaims2, mecaidEnroll):
    default_mecareClaims = "medicare_claims_new.csv"
    default_mecareEnroll = "medicare_enroll_new.csv"
    default_mecaidClaims = "medicaid_claims_new.csv"
    default_mecaidClaims2 = "medicaid_Rxclaims_new.csv"
    default_mecaidEnroll = "medicaid_enroll_new.csv"
    if num_data == "1":
        if mecaidClaims != default_mecaidClaims or mecaidClaims2 != default_mecaidClaims2 or mecaidEnroll != default_mecaidEnroll:
            raise ValueError("User choose Medicare only but input claim or enrollment files are related to Medicaid or other enrollment. Please use -mecareClaims and -mecareEnroll for Medicare, or use -numdata 2 for Medicaid or other enrollment only or -numdata 0 for both.")
            #warnings.warn("User choose Medicare only but input claim or enrollment files are related to Medicaid or other enrollment. This may cause unexpected behavior.", UserWarning)
    elif num_data == "2":
        if mecareClaims != default_mecareClaims or mecareEnroll != default_mecareEnroll:
            raise ValueError("User choose Medicaid or other enrollment only but input claim or enrollment files are related to Medicare. Please use -mecaidClaims, -mecaidClaims and -mecaidEnroll for Medicaid or other enrollment, or use -numdata 1 for Medicaid only or -numdata 0 for both.")
            #warnings.warn("User choose Medicaid or other enrollment only but input claim or enrollment files are related to Medicare. This may cause unexpected behavior.", UserWarning)


def check_medicaid2(month_len_medicaid, month_len_medicare, start_medicaid, start_medicare):
    if month_len_medicare is not None and month_len_medicaid is None:
        raise ValueError("Wrong parameter, use -mld instead of -mle for the month length of Medicaid or other insurance enrollment. Or use -numdata 1 for Medicare enrollment")
    if month_len_medicaid is None:
        raise ValueError("Month length of Medicaid or other insurance enrollment is required by -mld parameter")
    if start_medicare is not None and start_medicaid is None:
        raise ValueError("Wrong parameter, use -sd instead of -se for the start date of Medicaid or other insurance enrollment. Or use -numdata 1 for Medicare enrollment")
    if start_medicaid is None:
        raise ValueError("Start date of Medicaid or other insurance enrollment is required by -sd parameter")

def check_numdata(num_data):
    if num_data not in ["0", "1", "2"]:
        raise ValueError("Wrong parameter, use 0, 1 or 2 for both, only Medicare, only Medicaid or other claims")



