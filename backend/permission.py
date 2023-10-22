# Code by AkinoAlice@Tyrant_Rex

from handler import SQLHandler
import json


class PERMISSION(object):
    """
        IMPORTANT new function from authenticate.py should regis to setting.json
        or else it cause exception
        This module based on the permission setting of setting.json
        If you want to change the permission setting, you can edit the setting.json

    """
    def __init__(self, nid: str) -> None:
        self.nid = nid
        self.permission_level = SQLHandler().getPermission(self.nid)
        self.roles = {
            0: "No Permission",
            1: "Student",
            2: "Teacher",
            3: "Administrator",
        }
        try:
            with open("setting.json", "r") as f:
                self.permission_setting = json.load(f)["permissions"]
        except Exception as error:
            print(error, flush=True)
            raise FileNotFoundError("File not found: setting.json ")

    def __str__(self) -> str:
        return self.roles[self.permission]

    def get_role(self) -> str:
        return self.roles[self.permission]

    def get_levels(self) -> int:
        return self.permission_level

    def check_permission(self, func_name: str) -> bool:
        if self.permission_level >= self.permission_setting[func_name]:
            return True
        return False
