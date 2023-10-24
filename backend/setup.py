# Code by AkinoAlice@Tyrant_Rex

import mysql.connector as connector

import json
import os


class SettingSetupHandler(object):
    def __init__(self):
        try:
            assert os.path.exists("./setting.json")
        except AssertionError:
            self.file_setup()

    def file_setup(self):
        with open("./setting.json", "w+") as f:
            f.write(json.dumps({
                "debug": False,
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
                    "DATABASE": os.getenv("DATABASE") if os.getenv("DATABASE") else "PMS",
                    "HOST": os.getenv("HOST") if os.getenv("HOST") else "localhost",
                    "USER": os.getenv("USER") if os.getenv("USER") else "root",
                    "PASSWORD": os.getenv("PASSWORD") if os.getenv("PASSWORD") else "Abc!@#$%^&*()"
                },
                "JWT": {
                    "JWT_TOKEN_EXPIRE_TIME": os.getenv("JWT_TOKEN_EXPIRE_TIME") if os.getenv("JWT_TOKEN_EXPIRE_TIME") else 3600,
                    "JWT_SECRET": os.getenv("JWT_SECRET") if os.getenv("JWT_SECRET") else "May be this is a secret string",
                    "JWT_ALGORITHM": "HS256"
                }
            }))


class SQLSetupHandler(object):
    def __init__(self):
        try:
            assert os.path.exists("./setting.json")
        except AssertionError:
            SettingSetupHandler().file_setup()

        with open("./setting.json", "r") as f:
            json_file = json.load(f)
            self.database_setting = json_file["database"]

        self.DATABASE = self.database_setting["DATABASE"]
        self.HOST = self.database_setting["HOST"]
        self.USER = self.database_setting["USER"]
        self.PASSWORD = self.database_setting["PASSWORD"]

        try:
            self.conn = connector.connect(
                host=self.HOST,
                user=self.USER,
                password=self.PASSWORD,
            )
        except connector.errors.ProgrammingError:
            print(Exception, flush=True)
            raise Exception("Wrong password, please edit docker-compose.yaml file or setting.json")

        self.conn = connector.connect(
            host=self.HOST,
            user=self.USER,
            password=self.PASSWORD,
        )
        self.curser = self.conn.cursor()

        try:
            self.conn.connect(
                database=self.DATABASE
            )
        except connector.errors.ProgrammingError:
            self.conn = connector.connect(
                host=self.HOST,
                user=self.USER,
                password=self.PASSWORD,
            )
            self.curser = self.conn.cursor()
            sql = f"CREATE DATABASE {self.DATABASE}"
            self.curser.execute(sql)
            self.conn.connect(
                database=self.DATABASE
            )

        self.MYSQL_setup()

    def MYSQL_setup(self):
        self.curser.execute("""
            CREATE TABLE `announcements` (
                `PROJECT_ID` varchar(255) NOT NULL,
                `ANNOUNCEMENTS_ID` varchar(255) NOT NULL,
                `AUTHOR` varchar(45) NOT NULL,
                `TITLE` varchar(45) NOT NULL,
                `ANNOUNCEMENTS` longtext,
                `LAST_EDIT` date NOT NULL,
                `ENABLE` tinyint NOT NULL DEFAULT '1',
                PRIMARY KEY (`ANNOUNCEMENTS_ID`)
            )
            ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"""
        )
        self.conn.commit()

        self.curser.execute("""
            CREATE TABLE `assignment` (
                `TASK_ID` varchar(255) NOT NULL,
                `PROJECT_ID` varchar(255) NOT NULL,
                `NAME` varchar(45) NOT NULL,
                `STATUS` varchar(45) NOT NULL,
                `SUBMISSION_DATE` datetime(4) DEFAULT NULL,
                `GID` varchar(255) NOT NULL,
                `UPLOADER` varchar(255) DEFAULT NULL,
                `WEIGHT` int NOT NULL,
                `MARK` int NOT NULL,
                `ENABLE` tinyint NOT NULL DEFAULT '1',
                PRIMARY KEY (`TASK_ID`,`PROJECT_ID`)
            )
            ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"""
        )
        self.conn.commit()

        self.curser.execute("""
            CREATE TABLE `file` (
                `TASK_ID` varchar(255) NOT NULL,
                `FILE_ID` varchar(255) NOT NULL,
                `FILE_NAME` varchar(255) NOT NULL,
                `AUTHOR` varchar(255) NOT NULL,
                `DATE` date NOT NULL,
                `ENABLE` tinyint DEFAULT '1',
                PRIMARY KEY (`TASK_ID`,`FILE_ID`)
            )
            ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"""
        )
        self.conn.commit()

        self.curser.execute("""
            CREATE TABLE `group` (
                `PROJECT_ID` varchar(255) NOT NULL,
                `GID` varchar(255) NOT NULL,
                `NID` varchar(255) NOT NULL,
                `NAME` varchar(255) NOT NULL,
                `ENABLE` tinyint NOT NULL DEFAULT '1',
                PRIMARY KEY (`PROJECT_ID`,`GID`,`NID`)
            )
            ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"""
        )
        self.conn.commit()

        self.curser.execute("""
            CREATE TABLE `log` (
                `DATE` datetime(4) NOT NULL DEFAULT CURRENT_TIMESTAMP(4),
                `EVENT` varchar(45) NOT NULL,
                `ARGs` longtext NOT NULL,
                PRIMARY KEY (`DATE`)
            )
            ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"""
        )
        self.conn.commit()

        self.curser.execute("""
            CREATE TABLE `login` (
                `NID` varchar(16) NOT NULL,
                `USERNAME` varchar(255) NOT NULL,
                `PASSWORD` varchar(255) NOT NULL,
                `EMAIL` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'example@example.com',
                `LAST_LOGIN` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
                `ICON` varchar(255) NOT NULL DEFAULT 'default.png',
                `TOKEN` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                `PERMISSION` int NOT NULL DEFAULT '1',
                PRIMARY KEY (`NID`)
            )
            ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"""
        )
        self.conn.commit()

        self.curser.execute("""
            CREATE TABLE `member` (
                `PROJECT_ID` varchar(255) NOT NULL,
                `NID` varchar(255) NOT NULL,
                `ENABLE` tinyint NOT NULL DEFAULT '1',
                PRIMARY KEY (`PROJECT_ID`,`NID`)
            )
            ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"""
        )
        self.conn.commit()

        self.curser.execute("""
            CREATE TABLE `project` (
                `SUBJECT_ID` varchar(255) NOT NULL,
                `PROJECT_ID` varchar(255) NOT NULL,
                `NAME` varchar(255) NOT NULL DEFAULT '新項目',
                `ENABLE` tinyint NOT NULL DEFAULT '1',
                PRIMARY KEY (`SUBJECT_ID`,`PROJECT_ID`)
            )
            ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"""
        )
        self.conn.commit()

        self.curser.execute("""
            CREATE TABLE `student` (
                `PROJECT_ID` varchar(255) NOT NULL,
                `NID` varchar(255) NOT NULL,
                `ENABLE` tinyint NOT NULL DEFAULT '1',
                PRIMARY KEY (`PROJECT_ID`,`NID`)
            )
            ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"""
        )
        self.conn.commit()

        self.curser.execute("""
            CREATE TABLE `subject` (
                `SUBJECT_ID` varchar(255) NOT NULL,
                `NAME` varchar(255) NOT NULL,
                `YEAR` smallint NOT NULL,
                `START_DATE` date DEFAULT NULL,
                `END_DATE` date DEFAULT NULL,
                `SETTLEMENT_START_DATE` date DEFAULT NULL,
                `SETTLEMENT_END_DATE` date DEFAULT NULL,
                `ENABLE` tinyint DEFAULT '1',
                PRIMARY KEY (`SUBJECT_ID`)
            )
            ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"""
        )
        self.conn.commit()

        self.curser.execute("""
            CREATE TABLE `teacher` (
                `PROJECT_ID` varchar(255) NOT NULL,
                `NID` varchar(45) NOT NULL,
                `ENABLE` tinyint NOT NULL DEFAULT '1',
                PRIMARY KEY (`PROJECT_ID`,`NID`)
            )
            ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"""
        )
        self.conn.commit()
