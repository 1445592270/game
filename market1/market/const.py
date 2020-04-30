from enum import Enum


class TaskType(Enum):
    """任务类型"""

    BACKTEST = "T_BT"
    BACKTEST_COMPILE = "T_COM"
    PAPER_TRADING = "T_SIM"
    LIVE_TRADING = "T_REAL"
    UNKNOWN = "T_UNKNOWN"


class SMSType(Enum):
    user_reg = 1
    reset_pass = 2
    user_login = 4

    def to_tmpl_id(self):
        if self.value == 1:
            return "SMS_185570173"
        elif self.value == 2:
            return "SMS_185575161"
        elif self.value == 3:
            return "SMS_185555180"
        else:
            return ""
