def sectotext(seconds:int):
    seconds = int(seconds)
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

    return ", ".join([ res for res in p if res[0] != "0" ])

# print(sectotext(44801048))
# returns: 1 Year, 5 Months, 1 Day, 10 Hours, 44 Minutes, 8 Seconds
