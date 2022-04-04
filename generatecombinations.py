def buildlist(count:int,letters:str) -> list:
    letterlen=len(letters)
    holdlist=[]
    for _ in range(int((letterlen**count)/letterlen)):
        for b in letters:
            holdlist.append(b)
    holdlist.sort()
    tcount=0
    for _ in range(count-1):
        lcount= 0
        holdlist2=[]
        holdlist.reverse()
        for _ in range(len(holdlist)):
            mod = holdlist.pop()
            holdlist2.append(mod+letters[lcount])
            lcount+=1
            tcount+=1
            if lcount >= len(letters):
                lcount = 0
        holdlist = holdlist2.copy()
        holdlist.sort()
    holdlist.sort()
    return holdlist

allletters = "abcdefghijklmnopqrstuvwxyz"+"0123456789"+"-"
domainlist= buildlist(3,allletters)
print(domainlist)
