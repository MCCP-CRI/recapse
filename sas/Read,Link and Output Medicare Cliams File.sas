*read pre processed Medicare Claims Data
*DME, MEDPAR, NCH, OUTPAT, PDE files;


libname mc 'N:\Medicare 2015\Data With Selected Variable';
data dme9916;
set mc.dme9916;
	format claim_date_dme mmddyy10.;
dfile="DME";
	claim_date_dme=MDY (input(from_dtm, 8.0), input(from_dtd, 8.0), input(from_dty, 8.0));
keep  patient_id claim_id dfile clm_type dgns_cd1 - dgns_cd12 HCPCS_CD
hcfaspcl  ndc_cd  claim_date_dme ;
run;
proc sort data=dme9916; by patient_id;
run;
data medpar9916;
set mc.medpar9916;

format claim_date_medpar mmddyy10.;
dfile="MEDPAR";
	Claim_Date_MEDPAR = MDY(INPUT(ADMSNDTM,8.0), INPUT(ADMSNDTD,8.0), INPUT(ADMSNDTY,8.0));
array dgna(25) DGNsCD1-DGNsCD25;
array dgnb(25) DGNs_CD1-DGNs_CD25;	
do i= 1 to 25;
dgnb(i)=dgna(i);
end;
keep patient_id dfile  Claim_Date_MEDPAR LOSCNT PRCDRCD1-PRCDRCD25 DGNs_CD1-DGNs_CD25 ;
run;

proc sort data=medpar9916; by patient_id;
run;

data nch9916;
set mc.nch9916;

format claim_date_nch mmddyy10.;
dfile="NCH";
Claim_Date_NCH = MDY(INPUT(expnsdt1m,8.0), INPUT(expnsdt1d,8.0), INPUT(expnsdt1y,8.0));
keep Patient_ID claim_id dfile  Claim_Date_NCH
	dgns_cd1-dgns_cd12 LINDGNS HCPCS_CD  HCFASPCL  ;
run;

proc sort data=nch9916; by patient_id;
run;

data outpat9916;
set mc.outpat9916;
format claim_date_outpat   mmddyy10.;
dfile="OUTPAT";
claim_Date_outpat = MDY (INPUT(FROM_DTM,8.0), INPUT(FROM_DTD,8.0), INPUT(FROM_DTY,8.0));*create diag date;
keep patient_id claim_id dfile dgns_cd1 -dgns_cd25 prcdr_cd1 -prcdr_cd13 hcpcs_cd  REV_CNTR  
	claim_Date_outpat ;
run;
run;
proc sort data=outpat9916; by patient_id;
run;

data pde0716;
set mc.pdesaf0716;
format claim_date_pde mmddyy10.;
dfile="PDE";
claim_date_pde=MDY (input(srvc_mon, 8.0), input(srvc_day, 8.0), input(srvc_yr, 8.0));

keep patient_id  dflie prod_srvc_id  claim_date_pde   DAYS_SUPLY_NUM GCDF_DESC GNN BN;
run;


proc sort data=PDE0716; by patient_id;
run;

data Medicare;
set dme9916 medpar9916 nch9916 outpat9916 pde0716;
run;
proc sort data=medicare nodup; by patient_id;run;


****************Claims;
libname out1 'Z:\UG3-UH3\UH3\Data Analysis\Analysis Data\Updated Dec 12 2020';
data KCR_Medicare_Claims_FB0015;*Medicare claims;
merge Medicare(in=a) out1.id_crosswork_uh3(in=b);*link with incidence file for Female breast cancer patients;
format claims_date mmddyy10.;
by patient_id;
if a and b;

if dfile='' then dfile='PDE';

array prca(13) prcdr_cd1 -prcdr_cd13;
array prcb(13) PRCDRCD1-PRCDRCD13;

do j= 1 to 13;
	if prca(j) ne '' then prcb(j)=prca(j);
end;

array datea (5) claim_date_pde claim_Date_outpat Claim_Date_NCH
			Claim_Date_MEDPAR  claim_date_dme;
do i= 1 to 5;
	if claims_date=. then claims_date=datea(i);
end;
label PRCDRCD1 ='Procedure Code';
drop  i j prcdr_cd1 -prcdr_cd13 claim_date_pde claims_id claim_Date_outpat Claim_Date_NCH
			Claim_Date_MEDPAR  claim_date_dme clm_type;
run;
data out1.KCR_Medicare_Claims_FB0015;
set KCR_Medicare_Claims_FB0015;
drop patient_id ;
run;
