#Code by AkinoAlice@Tyrant_Rex

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from authenticate import AUTHENTICATION

import handler
import uuid
import datetime

app = FastAPI(debug=True)

#CORS config
origins = [
    "http://localhost",
    # [dev] port = page port
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# login api
@app.post("/login", status_code=200)
async def login(nid:str, password:str):
    access = AUTHENTICATION()
    token = access.authenticate(nid, password)

    if token:
        return {
            "access": True,
            "token": token,
        }
    else:
        return {
            "access": False,
        }

# Logout api
@app.post("/logout", status_code=200)
async def logout(nid:str):
    ...

# token validation api
@app.post("/JWTValidation", status_code=200)
async def JWTValidation(nid: str, token: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)

    if token_validation:
        return {
            "access": True,
            "token": token,
        }
    else:
        return {
            "access": False,
        }

# token validation api
@app.post("/TimeoutStatus", status_code=200)
async def TimeoutStatus(nid: str, token: str):
    access = AUTHENTICATION()
    timeout = access.verify_timeout(nid, token)
    return {
       "timeout": timeout,
    }
    # token_validation = access.verify_jwt_token(nid)

# subject
@app.post("/getSubject", status_code=200)
def getSubject(nid: str, token: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)

    if not token_validation:
        return {
            "status_code": 403,
        }

    subject_data = handler.SQLHandler().getSubjectData(nid)
    data_ = []
    if subject_data or subject_data == []:
        for i in subject_data:
            data_.append({
                "subjectUUID": i[0],
                "name": i[1],
                "year": i[2],
                "startDate": i[3],
                "endDate": i[4],
                "settlementStartDate": i[5],
                "settlementEndDate": i[6],
            })
        return data_
    else:
        return {
            "status_code": 500
        }

@app.post("/createSubject", status_code=200)
def createSubject(
    nid: str,
    token: str,
    subjectName: str,
    year: int,
    startDate: str,
    endDate: str,
    settlementStartDate: str,
    settlementEndDate: str
):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    for i in [subjectName, year, startDate, endDate, settlementStartDate, settlementEndDate]:
        if not AUTHENTICATION().SQLInjectionCheck(prompt=i):
            return {
                "SQLInjectionCheck": False,
            "status_code": 400
            }

    subjectData = {
        "subjectUUID": str(uuid.uuid4()),
        "projectUUID": str(uuid.uuid4()),
        "subjectName": subjectName,
        "year": year,
        "startDate": startDate,
        "endDate": endDate,
        "settlementStartDate": settlementStartDate,
        "settlementEndDate": settlementEndDate,
        "nid": nid
    }

    if handler.SQLHandler().createSubjectData(subjectData):
        return {
            "status_code": 200,
            "subjectUUID": subjectData["subjectUUID"]
        }
    else:
        return {
            "status_code": 500
        }

@app.post("/deleteSubject", status_code=200)
def deleteSubject(nid: str, token: str, subjectUUID: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    if not AUTHENTICATION().SQLInjectionCheck(prompt=subjectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }
    success = handler.SQLHandler().deleteSubjectData(subjectUUID)
    if success:
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 500
        }

# project
@app.post("/getProject", status_code=200)
def getProject(nid: str, token: str, subjectUUID: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)

    if not token_validation:
        return {
            "status_code": 403,
        }
    projectData = {
        "subjectUUID": subjectUUID,
        "NID": nid
    }
    project_data = handler.SQLHandler().getProjectData(projectData)
    if project_data or project_data == []:
        data_ = []

        for i in zip(
            project_data["name"],
            project_data["announcements"],
            project_data["student"],
            project_data["teacher"],
            project_data["group"],
            project_data["assignment"],
            project_data["projectID"],
        ):
            data_.append(
                {
                    "name": i[0][0],
                    "announcements": i[1][0],
                    "student": i[2][0],
                    "teacher": i[3][0],
                    "group": i[4][0],
                    "assignment": i[5][0],
                    "projectID": i[6][0],
                }
            )
        return data_
    else:
        return {
            "status_code": 500
        }

@app.post("/createProject", status_code=200)
def createProject(nid: str, token: str, subjectUUID: str, projectName: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    for i in [subjectUUID, projectName]:
        if not AUTHENTICATION().SQLInjectionCheck(prompt=i):
            return {
                "SQLInjectionCheck": False,
            "status_code": 400
            }

    params = {
        "subjectUUID": subjectUUID,
        "projectUUID": str(uuid.uuid4()),
        "projectName": projectName,
        "nid": nid,
    }
    if handler.SQLHandler().createProjectData(params):
        return {
            "status_code": 200,
            "subjectUUID": params["projectUUID"],
        }
    else:
        return {
            "status_code": 500
        }

@app.post("/deleteProject", status_code=200)
def deleteProject(nid: str, token: str, projectUUID: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }
    success = handler.SQLHandler().deleteProjectData(projectUUID)
    if success:
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 500
        }

@app.post("/getProjectInfo", status_code=200)
def getProjectInfo(nid: str, token: str, projectUUID: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }
    projectInfo = handler.SQLHandler().getProjectInfo(projectUUID)
    data = {
        "subjectUUID": projectInfo[0],
        "subjectName": projectInfo[1],
        "year": projectInfo[2],
        "startDate": projectInfo[3],
        "endDate": projectInfo[4],
        "settlementStartDate": projectInfo[5],
        "settlementEndDate": projectInfo[6],
    }
    return data

# student
@app.post("/getStudentData", status_code=200)
def getStudentData(nid: str, token: str, projectUUID: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    studentData = handler.SQLHandler().getStudentData(projectUUID)
    if studentData or studentData == []:
        data = []
        for i in studentData:
            data.append({
                "nid": i[0],
                "name": i[1],
            })
        return data
    else:
        return {
            "status_code": 500,
        }

@app.post("/getStudentList", status_code=200)
def getStudentList(nid: str, token: str, projectUUID):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    studentList = handler.SQLHandler().getStudentList()
    data = []
    if studentList or studentList == []:
        for i in studentList:
            data.append({
                "nid": i[0],
                "name": i[1]
            })
        return data
    else:
        return {
            "status_code": 500
        }

@app.post("/newStudent", status_code=200)
def newStudent(nid: str, token: str, projectUUID: str, studentNID: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }
    for i in [projectUUID, studentNID]:
        if not AUTHENTICATION().SQLInjectionCheck(prompt=i):
            return {
                "SQLInjectionCheck": False,
                "status_code": 400
            }
    params = {
        "nid": studentNID,
        "projectUUID": projectUUID,
    }
    success = handler.SQLHandler().newStudent(params)
    if success:
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 500
        }

@app.post("/deleteStudent", status_code=200)
def deleteStudent(nid: str, token: str, studentNID: str, projectUUID: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }
    for i in [studentNID, projectUUID]:
        if not AUTHENTICATION().SQLInjectionCheck(prompt=i):
            return {
                "SQLInjectionCheck": False,
                "status_code": 400
            }
    params = {
        "nid": studentNID,
        "projectUUID": projectUUID
    }
    if handler.SQLHandler().deleteStudent(params):
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 500
        }

@app.post("/getStudentInfo", status_code=200)
def getStudentInfo(nid: str, token: str, studentNID: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    if not AUTHENTICATION().SQLInjectionCheck(prompt=studentNID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    studentInfo = handler.SQLHandler().getStudentInfo(studentNID)
    if studentInfo:
        return {
            "name": studentInfo[0],
            "permission": studentInfo[1]
        }
    else:
        return {
            "status_code": 500
        }

# teacher
@app.post("/getTeacherData", status_code=200)
def getTeacherData(nid: str, token: str, projectUUID: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    teacherData = handler.SQLHandler().getTeacherData(projectUUID)
    if teacherData or teacherData == []:
        data = []
        for i in teacherData:
            data.append({
                "nid": i[0],
                "name": i[1],
            })
        return data
    else:
        return {
            "status_code": 500,
        }

@app.post("/getTeacherList", status_code=200)
def getTeacherList(nid: str, token: str, projectUUID):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    teacherList = handler.SQLHandler().getTeacherList()
    data = []
    if teacherList or teacherList == []:
        for i in teacherList:
            data.append({
                "nid": i[0],
                "name": i[1]
            })
        return data
    else:
        return {
            "status_code": 500
        }

@app.post("/newTeacher", status_code=200)
def newTeacher(nid: str, token: str, projectUUID: str, teacherNID: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }
    for i in [projectUUID, teacherNID]:
        if not AUTHENTICATION().SQLInjectionCheck(prompt=i):
            return {
                "SQLInjectionCheck": False,
                "status_code": 400
            }
    params = {
        "nid": teacherNID,
        "projectUUID": projectUUID,
    }
    success = handler.SQLHandler().newTeacher(params)
    if success:
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 500
        }

@app.post("/deleteTeacher", status_code=200)
def deleteTeacher(nid: str, token: str, teacherNID: str, projectUUID: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }
    for i in [teacherNID, projectUUID]:
        if not AUTHENTICATION().SQLInjectionCheck(prompt=i):
            return {
                "SQLInjectionCheck": False,
                "status_code": 400
            }
    params = {
        "nid": teacherNID,
        "projectUUID": projectUUID
    }
    if handler.SQLHandler().deleteTeacher(params):
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 500
        }

@app.post("/getTeacherInfo", status_code=200)
def getTeacherInfo(nid: str, token: str, teacherNID: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    if not AUTHENTICATION().SQLInjectionCheck(prompt=teacherNID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    teacherInfo = handler.SQLHandler().getTeacherInfo(teacherNID)
    if teacherInfo:
        return {
            "name": teacherInfo[0],
            "permission": teacherInfo[1]
        }
    else:
        return {
            "status_code": 500
        }

# announcement
@app.post("/getAnnouncementData", status_code=200)
def getAnnouncementData(nid: str, token: str, projectUUID: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    announcementData = handler.SQLHandler().getAnnouncementData(projectUUID)
    data = []
    if announcementData or announcementData == []:
        for i in announcementData:
            data.append({
                "announcementUUID": i[0],
                "author": i[1],
                "title": i[2],
                "date": i[3]
            })
        return data
    else:
        return {
            "status_code": 500
        }

@app.post("/createAnnouncement", status_code=200)
def createAnnouncement(nid: str, token: str, projectUUID: str, title: str, context: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }
    for i in [projectUUID, title, context]:
        if not AUTHENTICATION().SQLInjectionCheck(prompt=i):
            return {
                "SQLInjectionCheck": False,
            "status_code": 400,
            }

    params = {
        "PROJECT_ID": projectUUID,
        "ANNOUNCEMENTS_ID": str(uuid.uuid4()),
        "TITLE": title,
        "ANNOUNCEMENTS": context,
        "AUTHOR": nid,
        "LAST_EDIT": datetime.date.today()
    }
    success = handler.SQLHandler().createAnnouncement(params)
    if success:
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 500
        }

@app.post("/deleteAnnouncement", status_code=200)
def deleteAnnouncement(nid: str, token: str, announcementUUID: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    if not AUTHENTICATION().SQLInjectionCheck(prompt=announcementUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    if handler.SQLHandler().deleteAnnouncement(announcementUUID):
        return {
            "status_code": 200
        }
    return {
        "status_code": 500
    }

@app.post("/getAnnouncementInfo", status_code=200)
def getAnnouncementInfo(nid: str, token: str, announcementUUID: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    if not AUTHENTICATION().SQLInjectionCheck(prompt=announcementUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    announcementInfo = handler.SQLHandler().getAnnouncementInfo(announcementUUID)

    if announcementInfo:
        return {
            "author": announcementInfo[0],
            "title": announcementInfo[1],
            "context": announcementInfo[2],
            "date": announcementInfo[3]
        }
    else:
        return {
            "status_code": 500
        }

# group
@app.post("/getGroupData", status_code=200)
def getGroupData(nid: str, token: str, projectUUID: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    groupData = handler.SQLHandler().getGroupData(projectUUID)
    if groupData or groupData == []:
        return groupData
    else:
        return {
            "status_code": 500
        }

@app.post("/newGroup", status_code=200)
def newGroup(nid: str, token: str, projectUUID: str, member: str, group_name: str, GID):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    params = {
        "projectUUID": projectUUID,
        "name": group_name,
        "nid": member,
        "GID": GID
    }
    if handler.SQLHandler().newGroup(params):
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 500
        }

@app.post("/getGroupToken", status_code=200)
def getGroupToken(nid: str, token: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    return {
        "GID": str(uuid.uuid4())
    }

@app.post("/getGroupTeacherData", status_code=200)
def getGroupTeacherData(nid: str, token: str, projectUUID: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    teacher_data = handler.SQLHandler().getGroupTeacherData(projectUUID)
    teacher_list = []
    for i in teacher_data:
        teacher_list.append({
            "nid": i[0],
            "name": i[1],
        })

    if teacher_list:
        return teacher_list
    else:
        return {
            "status_code": 500
        }

@app.post("/getGroupStudentData", status_code=200)
def getGroupStudentData(nid: str, token: str, projectUUID: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    student_data = handler.SQLHandler().getGroupStudentData(projectUUID)
    student_list = []
    for i in student_data:
        student_list.append({
            "nid": i[0],
            "name": i[1],
        })

    if student_list:
        return student_list
    else:
        return {
            "status_code": 500
        }

@app.post("/getGroupInfo", status_code=200)
def getGroupInfo(nid: str, token: str, groupUUID: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    if not AUTHENTICATION().SQLInjectionCheck(prompt=groupUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    groupInfo = handler.SQLHandler().getGroupInfo(groupUUID)

    for i in groupInfo:
        if groupInfo[i] == []:
            groupInfo[i] = "None"
        if type(groupInfo[i]) == list:
            groupInfo[i] = ", ".join(groupInfo[i])

    return groupInfo

@app.post("/deleteGroup", status_code=200)
def deleteGroup(nid: str, token: str, groupUUID: str, projectUUID: str):
    access = AUTHENTICATION()
    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return {
            "status_code": 403,
        }

    if not AUTHENTICATION().SQLInjectionCheck(prompt=groupUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }
    params = {
        "groupUUID": groupUUID,
        "projectUUID": projectUUID,
    }

    handler.SQLHandler().deleteGroup(params)

@app.get("/",status_code=200)
async def main_page():
    return {
        "status_code": 200,
    }

if __name__ == "__main__":
    # development only
    # uvicorn main:app --reload
    app.run(debug=True)