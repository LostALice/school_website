# 逢甲大學專題管理系統

[![wakatime](https://wakatime.com/badge/user/09ce4786-a8a5-43eb-8a65-50ad8684b5da/project/2f818c62-a844-4b03-9072-4e4658b25ced.svg)](https://wakatime.com/badge/user/09ce4786-a8a5-43eb-8a65-50ad8684b5da/project/2f818c62-a844-4b03-9072-4e4658b25ced)

# Docker env

### The following environment variables edit the default setting of [setting.json](#settingjson) file

| Environment variables | Default setting                | Description                                              |
| --------------------- | ------------------------------ | -------------------------------------------------------- |
| DATABASE              | PMS                            | mysql schema name                                        |
| HOST                  | localhost                      | mysql database host address should be internal docker ip |
| USER                  | root                           | mysql username                                           |
| PASSWORD              | Abc!@#$%^&\*()                 | mysql password                                           |
| JWT_SECRET            | May be this is a secret string | Json Web Token secret                                    |
| JWT_TOKEN_EXPIRE_TIME | 3600                           | Json Web Token expiration time                           |

# setting.json

`The default setting of setting.json file`

```
{
    "debug": false,
    "permissions": {
        "login": 0,
        "JWTValidation": 0,
        "checkPermission": 0,
        "getPermissionLevel": 0,
        "TimeoutStatus": 0,
        "changePassword": 0,
        "getIconImages": 0,
        "changeIcon": 0,
        "getDeadlineProject": 0,
        "getSubject": 1,
        "getProject": 1,
        "getProjectInfo": 1,
        "getStudentData": 1,
        "getStudentList": 1,
        "getStudentInfo": 1,
        "getTeacherData": 1,
        "getTeacherList": 1,
        "getTeacherInfo": 1,
        "getAnnouncementData": 1,
        "getAnnouncementInfo": 1,
        "getGroupData": 1,
        "getGroupTeacherData": 1,
        "getGroupStudentData": 1,
        "getGroupInfo": 1,
        "getAssignment": 1,
        "downloadAssignment": 1,
        "uploadAssignment": 1,
        "deleteAssignment": 1,
        "deleteAssignmentItem": 1,
        "getAssignmentInfo": 1,
        "createSubject": 2,
        "deleteSubject": 2,
        "createProject": 2,
        "deleteProject": 2,
        "newStudent": 2,
        "deleteStudent": 2,
        "importStudent": 2,
        "newTeacher": 2,
        "deleteTeacher": 2,
        "importTeacher": 2,
        "createAnnouncement": 2,
        "deleteAnnouncement": 2,
        "newGroup": 2,
        "getGroupToken": 2,
        "deleteGroup": 2,
        "markAssignmentScore": 2,
        "newAssignment": 2,
        "getLog": 3,
        "forceChangePassword": 3
    },
    "database": {
        "DATABASE": "PMS",
        "HOST": "localhost",
        "USER": "root",
        "PASSWORD": "Abc!@#$%^&*()"
    },
    "JWT": {
        "JWT_TOKEN_EXPIRE_TIME": 3600,
        "JWT_SECRET": "May be this is a secret string",
        "JWT_ALGORITHM": "HS256"
    }
}
```
