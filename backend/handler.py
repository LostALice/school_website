# Code by AkinoAlice@Tyrant_Rex

from setup import SQLSetupHandler, SettingSetupHandler

import mysql.connector as connector
import json

class SQLHandler:
    def __init__(self):
        self.sql_init()

    def sql_init(self):
        """
            Env variables:
                JWT_TOKEN_EXPIRE_TIME # in seconds
                JWT_SECRET  # any string
                JWT_ALGORITHM # HMAC, RSA, ECDSA, etc
        """
        try:
            with open("setting.json", "r") as f:
                json_file = json.load(f)
                self.database_setting = json_file["database"]
                self.JWT_setting = json_file["JWT"]
        except Exception as error:
            SettingSetupHandler()
            raise error

        self.DATABASE = self.database_setting["DATABASE"]
        self.HOST = self.database_setting["HOST"]
        self.USER = self.database_setting["USER"]
        self.PASSWORD = self.database_setting["PASSWORD"]

        self.JWT_TOKEN_EXPIRE_TIME = self.JWT_setting["JWT_TOKEN_EXPIRE_TIME"]
        self.JWT_SECRET = self.JWT_setting["JWT_SECRET"]
        self.JWT_ALGORITHM = self.JWT_setting["JWT_ALGORITHM"]

        try:
            self.conn = connector.connect(
                database=self.DATABASE,
                host=self.HOST,
                user=self.USER,
                password=self.PASSWORD,
            )
        except Exception as e:
            print(e, flush=True)
            SQLSetupHandler()

        self.conn = connector.connect(
            database=self.DATABASE,
            host=self.HOST,
            user=self.USER,
            password=self.PASSWORD,
        )
        self.cursor = self.conn.cursor()

    # close the connection after query executed
    def sql_term(func) -> any:
        def warp(self, *data):
            _ = func(self, *data)
            LOGGER().log(func.__name__, data)
            self.conn.close()
            return _
        return warp

    # subject
    @sql_term
    def getSubjectData(self, nid: str = "") -> dict:
        self.cursor.execute("""
            SELECT
                subject.SUBJECT_ID,
                subject.NAME,
                subject.YEAR,
                subject.START_DATE,
                subject.END_DATE,
                subject.SETTLEMENT_START_DATE,
                subject.SETTLEMENT_END_DATE
            FROM
                subject
            INNER JOIN
                project ON subject.SUBJECT_ID = project.SUBJECT_ID
            INNER JOIN
                member ON project.PROJECT_ID = member.PROJECT_ID
            WHERE
                member.NID = %s and subject.ENABLE = 1
            GROUP BY subject.SUBJECT_ID;""", (nid,))
        data = self.cursor.fetchall()
        return data

    @sql_term
    def createSubjectData(self, params: dict) -> bool:
        # create subject
        self.cursor.execute("""
            INSERT INTO subject (
                subject.SUBJECT_ID,
                subject.NAME,
                subject.YEAR,
                subject.START_DATE,
                subject.END_DATE,
                subject.SETTLEMENT_START_DATE,
                subject.SETTLEMENT_END_DATE
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s
            );""", (
            params["subjectUUID"],
            params["subjectName"],
            params["year"],
            params["startDate"],
            params["endDate"],
            params["settlementStartDate"],
            params["settlementEndDate"]
        )
        )

        # bind project and student or teacher
        self.cursor.execute("""
            INSERT INTO member (
                member.PROJECT_ID,
                member.NID
            )
            VALUES (
                %s, %s
            );""", (
            params["projectUUID"], params["nid"])
        )

        # bind subject and project
        self.cursor.execute("""
            INSERT INTO project (
                project.SUBJECT_ID,
                project.PROJECT_ID
            )
            VALUES (
                %s, %s
            );""", (
            params["subjectUUID"],
            params["projectUUID"]
        )
        )
        self.conn.commit()
        return True

    @sql_term
    def deleteSubjectData(self, subjectUUID: str = "") -> bool:
        self.cursor.execute("""
            UPDATE subject
            SET subject.ENABLE = 0
            WHERE subject.SUBJECT_ID = %s ;
        """, (subjectUUID,))
        self.conn.commit()
        self.cursor.execute("""
            UPDATE project
            SET project.ENABLE = 0
            WHERE project.SUBJECT_ID = %s;;
        """, (subjectUUID,))
        self.conn.commit()
        return True

    # project
    @sql_term
    def getProjectData(self, projectData: str = "") -> dict:
        data = {
            "name": [],
            "announcements": [],
            "student": [],
            "teacher": [],
            "group": [],
            "assignment": [],
            "projectID": [],
        }

        # name
        self.cursor.execute("""
            SELECT project.PROJECT_ID as projectID
            FROM
                project
            INNER JOIN
                member on project.PROJECT_ID = member.PROJECT_ID
            WHERE
	            project.SUBJECT_ID = %s AND member.NID = %s AND project.ENABLE = 1; """,
                            (projectData["subjectUUID"], projectData["NID"])
                            )
        projectList = self.cursor.fetchall()
        data["projectID"] = projectList

        for i in projectList:
            # name
            self.cursor.execute("""
                SELECT project.NAME as name
                FROM
                    project
                INNER JOIN
                    member on project.PROJECT_ID = member.PROJECT_ID
                WHERE
                    project.PROJECT_ID = %s AND member.NID = %s AND project.ENABLE = 1""",
                                (i[0], projectData["NID"])
                                )
            data["name"].append(self.cursor.fetchall()[0])

            # announcements
            self.cursor.execute("""
                SELECT count(announcements.ANNOUNCEMENTS_ID) as announcements
                FROM
                    project
                INNER JOIN
                    member on project.PROJECT_ID = member.PROJECT_ID
                INNER JOIN
                    announcements on project.PROJECT_ID = announcements.PROJECT_ID
                WHERE
                    project.PROJECT_ID = %s AND member.NID = %s AND announcements.ENABLE = 1""",
                                (i[0], projectData["NID"])
                                )
            data["announcements"].append(self.cursor.fetchall()[0])

            # student
            self.cursor.execute("""
                SELECT count(student.NID) as student
                FROM
                    project
                INNER JOIN
                    member on project.PROJECT_ID = member.PROJECT_ID
                INNER JOIN
                    student on project.PROJECT_ID = student.PROJECT_ID
                WHERE
                    project.PROJECT_ID = %s AND member.NID = %s AND student.ENABLE = 1""",
                                (i[0], projectData["NID"])
                                )
            data["student"].append(self.cursor.fetchall()[0])

            # teacher
            self.cursor.execute("""
                SELECT count(teacher.NID) as teacher
                FROM
                    project
                INNER JOIN
                    member on project.PROJECT_ID = member.PROJECT_ID
                INNER JOIN
                    teacher on project.PROJECT_ID = teacher.PROJECT_ID
                WHERE
                    project.PROJECT_ID = %s AND member.NID = %s AND teacher.ENABLE = 1""",
                                (i[0], projectData["NID"])
                                )
            data["teacher"].append(self.cursor.fetchall()[0])

            # group
            self.cursor.execute("""
                SELECT
                    COUNT(gp.GID) AS gp
                FROM
                    `group` AS gp
                LEFT JOIN
                    project
                    ON project.PROJECT_ID = gp.PROJECT_ID
                Where
                    gp.NID = %s
                    AND project.PROJECT_ID = %s
                    AND project.ENABLE = 1
                    AND gp.ENABLE = 1;""",
                                (projectData["NID"], i[0]))
            data["group"].append(self.cursor.fetchall()[0])

            # assignment
            self.cursor.execute("""
                SELECT
                    COUNT(assignment.TASK_ID) AS task
                FROM
                    assignment
                LEFT JOIN
                    `group` AS gp
                    ON gp.GID = assignment.GID
                Where
                    gp.NID = %s
                    AND gp.PROJECT_ID = %s
                    AND assignment.ENABLE = 1
                    AND gp.ENABLE = 1;""",
                                (projectData["NID"], i[0]))
            data["assignment"].append(self.cursor.fetchall()[0])

        return data

    @sql_term
    def createProjectData(self, params: dict = {}) -> bool:
        # bind subject and project
        self.cursor.execute("""
            INSERT INTO project (
                project.SUBJECT_ID,
                project.PROJECT_ID,
                project.NAME
            )
            VALUES (
                %s, %s, %s
            );""", (
            params["subjectUUID"],
            params["projectUUID"],
            params["projectName"]
        )
        )
        self.conn.commit()

        self.cursor.execute("""
            INSERT INTO member (
                member.PROJECT_ID,
                member.NID
            )
            VALUES (
                %s, %s
            );""", (
            params["projectUUID"],
            params["nid"]
        )
        )
        self.conn.commit()

        return True

    @sql_term
    def deleteProjectData(self, projectUUID: str = "") -> bool:
        self.cursor.execute("""
            UPDATE project
            SET project.ENABLE = 0
            WHERE project.PROJECT_ID = %s ;
        """, (projectUUID,))

        self.cursor.execute("""
            UPDATE announcements
            SET announcements.ENABLE = 0
            WHERE announcements.PROJECT_ID = %s ;
        """, (projectUUID,))

        self.cursor.execute("""
            UPDATE assignment
            SET assignment.ENABLE = 0
            WHERE assignment.PROJECT_ID = %s ;
        """, (projectUUID,))

        self.cursor.execute("""
            UPDATE `group`
            SET `group`.ENABLE = 0
            WHERE `group`.PROJECT_ID = %s ;
        """, (projectUUID,))

        self.cursor.execute("""
            UPDATE student
            SET student.ENABLE = 0
            WHERE student.PROJECT_ID = %s ;
        """, (projectUUID,))

        self.cursor.execute("""
            UPDATE teacher
            SET teacher.ENABLE = 0
            WHERE teacher.PROJECT_ID = %s ;
        """, (projectUUID,))

        self.conn.commit()
        return True

    @sql_term
    def getProjectInfo(self, projectUUID: str = "") -> dict:
        self.cursor.execute("""
             SELECT
	            subject.SUBJECT_ID, subject.NAME, subject.YEAR, subject.START_DATE, subject.END_DATE, subject.SETTLEMENT_START_DATE, subject.SETTLEMENT_END_DATE
            FROM
                subject
            INNER JOIN
                project on project.SUBJECT_ID = subject.SUBJECT_ID
            WHERE
                subject.SUBJECT_ID = %s and subject.ENABLE = 1
            GROUP BY subject.SUBJECT_ID;""", (projectUUID,))
        data = self.cursor.fetchall()[0]
        return data

    # announcement
    @sql_term
    def getAnnouncementData(self, projectUUID: str = "") -> dict:
        self.cursor.execute("""
            SELECT
                announcements.ANNOUNCEMENTS_ID, announcements.AUTHOR, announcements.TITLE, announcements.LAST_EDIT
            FROM
                announcements
            JOIN
                member ON member.PROJECT_ID = announcements.PROJECT_ID
            WHERE
                member.PROJECT_ID = %s AND announcements.ENABLE = 1""", (
            projectUUID,
        ))

        announcementData = self.cursor.fetchall()
        return announcementData

    @sql_term
    def createAnnouncement(self, params: dict = {}) -> bool:
        a = self.cursor.execute("""
            INSERT INTO announcements (
                announcements.PROJECT_ID,
                announcements.ANNOUNCEMENTS_ID,
                announcements.AUTHOR,
                announcements.TITLE,
                announcements.ANNOUNCEMENTS,
                announcements.LAST_EDIT
            )
            VALUES (
                %s, %s, %s, %s, %s, %s
            )""", (
            params["PROJECT_ID"],
            params["ANNOUNCEMENTS_ID"],
            params["AUTHOR"],
            params["TITLE"],
            params["ANNOUNCEMENTS"],
            params["LAST_EDIT"]
        ))

        self.conn.commit()
        return True

    @sql_term
    def deleteAnnouncement(self, params: dict) -> bool:
        self.cursor.execute("""
            UPDATE
                announcements
            SET
                announcements.ENABLE = 0
            WHERE
                announcements.PROJECT_ID = %s
                AND announcements.ANNOUNCEMENTS_ID = %s""",
                            (params["projectUUID"], params["announcementUUID"]))
        self.conn.commit()
        return True

    @sql_term
    def getAnnouncementInfo(self, announcementUUID: str = "") -> dict:
        self.cursor.execute("""
            SELECT
                announcements.AUTHOR, announcements.TITLE,announcements. ANNOUNCEMENTS, announcements.LAST_EDIT
            FROM
                announcements
            WHERE
                announcements.ENABLE = 1 AND announcements.ANNOUNCEMENTS_ID = %s;""",
                            (announcementUUID,))

        info = self.cursor.fetchone()
        return info

    # student
    @sql_term
    def getStudentData(self, projectUUID: str = "") -> dict:
        self.cursor.execute("""
            SELECT
                student.NID, login.USERNAME
            FROM
                student
            JOIN
                login ON student.NID = login.NID
            WHERE
                student.PROJECT_ID = %s AND student.ENABLE = 1""",
                            (projectUUID,))

        studentData = self.cursor.fetchall()
        return studentData

    @sql_term
    def getStudentList(self) -> dict:
        self.cursor.execute("""
        SELECT
            login.NID, login.USERNAME
        FROM
            login
        WHERE
            login.NID LIKE "D%" """)

        studentList = self.cursor.fetchall()
        return studentList

    @sql_term
    def newStudent(self, params: dict = {}) -> bool:
        self.cursor.execute("""
            INSERT IGNORE INTO student
                (student.PROJECT_ID, student.NID)
            SELECT
                %s, %s
            WHERE EXISTS (
                SELECT 1
                FROM login
                WHERE login.NID = %s);""",
                            (params["projectUUID"], params["nid"], params["nid"]))
        self.conn.commit()
        self.cursor.execute("""
            INSERT IGNORE INTO member (
                member.PROJECT_ID,
                member.NID
            )
            VALUES (
                %s, %s
            );""",
                            (params["projectUUID"], params["nid"]))
        self.conn.commit()
        return True

    @sql_term
    def deleteStudent(self, params: dict = {}) -> bool:
        self.cursor.execute("""
            DELETE
            FROM
                student
            WHERE
                student.NID = %s AND student.PROJECT_ID = %s;""",
                            (params["nid"], params["projectUUID"]))
        self.conn.commit()
        return True

    @sql_term
    def getStudentInfo(self, nid: str = "") -> dict:
        self.cursor.execute("""
            SELECT
                login.USERNAME, login.PERMISSION
            FROM
                login
            WHERE
                login.NID = %s""", (nid,))
        info = self.cursor.fetchone()
        return info

    # teacher
    @sql_term
    def getTeacherData(self, projectUUID: str = "") -> dict:
        self.cursor.execute("""
            SELECT
                teacher.NID, login.USERNAME
            FROM
                teacher
            JOIN
                login ON teacher.NID = login.NID
            WHERE
                teacher.PROJECT_ID = %s AND teacher.ENABLE = 1""",
                            (projectUUID,))

        teacherData = self.cursor.fetchall()
        return teacherData

    @sql_term
    def getTeacherList(self) -> dict:
        self.cursor.execute("""
        SELECT
            login.NID, login.USERNAME
        FROM
            login
        WHERE
            login.NID LIKE "T%" """)

        teacherList = self.cursor.fetchall()
        return teacherList

    @sql_term
    def newTeacher(self, params: dict) -> bool:
        self.cursor.execute("""
            INSERT IGNORE INTO teacher
                (teacher.PROJECT_ID, teacher.NID)
            SELECT
                %s, %s
            WHERE EXISTS (
                SELECT 1
                FROM login
                WHERE login.NID = %s);""",
                            (params["projectUUID"], params["nid"], params["nid"]))
        self.conn.commit()
        self.cursor.execute("""
            INSERT INTO member (
                member.PROJECT_ID,
                member.NID
            )
            VALUES (
                %s, %s
            );""",
                            (params["projectUUID"], params["nid"]))
        self.conn.commit()
        return True

    @sql_term
    def deleteTeacher(self, params: dict = {}) -> bool:
        self.cursor.execute("""
            DELETE
            FROM
                teacher
            WHERE
                teacher.NID = %s AND teacher.PROJECT_ID = %s;""",
                            (params["nid"], params["projectUUID"]))
        self.conn.commit()
        return True

    @sql_term
    def getTeacherInfo(self, nid: str = "") -> dict:
        self.cursor.execute("""
            SELECT
                login.USERNAME, login.PERMISSION
            FROM
                login
            WHERE
                login.NID = %s""", (nid,))
        info = self.cursor.fetchone()
        return info

    # group
    @sql_term
    def getGroupData(self, projectUUID: str) -> list:
        self.cursor.execute("""
            SELECT
                gp.GID
            FROM
                `group` as gp
            WHERE
                gp.PROJECT_ID = %s
                AND gp.NID = "D1177531"
                AND gp.ENABLE = 1;""",
                            (projectUUID,))
        group_id = self.cursor.fetchall()
        groupData = []
        for i in group_id:
            data = {
                "groupUUID": i[0],
            }
            self.cursor.execute("""
            SELECT
                COUNT(gp.NID)
            FROM
                `group` as gp
            WHERE
                gp.GID = %s AND gp.ENABLE = 1 AND gp.NID LIKE "T%" """,
                                (i[0],))
            data["teacher"] = self.cursor.fetchall()[0][0]

            self.cursor.execute("""
            SELECT
                COUNT(gp.NID)
            FROM
                `group` as gp
            WHERE
                gp.GID = %s AND gp.ENABLE = 1 AND gp.NID LIKE "D%" """,
                                (i[0],))
            data["student"] = self.cursor.fetchall()[0][0]

            self.cursor.execute("""
            SELECT
                gp.NAME
            FROM
                `group` as gp
            WHERE
                gp.GID = %s AND gp.ENABLE = 1 """,
                                (i[0],))
            data["name"] = self.cursor.fetchall()[0][0]

            groupData.append(data)
        return groupData

    @sql_term
    def newGroup(self, params: dict) -> bool:
        self.cursor.execute("""
            INSERT IGNORE INTO
                `group` (PROJECT_ID, GID, NID, NAME)
            VALUES
                (%s, %s, %s, %s)""",
                            (params["projectUUID"], params["GID"], params["nid"], params["name"]))
        self.conn.commit()
        return True

    @sql_term
    def getGroupStudentData(self, projectUUID: str) -> dict:
        self.cursor.execute("""
            SELECT
                student.NID, login.USERNAME
            FROM
                student
            JOIN
                login
            ON
                login.NID = student.NID 
            WHERE
                student.PROJECT_ID = %s AND student.ENABLE = 1 """, (projectUUID,))
        student_list = self.cursor.fetchall()
        return student_list

    @sql_term
    def getGroupTeacherData(self, projectUUID: str) -> dict:
        self.cursor.execute("""
            SELECT
                teacher.NID, login.USERNAME
            FROM
                teacher
            JOIN
                login
            ON
                login.NID = teacher.NID
            WHERE
                teacher.PROJECT_ID = %s AND teacher.ENABLE = 1 """, (projectUUID,))
        teacher_list = self.cursor.fetchall()
        return teacher_list

    @sql_term
    def getGroupInfo(self, groupUUID: str) -> dict:
        info = {}
        self.cursor.execute("""
            SELECT
                gp.NAME
            FROM
                `group` AS gp
            WHERE
                gp.GID = %s AND gp.ENABLE = 1""", (groupUUID,))
        info["name"] = self.cursor.fetchall()[0][0]

        self.cursor.execute("""
            SELECT
                login.USERNAME
            FROM
                `group` AS gp
            JOIN
                login
            ON
                login.NID = gp.NID
            WHERE
                gp.GID = %s AND gp.ENABLE = 1 AND login.NID LIKE "D%";""",
                            (groupUUID,))
        info["student"] = [i[0] for i in self.cursor.fetchall()]

        self.cursor.execute("""
            SELECT
                COUNT(login.USERNAME)
            FROM
                `group` AS gp
            JOIN
                login
            ON
                login.NID = gp.NID
            WHERE
                gp.GID = %s AND gp.ENABLE = 1 AND login.NID LIKE "D%";""",
                            (groupUUID,))
        info["countStudent"] = self.cursor.fetchone()[0]

        self.cursor.execute("""
            SELECT
                login.USERNAME
            FROM
                `group` AS gp
            JOIN
                login
            ON
                login.NID = gp.NID
            WHERE
                gp.GID = %s AND gp.ENABLE = 1 AND login.NID LIKE "T%";""",
                            (groupUUID,))
        info["teacher"] = [i[0] for i in self.cursor.fetchall()]

        self.cursor.execute("""
            SELECT
                COUNT(login.USERNAME)
            FROM
                `group` AS gp
            JOIN
                login
            ON
                login.NID = gp.NID
            WHERE
                gp.GID = %s AND gp.ENABLE = 1 AND login.NID LIKE "T%";""",
                            (groupUUID,))
        info["countTeacher"] = self.cursor.fetchone()[0]

        return info

    @sql_term
    def deleteGroup(self, params: dict) -> bool:
        self.cursor.execute("""
            UPDATE
                `group` as gp
            SET
                gp.ENABLE = 0
            where
                gp.GID = %s and gp.PROJECT_ID = %s""",
                            (params["groupUUID"], params["projectUUID"]))
        self.conn.commit()
        return True

    @sql_term
    def getAssignment(self, params: dict) -> bool:
        self.cursor.execute("""
            SELECT gp.gid
            FROM
                `group` AS gp
            WHERE
                gp.nid = %s
                AND gp.project_id = %s
                AND gp.enable = 1""",
                            (params["nid"], params["projectUUID"]))
        group_ids = self.cursor.fetchall()
        group_ids = [i[0] for i in group_ids]

        assignment_data = []
        for group_id in group_ids:
            self.cursor.execute("""
                SELECT
                    assignment.TASK_ID,
                    gp.NAME,
                    assignment.NAME,
                    assignment.STATUS,
                    assignment.SUBMISSION_DATE,
                    assignment.UPLOADER
                FROM
                    assignment
                join
                    `group` as gp
                ON
                    assignment.GID = gp.GID
                WHERE
                    assignment.PROJECT_ID = %s
                    AND assignment.GID = %s
                    AND gp.NID = %s
                    AND assignment.enable = 1""",
                                (params["projectUUID"], group_id, params["nid"]))

            fetch = self.cursor.fetchall()
            if fetch != []:
                for i in fetch:
                    group_data = {}
                    group_data["assignmentUUID"] = i[0]
                    group_data["group"] = i[1]
                    group_data["title"] = i[2]
                    group_data["status"] = i[3]
                    group_data["date"] = "None" if i[4] == "" else i[4]
                    group_data["uploader"] = "Not " if i[5] == "" else str(
                        i[5])
                    assignment_data.append(group_data)

            return assignment_data

    @sql_term
    def deleteAssignment(self, params: dict):
        self.cursor.execute("""
            UPDATE
                assignment
            SET
                assignment.ENABLE = 0
            WHERE
                assignment.PROJECT_ID = %s
                AND assignment.TASK_ID = %s """,
                            (params["project_id"], params["task_id"]))
        self.conn.commit()
        return True

    @sql_term
    def getAssignmentInfo(self, params: dict) -> str:
        self.cursor.execute("""
            SELECT
                assignment.NAME,
                gp.NAME,
                assignment.MARK,
                assignment.WEIGHT,
                assignment.SUBMISSION_DATE
            FROM
                assignment
            JOIN
                `group` AS gp
            ON
                gp.GID = assignment.GID
            WHERE
                assignment.TASK_ID = %s
                AND assignment.PROJECT_ID = %s""",
                            (params["task_id"], params["project_id"]))

        info = self.cursor.fetchall()[0]
        info = {
            "assignment_name": info[0],
            "group_name": info[1],
            "mark": info[2],
            "weight": info[3],
            "date": info[4],
        }

        self.cursor.execute("""
            SELECT
                file.TASK_ID,
                file.FILE_ID,
                file.FILE_NAME,
                file.AUTHOR,
                file.DATE
            FROM
                file
            WHERE
                file.TASK_ID = %s
                AND file.ENABLE = 1""",
                            (params["task_id"],))

        files = self.cursor.fetchall()

        if files == []:
            return info

        assignment_file = []
        for i in files:
            assignment_file.append({
                "taskID": i[0],
                "fileID": i[1],
                "filename": i[2],
                "author": i[3],
                "date": i[4],
            })
        info["assignment_file"] = assignment_file
        return info

    @sql_term
    def downloadAssignment(self, params: dict) -> str:
        self.cursor.execute("""
            SELECT
                file.FILE_NAME
            FROM
                file
            WHERE
                file.TASK_ID = %s
                AND file.FILE_ID = %s""",
                            (params["taskUUID"], params["fileI  D"]))
        file_name = self.cursor.fetchone()[0]
        return file_name

    @sql_term
    def markAssignmentScore(self, params: dict) -> bool:
        self.cursor.execute("""
            UPDATE
                assignment
            SET
                assignment.MARK = %s
            WHERE
                assignment.TASK_ID = %s
                AND assignment.PROJECT_ID = %s """,
                            (params["marks"], params["taskUUID"], params["projectUUID"]))
        self.conn.commit()

        self.cursor.execute("""
            UPDATE
                assignment
            SET
                assignment.STATUS = "已評分"
            WHERE
                assignment.TASK_ID = %s
                AND assignment.PROJECT_ID = %s """,
                            (params["taskUUID"], params["projectUUID"]))
        self.conn.commit()
        return True

    @sql_term
    def deleteAssignmentItem(self, params: dict) -> bool:
        self.cursor.execute("""
            UPDATE
                file
            SET
                file.ENABLE = 0
            WHERE
                file.TASK_ID = %s
                AND file.FILE_ID = %s
                AND file.AUTHOR = %s """,
                            (params["taskID"], params["fileID"], params["author"]))

        self.conn.commit()
        return True

    @sql_term
    def newAssignment(self, params: dict) -> bool:
        self.cursor.execute("""
            INSERT IGNORE INTO
                assignment
                (
                    assignment.TASK_ID,
                    assignment.PROJECT_ID,
                    assignment.NAME,
                    assignment.STATUS,
                    assignment.SUBMISSION_DATE,
                    assignment.GID,
                    assignment.UPLOADER,
                    assignment.WEIGHT,
                    assignment.MARK
                )
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (
                                params["task_id"],
                                params["projectUUID"],
                                params["name"],
                                params["status"],
                                params["submission_date"],
                                params["gid"],
                                params["uploader"],
                                params["weight"],
                                params["mark"],
                            ))
        self.conn.commit()
        return True

    @sql_term
    def uploadAssignment(self, params: dict) -> bool:
        self.cursor.execute("""
            INSERT INTO
                file
                (TASK_ID, FILE_ID, FILE_NAME, AUTHOR, DATE)
            values
                (%s, %s, %s, %s, %s)""",
                            (params["TASK_ID"],
                             params["FILE_ID"],
                                params["FILE_NAME"],
                                params["AUTHOR"],
                                params["DATE"]))
        self.conn.commit()

        self.cursor.execute("""
            UPDATE
                assignment
            SET
                assignment.STATUS = "已繳交"
            WHERE
                assignment.TASK_ID = %s
                AND assignment.PROJECT_ID = %s """,
                            (params["TASK_ID"], params["projectUUID"]))
        self.conn.commit()
        return True

    @sql_term
    def getIconImage(self, nid: str) -> str:
        self.cursor.execute("""
            SELECT
                login.ICON
            FROM
                login
            WHERE
                login.NID = %s """,
                            (nid,))

        icon_name = str(self.cursor.fetchone()[0])
        if icon_name == "default.png":
            return icon_name

        icon_name = f"{nid}/{icon_name}"
        return icon_name

    @sql_term
    def changeIcon(self, params: dict) -> bool:
        self.cursor.execute("""
            UPDATE
                login
            SET
                login.ICON = %s
            WHERE
                login.NID = %s""",
                            (params["filename"], params["nid"]))
        self.conn.commit()
        return True

    # dashboard

    @sql_term
    def getDeadlineProject(self, nid: str) -> list:
        c = self.conn.cursor(dictionary=True)
        c.execute("""
        SELECT
            assignment.TASK_ID, assignment.PROJECT_ID, assignment.NAME, assignment.SUBMISSION_DATE
        FROM
            assignment
        JOIN member
            ON assignment.PROJECT_ID = member.PROJECT_ID
        JOIN `group` AS gp
            ON gp.PROJECT_ID = member.PROJECT_ID AND gp.NID = member.NID AND gp.GID = assignment.GID
        WHERE
            member.NID = %s
            AND assignment.STATUS = "未完成"
            AND member.ENABLE = 1
            AND gp.ENABLE = 1
            AND assignment.ENABLE = 1
        ORDER BY
            ABS(DATEDIFF(assignment.SUBMISSION_DATE, NOW())) DESC""",
                  (nid,))

        return c.fetchall()

    @sql_term
    def getPermission(self, nid: str) -> int:
        self.cursor.execute("""
            SELECT login.PERMISSION
            FROM login
            WHERE login.NID = %s """,
                            (nid,))

        permission = self.cursor.fetchone()
        if permission:
            return permission[0]
        else:
            return 0

class LOGGER(SQLHandler):
    def __init__(self):
        self.sql_init()
        self.cursor = self.conn.cursor(dictionary=True)

    def log(self, event: str, args:  list) -> None:
        self.cursor.execute("""
            INSERT INTO log
                (log.EVENT, log.ARGs)
            VALUES
                (%s, %s)""", (event, str(args)))

        self.conn.commit()

    def record(self) -> list:
        self.cursor.execute("""SELECT * FROM log LIMIT 5000""")
        return self.cursor.fetchall()
