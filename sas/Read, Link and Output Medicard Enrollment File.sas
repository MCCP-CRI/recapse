
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

***1. get data for Medicaid Enroll;
libname md2 'Z:\Data Linkage 2019\Linked Mediciad Claims\Analysis Data';
data mdenroll;
set md2.medicaid_master_coverage_index;
drop master ;
run;
proc sort data=mdenroll nodupkey; by id_medicaid; run;
data mdall;
merge md(in=a) mdenroll(in=b);
by id_medicaid;
if a and b then index=1;
else if a then index=2;
else if b then index=3;
array mona(240) mon1-mon240;
array yeara(20) year_flag00-year_flag19;

PATIENT_ID=CATS("42",PUT(PPATID, Z8.));
do i=1 to 20;
	do j=1 to 12;
	mona((i-1)*12+j)= substr(yeara(i),j,1);
	end;
end;
drop ppatid studyid year_flag00-year_flag19 index i j;
run;
proc sort data=mdall; by patient_id; run;
data kcrid.KCR_Medicaid_Enroll_FB0015;
merge ids(in=a) mdall(in=b);
by patient_id;
if a and b;
drop patient_id;
run;
