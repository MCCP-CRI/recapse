*Read the PEDSF file and output the enrollment variables****;

*https://healthcaredelivery.cancer.gov/seermedicare/program/sas.html;
*Medicare Enrollment range: 1991.1-2017.12;
******************enroll;
libname in3 'N:\Medicare 2015\Data With Selected Variable';
data mcenroll;
set in3.pedsf;*Concatenated PEDSF file;
keep patient_id mon1-mon324 GHO1-GHO324;*month enroll index;
run;
proc sort data=mcenroll; by patient_id; run;

data out1.KCR_Medicare_ENROLL_FB0015;*medicare enrolls;
merge mcenroll(in=b)  out1.id_crosswork_uh3(in=a);
by patient_id;
if a and b;
keep study_id mon1-mon324 GHO1-GHO324;
run;
