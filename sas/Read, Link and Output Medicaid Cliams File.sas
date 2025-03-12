
filename dat 'Z:\Data Linkage 2019\Linked Mediciad Claims\Program';
************************;
libname kcrid 'Z:\UG3-UH3\UH3\Data Analysis\Analysis Data\Updated Dec 12 2020';
data ids;
set kcrid.id_crosswork_uh3;
run;

libname mdlist 'Z:\Data Linkage 2019\Step7-Get Final Dataset';
data md;
set mdlist.final_ids;
drop index;
run;
proc sort data=md nodupkey; by id_medicaid; run;

*****2. Get Data for Medicaid health claims;

data mdall_list;*FB0015;
merge ids(in=a) mdall(in=b);
by patient_id;
if a and b;;
keep patient_id study_id id_medicaid;
run;
proc sort data= mdall_list; by id_medicaid; run;

%include dat ("Read in Medicaid Claims.sas");
data MedicaidID_w_claims;
set claims00-claims19;*from sas program read medical claims;
keep  SAK_CLAIM ID_MEDICAID CDE_DIAG_PRIM CDE_DIAG_2-CDE_DIAG_4
CDE_PROC_PRIM CDE_MODIFIER_1 CDE_MODIFIER_2 CDE_REVENUE 
DTE_FIRST_SVC  DTE_LAST_SVC ;
run;
proc sort data=MedicaidID_w_claims ; by id_medicaid; run;
*************check this part****;
data mdenroll_claim;
merge mdall_list(in=a) MedicaidID_w_claims(in=b);
by id_medicaid;
if a and b then index_claim=1;*both;
else if a then index_claim=0;*no claim, only enroll;
else if b then index_claim=9;
drop ppatid studyid ;
run;
proc freq data=mdenroll_claim;table index_claim; run;

data kcrid.KCR_Medicaid_HealthClaims_FB0015;
set mdenroll_claim(in=b);
if index_claim=1;
drop patient_id index_claim;
run;
*Replace '#' as '';
data kcrid.Medicaid_HealthClaims_FB0015;
set kcrid.KCR_Medicaid_HealthClaims_FB0015;
array icd(8) CDE_DIAG_PRIM CDE_DIAG_2-CDE_DIAG_4
CDE_PROC_PRIM CDE_MODIFIER_1 CDE_MODIFIER_2 CDE_REVENUE;
do i= 1 to 8;
if substr(icd(i),1,1)='#' then icd(i)='';
end;
drop I;
run;
*pharm;
libname out 'Z:\Data Linkage 2019\Linked Mediciad Claims\Analysis Data';
data medicaid_RX;
set out.medicaidrx_list_w_claim;
id_medicaid2=id_medicaid*1;
drop id_medicaid;
run;

proc sort data=medicaid_RX ; by id_medicaid2; run;

data mdenroll_rxclaim;
merge mdall_list(in=a) medicaid_RX(in=b rename=id_medicaid2=id_medicaid);
by id_medicaid;
if a and b then index_claim=1;*both;
else if a then index_claim=0;*no claim, only enroll;
else if b then index_claim=9;
drop ppatid studyid ;
run;
proc freq data=mdenroll_rxclaim;table index_claim; run;

data kcrid.KCR_Medicaid_PharmClaims_FB0015;
set mdenroll_rxclaim(in=b);
if index_claim=1;
drop patient_id index_claim;
run;


