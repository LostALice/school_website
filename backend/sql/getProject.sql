SELECT * 
FROM 
	project
INNER JOIN 
	member on project.PROJECT_ID = member.PROJECT_ID
;