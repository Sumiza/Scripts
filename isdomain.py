import re
a = re.search('^([a-z0-9\d-])*\.[a-z]{1,4}$',"google.com")
if a:
    print(a.string)
