# %%
import pandas as pd
import numpy as np
import json
import re
from datetime import datetime
# %%
class Validator():
    def __init__(self) -> None:
        pass


    def funcS(myTime):
        if myTime == -1:
            return None
        elif re.match(r"^\d+$", str(myTime)):
            return (datetime.strptime(myTime, "%H").time())
        elif re.match(r"^\d+:\d+$", myTime):
            return (datetime.strptime(myTime, "%H:%M").time())
        elif re.match(r"^\d+:\d+:\d+$", myTime):
            return (datetime.strptime(myTime, "%H:%M:%S").time())
        else:
            return None


    def funcE(myTime):
        if myTime == -1:
            return None
        elif re.match(r"^\d+$", str(myTime)):
            if myTime == str(24):
                return (datetime.strptime("00", "%H").time())
            else:
                return (datetime.strptime(myTime, "%H").time())
        elif re.match(r"^\d+:\d+$", myTime):
            if myTime.split(":")[0] == str(24):
                return (datetime.strptime(re.sub(r"^24", "00", myTime), "%H:%M").time())
            else:
                return (datetime.strptime(myTime, "%H:%M").time())
        elif re.match(r"^\d+:\d+:\d+$", myTime):
            if myTime.split(":")[0] == str(24):
                return (datetime.strptime(re.sub(r"^24", "00", myTime), "%H:%M:%S").time())
            else:
                return (datetime.strptime(myTime, "%H:%M:%S").time())
        else:
            return None


    def validate(self, rate: float, rateRange: float, phone: str, **kwargs):
        if rate > rateRange:
            raise ValueError(f"Rate: {rate} is greather than rateRange: {rateRange}")
        else:
            rate = round(rate / (rateRange / 5), 1)

        # Validate Phone : 09123456789, 9123456789, 02134567890, 34567890
        if not re.match(r"(^0\d{10}$)|(^[1-9]\d{7}$)|(^9\d{9}$)", phone):
            raise ValueError(f"phone: '{phone}' is not correct !")
        
        for key in kwargs:
            if key == "workStart":
                if self.funcS(kwargs["workStart"]) == None:
                    raise ValueError(f"time: '{kwargs['workStart']}' is not correct!")
            if key == "workEnd":
                if self.funcE(kwargs["workEnd"]) == None:
                    raise ValueError(f"time: '{kwargs['workEnd']}' is not correct!")
            else:
                raise ValueError(f"{key} is not valid")

        return rate, phone, kwargs