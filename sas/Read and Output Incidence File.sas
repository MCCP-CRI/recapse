
libname in 'Z:\KCR Data\1995-2019 SEER\SEER 2020 Submission\Update';
data fbreast0015;
set in.ky9503 in.ky0409 in.ky1019;
if 2000<=year_diag <=2015;
if seersite = 26000;
if sex=2;
if ICDO3BehaveCode=3;
PATIENT_ID=CATS("42",PUT(PPATID, Z8.));
run;

*link new KCR information with old study_id( which used to link claims data);
libname outold 'Z:\UG3-UH3\UH3\Data Analysis\Analysis Data\Update Oct 2021';
data fbreastlist;
set outold.fbreastlistold;run;

proc sort data=fbreast0015 ; by patient_id CentralSequenceNumber; run;
data fbreast0015_2;
merge fbreast0015(in=a) fbreastlist; 
by patient_id ;
if a;
if csfactor1='010' then er_stat=1;
else if csfactor1='020' then er_stat=0;
else er_stat=9;
if csfactor2='010' then pr_stat=1;
else if csfactor2='020' then pr_stat=0;
else pr_stat=9;
if csfactor9='010' then her2_stat=1;
else if csfactor9='020' then her2_stat=0;
else her2_stat=9;
tract=cats(county, censtract2010);
keep study_id patient_id ppatid CentralSequenceNumber  DIAGAGE race1 PrimarySite BestStageGrp SEERSummStg2000 DerivedSS2000
	grade  year_diag Laterality er_stat pr_stat her2_stat RXSummSurgPrimSite 
	 RXSummRadiation RXSummChemo  RXSummHormone
	TNMClinT TNMClinN TNMClinM TNMPathT TNMPathN TNMPathM 
	RegNodesExamined RegNodesPositive CSTumorSize CSTumorSizeExtEval
	CSLymphNodes  RuralUrbanContin2013
	Date_1Recur appal VitalStat  CauseOfDeath  Date_dx date_Birth date_LC	tract;
run;
*LINK with RUCA code;
PROC IMPORT OUT= WORK.RUCAKY 
            DATAFILE= "Z:\KCR Data\Population\RUCA code 2019.xlsx" 
            DBMS=EXCEL REPLACE;
     RANGE="Sheet1$"; 
     GETNAMES=YES;
     MIXED=NO;
     SCANTEXT=YES;
     USEDATE=YES;
     SCANTIME=YES;
RUN;
data rucaky2;
set rucaky;
keep ruca2010 tract County;
run;
proc sort data=rucaky2; by tract;run;
proc sort data=fbreast0015_2; by tract; run;
data fbreast0015_3;
merge fbreast0015_2(in=a) rucaky2(in=b );
by tract;
if a;
drop tract;
run;

**Link with other cancer sites;
* to get subsequent caner information, eg. sites, date_dx, for Female Breast;
data allkcr;
set in.ky9503 in.ky0409 in.ky1019;
PATIENT_ID=CATS("42",PUT(PPATID, Z8.));
keep patient_id centralsequencenumber PrimarySite ICDO3Histology seersite date_dx;
run;
proc sort data=allkcr; by patient_id centralsequencenumber; run;
data allFBpateint_withcancer;
merge fbreastlist(in=a) allkcr;
by patient_id;
if a;
if seersite ne 26000;*non FB cases;
run;
/*
proc freq; table ICDO3Histology ; where  primarysite in ('C502','C504','C509'); run;
*/
proc transpose data=allFBpateint_withcancer out=FBpatient1 prefix=site_o;
var primarysite ;
    by patient_id;
run;
proc transpose data=allFBpateint_withcancer out=FBpatient2 prefix=date_o;
var date_dx ;
    by patient_id;
run;
proc transpose data=allFBpateint_withcancer out=FBpatient3 prefix=sequence_o;
var  centralsequencenumber;
    by patient_id;
run;
data fbpatient_withOtherCancer;*FB patients with their cancer information on other sites;
merge fbpatient1-fbpatient3;
by patient_id;
drop _name_;
run;
proc sort data=fbreast0015_3; by patient_id; run;
data fbreast0015_4;
merge fbreast0015_3(in=a) fbpatient_withOtherCancer;
by patient_id;
if a;
run;
proc print data=fbreast0015_4;
where patient_id='4200047616';run;
proc sort data=fbreast0015_4; by study_id  centralsequencenumber; run;
libname out1 'Z:\UG3-UH3\UH3\Data Analysis\Analysis Data\Update Oct 2021';

data out1.UH3_NewKCRdata_NovUpdate;*new kcr info linked with previous created study_id;
set fbreast0015_4 ; 
by study_id  centralsequencenumber;
drop patient_id ppatid;
run;


data test;
set fbreast0015_4;
drop study_id patient_id ppatid;

run;

ods html path="Z:\UG3-UH3\UH3\Data Analysis\Analysis Data\Update Oct 2021" 
        gpath="Z:\UG3-UH3\UH3\Data Analysis\Analysis Data\Update Oct 2021"(URL=none);
ods html newfile=proc; 
proc freq data=test;
table _all_ ;
run;
ods html close;
