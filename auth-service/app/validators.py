import re
from typing import Pattern

def regex_validator(pattern: str | Pattern, data: str, err_msg: str) -> str:
    if not re.match(pattern, data):
        raise ValueError(err_msg)
    return data