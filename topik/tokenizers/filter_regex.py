import re

predefined_filters= {
    'html': '<\/?[^>]+>'
}

def filter_regex(text, regex):
    if regex:
        if regex in predefined_filters:
            regex = predefined_filters[regex]
        text = re.sub(regex, "", text)
    return text
