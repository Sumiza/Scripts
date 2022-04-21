import re
a = re.search('^[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9][.][a-zA-Z]*$',"google.com")
if a:
    print(a.string)
