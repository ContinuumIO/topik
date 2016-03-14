import re


def filter_regex(text, regex):
    if regex:
        text = re.sub(regex, "", text)
    return text