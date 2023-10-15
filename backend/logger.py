# Code by AkinoAlice@Tyrant_Rex

from handler import SQLHandler


class LOGGER(SQLHandler):
    def __init__(self):
        self.sql_init()
        self.cursor = self.conn.cursor(dictionary=True)

    def log(self, event: str, args:  list) -> None:
        print(event, args)

    def record(self) -> list:
        self.cursor.execute("""SELECT * FROM log LIMIT 1000""")
        print(self.cursor.fetchall())

if __name__ == "__main__":
    log = LOGGER()
    log.record()