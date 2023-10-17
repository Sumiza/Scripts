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
        if '-'in r and '/' in r:
            r = r.replace('-',' ').replace('/',' ').split()
            start = int(r[0]) % int(r[2])
            return [i for i in range(int(r[0]),int(r[1])) if i % int(r[2]) == start]

        if '-' in r:
            r = r.split('-')
            return [i for i in range(int(r[0]),int(r[1])+1)]
        
        if '/' in r:
            r = r.split('/')
            return [(i+daymonth)*int(r[1]) for i in range(int(r[0])//int(r[1]))]
        
        return [int(r)]

    def parseall(parseme:list) -> list:
        output = []
        for idx, part in enumerate(parseme):
            if part is not None:
                part = part.split(',')
                hold = []
                if idx == 0 or idx == 1: daymonth = 0
                else : daymonth = 1 # there are no 0 days
                for i in part:
                    hold.append(parsesingle(i,daymonth))
                    if len(hold) > 1:
                        hold[0] = hold[0] + hold[1]
                        hold = hold[:1]
                output.append(*hold)
            else:
                output.append(None)
        return output

    parsedcron = parseall(cron)
    # print(parsedcron)
    # print(cron)
    minutes = parsedcron[0]
    hours = parsedcron[1]
    days = parsedcron[2]
    months = parsedcron[3]
    weekday = parsedcron[4]
    # print(curdatetime.minute,curdatetime.hour,curdatetime.day,curdatetime.weekday(),curdatetime.month)
    
    if months is not None and curdatetime.month not in months: return False
    if weekday is not None and curdatetime.weekday() not in weekday: return False
    if days is not None and curdatetime.day not in days: return False
    if hours is not None and curdatetime.hour not in hours: return False
    if minutes is not None and curdatetime.minute not in minutes: return False

    return True

oldtrig = None
while True:
    newtrig = time.time()//60
    if oldtrig != newtrig:
        oldtrig = newtrig
        print(cron('30-60/2 */2 5 1-5 *'))
    time.sleep(5)
