def sectotext(seconds:int,restype:str=""):
    """
    Converts seconds to human readable text or tuple
    
    Args:
        seconds:    amount of seconds for it to process,
                    can be float but will be changed to int,
                    can be negative but will be changed to positive.
                    
        restype:
                default:    skips any part of the response that is 0.
                    print(sectotext(12069123,"showall"))
                    0 Years, 4 Months, 18 Days, 0 Hours, 32 Minutes, 3 Seconds

                showzeros:  trims any part before the first not 0.
                    print(sectotext(-12069123,"showzeros"))
                    4 Months, 18 Days, 0 Hours, 32 Minutes, 3 Seconds
                
                showall:    shows all parts.
                    print(sectotext(12069123))
                    4 Months, 18 Days, 32 Minutes, 3 Seconds
                
                rawtuple:   returns a 6 part tuple.
                    print(sectotext(12069123,"rawtuple"))
                    (0, 4, 18, 0, 32, 3)
    """
    
    seconds = int(seconds)
    if seconds < 0:
        seconds = seconds * -1
    years, seconds = divmod(seconds,31536000)
    months, seconds = divmod(seconds,2628000)
    days, seconds = divmod(seconds,86400)
    hours, seconds = divmod(seconds,3600)
    minutes, seconds = divmod(seconds,60)

    def plural(n:str):
        if n != 1:
            return "s"
        return ""
        
    p = [f"{years} Year{plural(years)}",
        f"{months} Month{plural(months)}",
        f"{days} Day{plural(days)}", 
        f"{hours} Hour{plural(hours)}", 
        f"{minutes} Minute{plural(minutes)}", 
        f"{seconds} Second{plural(seconds)}"]
    
    if restype == "showzeros":
        for loc,res in enumerate(p):
            if res[0] != "0":
                return ", ".join(p[loc:len(p)])
    elif restype == "showall":
        return ", ".join([ res for res in p])
    elif restype == "rawtuple":
        return (years,months,days,hours,minutes,seconds)
    else:
        return ", ".join([ res for res in p if res[0] != "0" ])
        
