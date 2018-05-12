# -*- coding: utf-8 -*-
import re

#在字符串中提取数字
def extract_num(text):
    match_re=re.match(".*?(\d+).*",text)
    if match_re:
        nums=int(match_re.group(1))
    else:
        nums=0
    return nums