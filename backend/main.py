# Code by AkinoAlice@Tyrant_Rex

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from setup import SettingSetupHandler
from shutil import copyfileobj
from pandas import read_excel
from inspect import stack

from authenticate import AUTHENTICATION
from handler import SQLHandler, LOGGER
from permission import PERMISSION

import datetime
import json
import uuid
import os

try:
    assert os.path.exists("./setting.json")
except AssertionError:
    SettingSetupHandler().file_setup()

with open("./setting.json", "r") as f:
    json_file = json.load(f)
    DEBUG = json_file["debug"]

app = FastAPI(debug=DEBUG)

# CORS config
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


@app.get("/login/{nid}/{password}", status_code=200)
async def login(nid: str, password: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

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

# token validation


@app.get("/getPermissionLevel/{nid}/{token}", status_code=200)
async def getPermissionLevel(nid: str, token: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    return PERMISSION(nid).get_levels()


@app.get("/JWTValidation/{nid}/{token}", status_code=200)
async def JWTValidation(nid: str, token: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

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


@app.get("/TimeoutStatus/{nid}/{token}", status_code=200)
async def TimeoutStatus(nid: str, token: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    timeout = access.verify_timeout(nid, token)

    if not all([token_validation, timeout]):
        return {
            "status_code": 403,
            "timeout": True
        }
    return {
        "status_code": 200,
        "timeout": False
    }

# Administration


@app.get("/getLogs/{nid}/{token}", status_code=200)
def getLog(nid: str, token: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    return LOGGER().record()


@app.post("/forceChangePassword", status_code=200)
def forceChangePassword(nid: str, token: str, target_nid: str, password: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    for i in [target_nid, password]:
        if not AUTHENTICATION().SQLInjectionCheck(prompt=i):
            return {
                "SQLInjectionCheck": False,
                "status_code": 400
            }


    if access.forceChangePassword(target_nid, password):
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 400
        }

# Subject


@app.get("/getSubject/{nid}/{token}", status_code=200)
def getSubject(nid: str, token: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    subject_data = SQLHandler().getSubjectData(nid)
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
        return HTTPException(status_code=500, detail="No data available")


@app.post("/createSubject", status_code=200)
def createSubject(
        nid: str,
        token: str,
        subjectName: str,
        year: int,
        startDate: str,
        endDate: str,
        settlementStartDate: str,
        settlementEndDate: str):

    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

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

    if SQLHandler().createSubjectData(subjectData):
        return {
            "status_code": 200,
            "subjectUUID": subjectData["subjectUUID"]
        }
    else:
        return {
            "status_code": 500
        }


@app.delete("/deleteSubject/{nid}/{token}/{subjectUUID}", status_code=200)
def deleteSubject(nid: str, token: str, subjectUUID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    if not AUTHENTICATION().SQLInjectionCheck(prompt=subjectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }
    success = SQLHandler().deleteSubjectData(subjectUUID)
    if success:
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 500
        }

# project


@app.get("/getProject/{nid}/{token}/{subjectUUID}", status_code=200)
def getProject(nid: str, token: str, subjectUUID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    projectData = {
        "subjectUUID": subjectUUID,
        "NID": nid
    }

    project_data = SQLHandler().getProjectData(projectData)
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
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

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
    if SQLHandler().createProjectData(params):
        return {
            "status_code": 200,
            "subjectUUID": params["projectUUID"],
        }
    else:
        return {
            "status_code": 500
        }


@app.delete("/deleteProject/{nid}/{token}/{projectUUID}", status_code=200)
def deleteProject(nid: str, token: str, projectUUID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }
    success = SQLHandler().deleteProjectData(projectUUID)
    if success:
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 500
        }


@app.get("/getProjectInfo/{nid}/{token}/{projectUUID}", status_code=200)
def getProjectInfo(nid: str, token: str, projectUUID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }
    projectInfo = SQLHandler().getProjectInfo(projectUUID)
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


@app.get("/getStudentData/{nid}/{token}/{projectUUID}", status_code=200)
def getStudentData(nid: str, token: str, projectUUID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    studentData = SQLHandler().getStudentData(projectUUID)
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


@app.get("/getStudentList/{nid}/{token}/{projectUUID}", status_code=200)
def getStudentList(nid: str, token: str, projectUUID):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    studentList = SQLHandler().getStudentList()
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
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")
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
    success = SQLHandler().newStudent(params)
    if success:
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 500
        }


@app.delete("/deleteStudent/{nid}/{token}/{studentNID}/{projectUUID}", status_code=200)
def deleteStudent(nid: str, token: str, studentNID: str, projectUUID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")
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
    if SQLHandler().deleteStudent(params):
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 500
        }


@app.get("/getStudentInfo/{nid}/{token}/{studentNID}", status_code=200)
def getStudentInfo(nid: str, token: str, studentNID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    if not AUTHENTICATION().SQLInjectionCheck(prompt=studentNID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    studentInfo = SQLHandler().getStudentInfo(studentNID)
    if studentInfo:
        return {
            "name": studentInfo[0],
            "permission": studentInfo[1]
        }
    else:
        return {
            "status_code": 500
        }


@app.post("/importStudent", status_code=200)
def importStudent(nid: str, token: str, projectUUID: str, file_: UploadFile):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    with open("./temp/tempStudent.temp", "wb+") as f:
        copyfileobj(file_.file, f)

    df = read_excel("./temp/tempStudent.temp")

    for i in df["NID"]:
        if not i.startswith("D"):
            continue
        params = {
            "nid": i,
            "projectUUID": projectUUID,
        }
        success = SQLHandler().newStudent(params)
        if not success:
            return {
                "status_code": 500
            }

    return {
        "status_code": 200
    }

# teacher


@app.get("/getTeacherData/{nid}/{token}/{projectUUID}", status_code=200)
def getTeacherData(nid: str, token: str, projectUUID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    teacherData = SQLHandler().getTeacherData(projectUUID)
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


@app.get("/getTeacherList/{nid}/{token}/{projectUUID}", status_code=200)
def getTeacherList(nid: str, token: str, projectUUID):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    teacherList = SQLHandler().getTeacherList()
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
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")
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
    success = SQLHandler().newTeacher(params)
    if success:
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 500
        }


@app.delete("/deleteTeacher/{nid}/{token}/{teacherNID}/{projectUUID}", status_code=200)
def deleteTeacher(nid: str, token: str, teacherNID: str, projectUUID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")
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
    if SQLHandler().deleteTeacher(params):
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 500
        }


@app.get("/getTeacherInfo/{nid}/{token}/{teacherNID}", status_code=200)
def getTeacherInfo(nid: str, token: str, teacherNID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    if not AUTHENTICATION().SQLInjectionCheck(prompt=teacherNID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    teacherInfo = SQLHandler().getTeacherInfo(teacherNID)
    if teacherInfo:
        return {
            "name": teacherInfo[0],
            "permission": teacherInfo[1]
        }
    else:
        return {
            "status_code": 500
        }


@app.post("/importTeacher", status_code=200)
def importTeacher(nid: str, token: str, projectUUID: str, file_: UploadFile):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    with open("./temp/tempTeacher.temp", "wb+") as f:
        copyfileobj(file_.file, f)

    df = read_excel("./temp/tempTeacher.temp")

    for i in df["NID"]:
        if not i.startswith("T"):
            continue
        params = {
            "nid": i,
            "projectUUID": projectUUID,
        }
        success = SQLHandler().newTeacher(params)
        if not success:
            return {
                "status_code": 500
            }

    return {
        "status_code": 200
    }

# announcement


@app.get("/getAnnouncementData/{nid}/{token}/{projectUUID}", status_code=200)
def getAnnouncementData(nid: str, token: str, projectUUID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    announcementData = SQLHandler().getAnnouncementData(projectUUID)
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
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")
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
    success = SQLHandler().createAnnouncement(params)
    if success:
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 500
        }


@app.delete("/deleteAnnouncement/{nid}/{token}/{projectUUID}/{announcementUUID}", status_code=200)
def deleteAnnouncement(nid: str, token: str, projectUUID: str, announcementUUID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    for i in [projectUUID, announcementUUID]:
        if not AUTHENTICATION().SQLInjectionCheck(prompt=i):
            return {
                "SQLInjectionCheck": False,
                "status_code": 400
            }

    params = {
        "projectUUID": projectUUID,
        "announcementUUID": announcementUUID
    }
    if SQLHandler().deleteAnnouncement(params):
        return {
            "status_code": 200
        }
    return {
        "status_code": 500
    }


@app.get("/getAnnouncementInfo/{nid}/{token}/{announcementUUID}", status_code=200)
def getAnnouncementInfo(nid: str, token: str, announcementUUID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    if not AUTHENTICATION().SQLInjectionCheck(prompt=announcementUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    announcementInfo = SQLHandler().getAnnouncementInfo(announcementUUID)

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


@app.get("/getGroupData/{nid}/{token}/{projectUUID}", status_code=200)
def getGroupData(nid: str, token: str, projectUUID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    groupData = SQLHandler().getGroupData(projectUUID)
    if groupData or groupData == []:
        return groupData
    else:
        return {
            "status_code": 500
        }


@app.post("/newGroup", status_code=200)
def newGroup(nid: str, token: str, projectUUID: str, member: str, group_name: str, GID):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

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
    if SQLHandler().newGroup(params):
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 500
        }


@app.get("/getGroupToken/{nid}/{token}", status_code=200)
def getGroupToken(nid: str, token: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    return {
        "GID": str(uuid.uuid4())
    }


@app.get("/getGroupTeacherData/{nid}/{token}/{projectUUID}", status_code=200)
def getGroupTeacherData(nid: str, token: str, projectUUID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    teacher_data = SQLHandler().getGroupTeacherData(projectUUID)
    teacher_list = []
    for i in teacher_data:
        teacher_list.append({
            "nid": i[0],
            "name": i[1],
        })

    if teacher_list:
        return teacher_list
    else:
        return []


@app.get("/getGroupStudentData/{nid}/{token}/{projectUUID}", status_code=200)
def getGroupStudentData(nid: str, token: str, projectUUID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    if not AUTHENTICATION().SQLInjectionCheck(prompt=projectUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    student_data = SQLHandler().getGroupStudentData(projectUUID)
    student_list = []
    for i in student_data:
        student_list.append({
            "nid": i[0],
            "name": i[1],
        })

    if student_list:
        return student_list
    else:
        return []


@app.get("/getGroupInfo/{nid}/{token}/{groupUUID}", status_code=200)
def getGroupInfo(nid: str, token: str, groupUUID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    if not AUTHENTICATION().SQLInjectionCheck(prompt=groupUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    groupInfo = SQLHandler().getGroupInfo(groupUUID)

    for i in groupInfo:
        if groupInfo[i] == []:
            groupInfo[i] = "None"
        if type(groupInfo[i]) == list:
            groupInfo[i] = ", ".join(groupInfo[i])

    return groupInfo


@app.delete("/deleteGroup/{nid}/{token}/{GID}/{projectUUID}", status_code=200)
def deleteGroup(nid: str, token: str, groupUUID: str, projectUUID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    if not AUTHENTICATION().SQLInjectionCheck(prompt=groupUUID):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }
    params = {
        "groupUUID": groupUUID,
        "projectUUID": projectUUID,
    }

    SQLHandler().deleteGroup(params)

# assignment


@app.get("/getAssignment/{nid}/{token}/{projectUUID}", status_code=200)
def getAssignment(nid: str, token: str, projectUUID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    for i in [projectUUID]:
        if not AUTHENTICATION().SQLInjectionCheck(prompt=i):
            return {
                "SQLInjectionCheck": False,
                "status_code": 400
            }
    params = {
        "nid": nid,
        "projectUUID": projectUUID
    }
    assignment_data = SQLHandler().getAssignment(params)
    if assignment_data or assignment_data == []:
        return assignment_data
    else:
        return {
            "status_code": 500
        }


@app.post("/downloadAssignment", status_code=200)
def downloadAssignment(
        nid: str,
        token: str,
        projectUUID: str,
        taskUUID: str,
        fileID: str):

    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    for i in [taskUUID, fileID]:
        if not AUTHENTICATION().SQLInjectionCheck(prompt=i):
            return {
                "SQLInjectionCheck": False,
                "status_code": 400
            }
    params = {
        "taskUUID": taskUUID,
        "fileID": fileID
    }
    file_name = SQLHandler().downloadAssignment(params)

    file_path = f"assignment/{projectUUID}/{params['taskUUID']}/{params['fileID']}/{file_name}"
    return FileResponse(path=file_path)


@app.post("/uploadAssignment", status_code=200)
def uploadAssignment(
        nid: str,
        token: str,
        projectUUID: str,
        taskUUID: str,
        filename: str,
        file_: UploadFile):

    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    for i in [projectUUID, taskUUID, filename]:
        if not AUTHENTICATION().SQLInjectionCheck(prompt=i):
            return {
                "SQLInjectionCheck": False,
                "status_code": 400
            }

    file_id = str(uuid.uuid4())
    file_path = f"./assignment/{projectUUID}/{taskUUID}/{file_id}/{filename}"
    path = f"./assignment/{projectUUID}/{taskUUID}/{file_id}/"

    os.makedirs(path)
    with open(file_path, "wb+") as f:
        copyfileobj(file_.file, f)

    params = {
        "TASK_ID": taskUUID,
        "FILE_ID": file_id,
        "FILE_NAME": filename,
        "AUTHOR": nid,
        "DATE": datetime.date.today(),
        "projectUUID": projectUUID,
    }
    if SQLHandler().uploadAssignment(params):
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 500
        }


@app.delete("/deleteAssignment/{nid}/{token}/{projectUUID}/{assignmentUUID}", status_code=200)
def deleteAssignment(nid: str, token: str, assignmentUUID: str, projectUUID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    for i in [projectUUID]:
        if not AUTHENTICATION().SQLInjectionCheck(prompt=i):
            return {
                "SQLInjectionCheck": False,
                "status_code": 400
            }

    params = {
        "project_id": projectUUID,
        "task_id": assignmentUUID,
    }

    if SQLHandler().deleteAssignment(params):
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 500
        }


@app.delete("/deleteAssignmentItem/{nid}/{token}/{taskUUID}/{fileUUID}/{author}", status_code=200)
def deleteAssignmentItem(nid: str, token: str, taskID: str, fileID: str, author: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    for i in [taskID, fileID, author]:
        if not AUTHENTICATION().SQLInjectionCheck(prompt=i):
            return {
                "SQLInjectionCheck": False,
                "status_code": 400
            }

    params = {
        "taskID": taskID,
        "fileID": fileID,
        "author": author
    }

    if SQLHandler().deleteAssignmentItem(params):
        return {
            "status_code": 200,
        }
    else:
        return {
            "status_code": 500
        }


@app.post("/markAssignmentScore", status_code=200)
def markAssignmentScore(nid: str, token: str, projectUUID: str, taskUUID: str, marks: int):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    for i in [projectUUID, taskUUID, marks]:
        if not AUTHENTICATION().SQLInjectionCheck(prompt=i):
            return {
                "SQLInjectionCheck": False,
                "status_code": 400
            }

    params = {
        "projectUUID": projectUUID,
        "taskUUID": taskUUID,
        "marks": marks
    }
    if SQLHandler().markAssignmentScore(params):
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 500
        }


@app.post("/newAssignment", status_code=200)
def newAssignment(
        nid: str,
        token: str,
        projectUUID: str,
        gid: str,
        name: str,
        weight: int,
        date: str):

    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    for i in [projectUUID, gid, name, weight, date]:
        if not AUTHENTICATION().SQLInjectionCheck(prompt=i):
            return {
                "SQLInjectionCheck": False,
                "status_code": 400
            }

    params = {
        "task_id": str(uuid.uuid4()),
        "projectUUID": projectUUID,
        "name": name,
        "status": "未完成",
        "submission_date": date,
        "gid": gid,
        "uploader": nid,
        "weight": weight,
        "mark": 0
    }

    SQLHandler().newAssignment(params)


@app.get("/getAssignmentInfo/{nid}/{token}/{projectUUID}/{assignmentUUID}", status_code=200)
def getAssignmentInfo(nid: str, token: str, assignmentUUID: str, projectUUID: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    for i in [projectUUID, assignmentUUID]:
        if not AUTHENTICATION().SQLInjectionCheck(prompt=i):
            return {
                "SQLInjectionCheck": False,
                "status_code": 400
            }

    params = {
        "task_id": assignmentUUID,
        "project_id": projectUUID,
    }

    info = SQLHandler().getAssignmentInfo(params)
    if info and info != ():
        return info
    else:
        return {
            "status_code": 500
        }

# profile


@app.post("/changePassword", status_code=200)
async def changePassword(nid: str, token: str, oldPassword: str, newPassword: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    for i in [oldPassword, newPassword]:
        if not AUTHENTICATION().SQLInjectionCheck(prompt=i):
            return {
                "SQLInjectionCheck": False,
                "status_code": 400
            }

    if access.change_password(nid, oldPassword, newPassword):
        return {
            "status_code": 200
        }
    else:
        return {
            "status_code": 400
        }


@app.get("/getIconImages/{nid}/{token}", status_code=200)
async def getIconImages(nid: str, token: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")
    icon_file_name = SQLHandler().getIconImage(nid)
    return FileResponse(f"./icon/{icon_file_name}")


@app.post("/changeIcon", status_code=200)
async def changeIcon(nid: str, token: str, file_: UploadFile, filename: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    if not AUTHENTICATION().SQLInjectionCheck(prompt=filename):
        return {
            "SQLInjectionCheck": False,
            "status_code": 400
        }

    file_extension = filename.split(".")[-1]
    file_name = str(uuid.uuid4())

    path = f"./icon/{nid}/"
    file_path = f"./icon/{nid}/{file_name}.{file_extension}"

    params = {
        "filename": f"{file_name}.{file_extension}",
        "nid": nid,
    }
    if not os.path.exists(path):
        os.makedirs(path)

    with open(file_path, "wb+") as f:
        copyfileobj(file_.file, f)

    SQLHandler().changeIcon(params)

    return {
        "status_code": 200,
    }


# dashboard

@app.get("/getDeadlineProject/{nid}/{token}", status_code=200)
def getDeadlineProject(nid: str, token: str):
    access = AUTHENTICATION()
    func_name = stack()[0][3]
    if not access.permission_check(nid, func_name):
        return HTTPException(403, "Access denied")

    token_validation = access.verify_jwt_token(nid, token)
    if not token_validation:
        return HTTPException(status_code=403, detail="Token invalid")

    data = SQLHandler().getDeadlineProject(nid)
    if data:
        return {
            "status_code": 200,
            "data": data
        }
    else:
        return {
            "status_code": 200,
            "data": None
        }


if __name__ == "__main__":
    # development only
    # uvicorn main:app --reload
    app.run(debug=DEBUG)
