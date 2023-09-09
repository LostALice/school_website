#Code by AkinoAlice@Tyrant_Rex

import mysql.connector as connector

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
        self.DATABASE = "test"
        self.HOST = "localhost"
        self.USER = "root"
        self.PASSWORD = "Zyon-56241428"

        # for environment variables
        # self.DATABASE = os.getenv("SQL_DATABASE")
        # self.HOST = os.getenv("SQL_HOST")
        # self.USER = os.getenv("SQL_USER")
        # self.PASSWORD = os.getenv("SQL_PASSWORD")

        self.JWT_TOKEN_EXPIRE_TIME = 3600  # Token valid for 1 Hour
        self.JWT_SECRET = "My wife is kurumi"   # Encryption and decryption key
        self.JWT_ALGORITHM = "HS256"  # encryption and decryption algorithm e.g.

        # self.JWT_TOKEN_EXPIRE_TIME = os.getenv("JWT_TOKEN_EXPIRE_TIME")
        # self.JWT_SECRET = os.getenv("JWT_SECRET")
        # self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

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
            self.conn.close()
            return _
        return warp

    # subject
    @sql_term
    def getSubjectData(self, nid: str="") -> dict:
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

        # bind subject and creator
        self.cursor.execute("""
            INSERT INTO member (
                member.PROJECT_ID,
                member.NID
            )
            VALUES (
                %s, %s
            );""", (
                params["projectUUID"],
                params["nid"],
            )
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
    def deleteSubjectData(self, subjectUUID: str="") -> bool:
        self.cursor.execute("""
            UPDATE subject
            SET subject.ENABLE = 0
            WHERE subject.SUBJECT_ID = %s ;
        """, (subjectUUID,))
        self.conn.commit()
        return True

    # project
    @sql_term
    def getProjectData(self, projectData: str="") -> dict:
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
                SELECT count(`group`.GID) as `group`
                FROM
                    project
                INNER JOIN
                    member on project.PROJECT_ID = member.PROJECT_ID
                INNER JOIN
                    `group` on project.PROJECT_ID = `group`.PROJECT_ID
                WHERE
                    project.PROJECT_ID = %s AND member.NID = %s AND `group`.ENABLE = 1""",
                    (i[0], projectData["NID"])
            )
            data["group"].append(self.cursor.fetchall()[0])

            # assignment
            self.cursor.execute("""
                SELECT count(assignment.TASK_ID) as task
                FROM
                    project
                INNER JOIN
                    member on project.PROJECT_ID = member.PROJECT_ID
                INNER JOIN
                    assignment on project.PROJECT_ID = assignment.PROJECT_ID
                WHERE
                    project.PROJECT_ID = %s AND member.NID = %s AND assignment.ENABLE = 1""",
                    (i[0], projectData["NID"])
            )
            data["assignment"].append(self.cursor.fetchall()[0])

        return data

    @sql_term
    def createProjectData(self, params: dict={}) -> bool:
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
    def deleteProjectData(self, projectUUID: str="") -> bool:
        self.cursor.execute("""
            UPDATE project
            SET project.ENABLE = 0
            WHERE project.PROJECT_ID = %s ;
        """, (projectUUID,))
        self.conn.commit()
        return True

    @sql_term
    def getProjectInfo(self, projectUUID: str="") -> dict:
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
    def getAnnouncementData(self, projectUUID: str="") -> dict:
        self.cursor.execute("""
            SELECT
                announcements.ANNOUNCEMENTS_ID, announcements.AUTHOR, announcements.TITLE, announcements.LAST_EDIT
            FROM
                announcements
            JOIN
                member ON member.PROJECT_ID = announcements.PROJECT_ID
            WHERE
                member.PROJECT_ID = %s AND announcements.ENABLE = 1""",(
                    projectUUID,
                ))

        announcementData = self.cursor.fetchall()
        return announcementData

    @sql_term
    def createAnnouncement(self, params: dict={}) -> bool:
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
    def getAnnouncementInfo(self, announcementUUID: str="") -> dict:
        print(announcementUUID)
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
    def getStudentData(self, projectUUID: str="") -> dict:
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
        print(studentData)
        return studentData

    @sql_term
    def getStudentList(self) -> dict:
        self.cursor.execute("""
        SELECT
            login.NID, login.USERNAME
        FROM
            login
        LEFT JOIN student
            ON login.NID = student.NID
        WHERE
            student.NID IS NULL AND login.NID LIKE "D%" """)

        studentList = self.cursor.fetchall()
        return studentList

    @sql_term
    def newStudent(self, params: dict={}) -> bool:
        print(params)
        self.cursor.execute("""
            INSERT INTO student
                (student.PROJECT_ID, student.NID)
            VALUES
                (%s, %s)""",(params["projectUUID"], params["nid"]))
        self.conn.commit()
        return True

    @sql_term
    def deleteStudent(self, params: dict={}) -> bool:
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
    def getStudentInfo(self, nid: str="") -> dict:
        self.cursor.execute("""
            SELECT
                login.USERNAME, login.PERMISSION
            FROM
                login
            WHERE
                login.NID = %s""", (nid,))
        info = self.cursor.fetchone()
        return info

    @sql_term
    def importStudent(self, projectUUID: str="") -> bool:
        ...

    # teacher
    @sql_term
    def getTeacherData(self, projectUUID: str="") -> dict:
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
        LEFT JOIN teacher
            ON login.NID = teacher.NID
        WHERE
            teacher.NID IS NULL AND login.NID LIKE "T%" """)

        teacherList = self.cursor.fetchall()
        return teacherList

    @sql_term
    def newTeacher(self, params: dict={}) -> bool:
        print(params)
        self.cursor.execute("""
            INSERT INTO teacher
                (teacher.PROJECT_ID, teacher.NID)
            VALUES
                (%s, %s)""",(params["projectUUID"], params["nid"]))
        self.conn.commit()
        return True

    @sql_term
    def deleteTeacher(self, params: dict={}) -> bool:
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
    def getTeacherInfo(self, nid: str="") -> dict:
        self.cursor.execute("""
            SELECT
                login.USERNAME, login.PERMISSION
            FROM
                login
            WHERE
                login.NID = %s""", (nid,))
        info = self.cursor.fetchone()
        return info

    @sql_term
    def importTeacher(self, projectUUID: str="") -> bool:
        ...

    # group
    @sql_term
    def getGroupData(self, projectUUID: str) -> list:
        self.cursor.execute("""
            SELECT
                gp.GID
            FROM
                `group` as gp
            WHERE
                gp.PROJECT_ID = %s AND gp.ENABLE = 1
            GROUP BY
                gp.GID;""", (projectUUID,))
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
            data["teacher"] = self.cursor.fetchone()[0]

            self.cursor.execute("""
            SELECT
                COUNT(gp.NID)
            FROM
                `group` as gp
            WHERE
                gp.GID = %s AND gp.ENABLE = 1 AND gp.NID LIKE "D%" """,
                (i[0],))
            data["student"] = self.cursor.fetchone()[0]

            self.cursor.execute("""
            SELECT
                gp.NAME
            FROM
                `group` as gp
            WHERE
                gp.GID = %s AND gp.ENABLE = 1 """,
                (i[0],))
            data["name"] = self.cursor.fetchone()[0]

            groupData.append(data)
        return groupData

    @sql_term
    def newGroup(self, params: dict) -> bool:
        self.cursor.execute("""
            INSERT INTO
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
                student.PROJECT_ID = %s AND student.ENABLE = 1 """,(projectUUID,))
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
                teacher.PROJECT_ID = %s AND teacher.ENABLE = 1 """,(projectUUID,))
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

# development only
if __name__ == "__main__":
    a = SQLHandler("D1177531", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiRDExNzc1MzEiLCJleHAiOjE2OTMyMDMyMjd9.0aRf7pmiPjtCVuumXNjMXEda9wukzUKZoEb0Hs3H23g")
    b = a.getSubjectData()