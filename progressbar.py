def progressbar(current:float, total:float,posttext:str="",pretext:str="Progress:",length:int=60,endtext:str="",endline:str='\r',re:bool=False):
    """ 
        Progress Bar
        Args:
        current*(float) Current iterations of total.
        total*  (float) Total iterations that will be run.
        posttext(str)   Text to appear after the current X% [count].
        pretext (str)   First word in line (default Progress:)
        length  (int)   Length of the progress bar (default 60)
        endtext (str)   Text to replace posttext at 100% complete
        endline (str)   end variable for print (default '\r')
        re      (bool)  returns progress bar rather than printing (default False)
        *required
        Basic Example:
        from progressbar import progressbar
        for i in range(101):
            progressbar(i,100)
    """
    done=int((current/total)*100)
    barlen=int(done/100*length)
    bar = "█"*barlen+"░"*(length-barlen)
    if total == current:
        if endtext != "":
            posttext = endtext+" "*(len(str(posttext))-len(str(endtext)))
        endline = '\n'
    comb=f"{pretext} {bar} {done}% [{current}/{total}] {posttext}"
    if re == False:
        print(comb,end=endline)
    else:
        return comb

def progressbardiscord(current:float, total:float,posttext:str="",pretext:str="Progress:",length:int=32,endtext:str="",idtoken:str="",idtime:tuple=("",0),disuser:str="Progress Bot",throttle:float=0.5):
    import requests
    import json
    from time import time
    """
    Discord progress bar
        Args:
        current*(float) Current iterations of total
        total*  (float) Total iterations that will be run
        posttext(str)   Text to appear after the current X% [count]
        pretext (str)   First word in line (default Progress:)
        length  (int)   Length of the progress bar (default 32)
        endtext (str)   Text to replace posttext at 100% complete
        idtoken*(str)   {webhook.id}/{webhook.token} part of webhook
        idtime**(tuple) message id and time of last message 
        disuser*(str)   User name for the bot
        throttle(float) Time between updates of discord message cf rate is 5/2sec
        *required
        **required to modify only not as first message
        Basic Example:
        import progressbar
        tok="555555555555555555/TRPM9nM1fRwxVMIxFPRurzg-2GsWXePGBsUunnjOeolzr80R7QBPbV8iz6OjgfNZ0_M-"
        id=("",0)
        for i in range(201):
            id = progressbar.progressbardiscord(i,200,idtoken=tok,idtime=id)
    """
    messid,lastime = idtime
    if lastime+throttle <= time() or lastime == 0 or current == total:
        
        bar = progressbar(current,total,posttext=posttext,pretext=pretext,length=length,endtext=endtext,re=True)
        
        webheader = {"Content-Type": "application/json; charset=utf-8"}
        webhook = "https://discord.com/api/webhooks/"+idtoken
        
        if messid == "":
            try:
                data= {"content":f"{bar}","username": f"{disuser}"}
                a = requests.post(webhook+"?wait=true",headers=webheader,data=json.dumps(data))
                if 200 >= a.status_code < 400:
                    messid = str(json.loads(a.text)["id"])
                else:
                    return ("",0) #return blank so it will try posting message again.
            except:
                pass
        else:
            try:
                data= {"content":f"{bar}"}
                a = requests.patch(webhook+"/messages/"+messid,headers=webheader,data=json.dumps(data))
            except:
                pass
        lastime = time()
    return (messid,lastime)
