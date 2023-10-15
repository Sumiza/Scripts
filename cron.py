def cron(cron:str,timezone=None) -> bool:
    cron = [None if t == '*' else t for t in cron.split(' ')]
    
    if len(cron) != 5: raise ValueError('Wrong Cron setup')
    
    curdatetime = datetime.datetime.now(tz=timezone)

    def parsesingle(r:str) -> list:
        if '-' in r:
            r = r.split('-')
            return [i for i in range(int(r[0]),int(r[1])+1)]
        elif '/' in r:
            ...
        else:
            return [int(r)]

    def parseall(parseme:list) -> list:
        output = []
        for t in parseme:
            if t is not None:
                t = t.split(',')
                hold = []
                for i in t:
                    hold.append(parsesingle(i))
                    if len(hold) > 1:
                        hold[0] = hold[0] + hold[1]
                        hold = hold[:1]
                output.append(*hold)
            else:
                output.append(None)
        return output

    parsedcron = parseall(cron)
    print(parsedcron)
    print(cron)
    minutes = parsedcron[0]
    hours = parsedcron[1]
    days = parsedcron[2]
    months = parsedcron[3]
    weekday = parsedcron[4]

    if months is not None and curdatetime.month in months: print('month')
    if weekday is not None and curdatetime.weekday() in weekday: print('weekda')
    if days is not None and curdatetime.day in days: print('day')
    if hours is not None and curdatetime.hour in hours: print('hour')
    if minutes is not None and curdatetime.minute in minutes: print('minue')
 

    return True

print(cron('2,7-9 3,5,18-21 4 * 1,3'))
# print(cron('0-59 2-5,18-21 1-31 1-4,9,10 0-3,6'))
