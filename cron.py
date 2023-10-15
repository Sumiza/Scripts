def cron(cron:str,timezone=None) -> bool:
    cron = cron.split(' ')
    for idx, i in enumerate(cron):
        if '*' in i:
            if '/' in i:
                i = i.split('/')
                if idx == 0: i[0] = str(60) #minutes
                elif idx == 1: i[0] = str(24) #hours
                elif idx == 2: i[0] = str(31) #days
                elif idx == 3: i[0] = str(12) #months
                cron[idx] = '/'.join(i)
            else:
                cron[idx] = None
    
    if len(cron) != 5: raise ValueError('Wrong number of cron variables should be "* * * * *"')
    
    curdatetime = datetime.datetime.now(tz=timezone)

    def parsesingle(r:str,daymonth:int) -> list:
        if '-' in r:
            r = r.split('-')
            return [i for i in range(int(r[0]),int(r[1])+1)]
        elif '/' in r:
            r = r.split('/')
            return [(i+daymonth)*int(r[1]) for i in range(int(r[0])//int(r[1]))]
        else:
            return [int(r)]

    def parseall(parseme:list) -> list:
        output = []
        for idx, t in enumerate(parseme):
            if t is not None:
                t = t.split(',')
                hold = []
                if idx == 0 or idx == 1: daymonth = 0
                else : daymonth = 1 # there are no 0 days
                for i in t:
                    hold.append(parsesingle(i,daymonth))
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

print(cron('*/30 0 */5 * *'))
