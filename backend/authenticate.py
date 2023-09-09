#Code by AkinoAlice@Tyrant_Rex

from handler import SQLHandler

import hashlib, jwt, time, re

class AUTHENTICATION(SQLHandler):
    def __init__(self) -> None:
        self.sql_init()
        self.injection_keywords = ["'",
            '"',
            '#',
            '-',
            '--',
            "'%20--",
            "--';",
            "'%20;",
            "=%20'",
            '=%20;',
            '=%20--',
            '#',
            "'",
            "=%20;'",
            "=%20'",
            "'OR SELECT *",
            "'or SELECT *",
            "'or%20select *",
            "admin'--",
            '<>"\'%;)(&+',
            "'%20or%20''='",
            "'%20or%20'x'='x",
            '"%20or%20"x"="x',
            "')%20or%20('x'='x",
            '0 or 1=1',
            "' or 0=0 --",
            '" or 0=0 --',
            'or 0=0 --',
            "' or 0=0 #",
            '" or 0=0 #',
            'or 0=0 #',
            "' or 1=1--",
            '" or 1=1--',
            "' or '1'='1'--",
            '"\' or 1 --\'"',
            'or 1=1--',
            'or%201=1',
            'or%201=1 --',
            "' or 1=1 or ''='",
            '" or 1=1 or ""="',
            "' or a=a--",
            '" or "a"="a',
            "') or ('a'='a",
            '") or ("a"="a',
            'hi" or "a"="a',
            'hi" or 1=1 --',
            "hi' or 1=1 --",
            "hi' or 'a'='a",
            "hi') or ('a'='a",
            'hi") or ("a"="a',
            "'hi' or 'x'='x';",
            '@variable',
            ',@variable',
            'PRINT',
            'PRINT @@variable',
            'select',
            'insert',
            'as',
            'or',
            'procedure',
            'limit',
            'order by',
            'asc',
            'desc',
            'delete',
            'update',
            'distinct',
            'having',
            'truncate',
            'replace',
            'like',
            'handler',
            'bfilename',
            "' or username like '%",
            "' or uname like '%",
            "' or userid like '%",
            "' or uid like '%",
            "' or user like '%",
            'exec xp',
            'exec sp',
            "'; exec master..xp_cmdshell",
            "'; exec xp_regread",
            "t'exec master..xp_cmdshell 'nslookup www.google.com'--",
            '--sp_password',
            "'UNION SELECT",
            "' UNION SELECT",
            "' UNION ALL SELECT",
            "' or (EXISTS)",
            "' (select top 1",
            "'||UTL_HTTP.REQUEST",
            '1;SELECT%20*',
            'to_timestamp_tz',
            'tz_offset',
            "&lt;&gt;&quot;'%;)(&amp;+",
            "'%20or%201=1",
            '%27%20or%201=1',
            '%20$(sleep%2050)',
            "%20'sleep%2050'",
            'char%4039%41%2b%40SELECT',
            '&apos;%20OR',
            "'sqlattempt1",
            '(sqlattempt2)',
            '|',
            '%7C',
            '*|',
            '%2A%7C',
            '*(|(mail=*))',
            '%2A%28%7C%28mail%3D%2A%29%29',
            '*(|(objectclass=*))',
            '%2A%28%7C%28objectclass%3D%2A%29%29',
            '(',
            '%28',
            ')',
            '%29',
            '&',
            '%26',
            '!',
            '%21',
            "' or 1=1 or ''='",
            "' or ''='",
            "x' or 1=1 or 'x'='y",
            '/',
            '//',
            '//*',
            '*/*',
            "drop",
            "DROP",
            "Drop",
        ]

    def SQLInjectionCheck(self, nid: str=None, JWT: str=None, prompt: str="") -> bool:
        """Check if the given nid and JWT contain SQL injection keywords

        Args:
            nid (str, optional): NID. Defaults to None.
            JWT (str, optional): JSON Web Token. Defaults to None.
            prompt (str, optional): Incoming query words. Defaults to "".

        Returns:
            bool: True = pass, False = Error
        """
        if nid:
            return True if re.match(r"^[dtDT]\d{7}$", nid) else False

        if JWT:
            try:
                jwt.decode(JWT, self.JWT_SECRET, algorithms=self.JWT_ALGORITHM)
            except:
                return False

        if prompt in self.injection_keywords:
            return False

        return True

    # return a hashed and salted password
    # method: "hashed password" + "nid" => hash function = new hashed password
    def authenticate(self, nid: str, hashed_password: str) -> set:
        self.sql_init()
        sha256 = hashlib.sha256()
        string = hashed_password + nid

        sha256.update(string.encode("utf8"))
        new_hashed_password = sha256.hexdigest()

        if not self.SQLInjectionCheck(nid=nid, JWT=hashed_password):
            return False

        self.cursor.execute("SELECT * FROM login WHERE `NID` = %s and `PASSWORD` = %s;", (nid, new_hashed_password))

        if self.cursor.fetchall():
            token = self.generate_jwt_token(nid)
            print(nid, token)
            self.cursor.execute("UPDATE login SET `NID` = %s, `TOKEN` = %s WHERE `NID` = %s;", (nid, token, nid))
            self.conn.commit()
            self.conn.close()
            return {
                "x-access-token": token
            }
        else:
            return False

    def generate_jwt_token(self, user_id: str) -> str:
        payload = {
            "user_id": user_id,
            "exp": int(time.time()) + self.JWT_TOKEN_EXPIRE_TIME
        }
        token = jwt.encode(payload, self.JWT_SECRET, algorithm=self.JWT_ALGORITHM)
        return token

    def verify_jwt_token(self, nid: str, token: str) -> bool:
        if not self.SQLInjectionCheck(nid=nid, JWT=token):
            return False

        self.cursor.execute("SELECT * FROM login WHERE `NID` = %s and `TOKEN` = %s;", (nid, token))
        if self.cursor.fetchall():
            return True
        else:
            return False

    def verify_timeout(self, nid: str, token: str) -> bool:
        if not self.SQLInjectionCheck(nid=nid, JWT=token):
            return False

        try:
            jwt.decode(token, self.JWT_SECRET, algorithms=self.JWT_ALGORITHM)
        except jwt.exceptions.ExpiredSignatureError as error:
            self.cursor.execute("UPDATE login SET TOKEN = NULL WHERE NID = %s", (nid,))
            self.conn.commit()
            return False

        self.cursor.execute("SELECT * FROM login WHERE TOKEN = %s;",(token,))
        if self.cursor.fetchall():
            return True
        else:
            return False

    # def

# development only
if __name__ == "__main__":
    a = AUTHENTICATION()
    b = a.verify_jwt_token("D1177531","688787d8ff144c502c7f5cffaafe2cc588d86079f9de88304c26b0cb99ce91c6")
    print(b)

