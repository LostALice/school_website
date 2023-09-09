SELECT subject.SUBJECT_ID,  subject.NAME, subject.YEAR, subject.START_DATE, subject.END_DATE, subject.SETTLEMENT_START_DATE, subject.SETTLEMENT_END_DATE 
FROM subject
INNER JOIN project ON subject.SUBJECT_ID = project.SUBJECT_ID
INNER JOIN member ON project.PROJECT_ID = member.PROJECT_ID
WHERE member.NID = "D1177531" and subject.ENABLE = 1;