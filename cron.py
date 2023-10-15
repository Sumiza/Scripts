def cron(cron:str,timezone:datetime=None) -> bool:
    cron = [None if t == '*' else t for t in cron.split(' ')]
    
    if len(cron) != 5: raise ValueError('Wrong Cron setup')
    
    curdatetime = datetime.datetime.now(tz=timezone)

    minutes = cron[0]
    hours = cron[1]
    days = cron[2]
    months = cron[3]
    weekday = cron[4]

    if curdatetime.month != months: return False
    if curdatetime.day != days: return False
    if curdatetime.hour != hours: return False
    if curdatetime.minute != minutes: return False
    if curdatetime.weekday() != weekday: return False

    print(cron)
    print(curdatetime)
