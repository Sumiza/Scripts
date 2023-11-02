import datetime

import timeit

def datetoepoch(date):
    """
    turn epoch time to datetime
    """
    datetimestr = datetime.datetime.utcfromtimestamp(date).timetuple()

    print(datetimestr)

print(datetoepoch(32))

a= timeit.("datetoepoch(32)",globals=globals(),number=100)
print(a)
print(globals())