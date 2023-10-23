import os
import subprocess
import time
import multiprocessing

howmany = 5
lookfor = 'Sumiza'
lettercase = False
passphrase = '""'
comment = '@computer'
rounds = 16


def genkey(id,lookfor:str,findtotal,passphrase,comment,foundcounter):
    count = 0
    while True:

        if foundcounter.value >= findtotal:
            break

        call = f'ssh-keygen -t ed25519 -f {id}-{count} -N {passphrase} -C {comment} -a {rounds}'

        subprocess.call(call,shell=True,stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL)

        with open(f'{id}-{count}.pub') as file:
            pubkey = file.read()
        
        if lettercase is False:
            lookfor = lookfor.lower()
            pubkey = pubkey.lower()

        if lookfor in pubkey:
            foundcounter.value += 1
            print(f'{foundcounter.value}. {id}-{count}:',pubkey)
        else:
            os.remove(f'{id}-{count}.pub')
            os.remove(f'{id}-{count}')
        count += 1
        # eachcounter.value += 1
        
print('Started')

multilist = []
foundcounter = multiprocessing.Value('i',0)
eachcouter = multiprocessing.Value('i',0)
for cpu in range(os.cpu_count()):
    p = multiprocessing.Process(target=genkey,args=(cpu,lookfor,howmany,passphrase,comment,foundcounter))
    p.start()
    multilist.append(p)

time.sleep(5)
# while foundcounter.value <= howmany:
#     print(eachcouter.value)
#     time.sleep(5)

print(multilist)
for m in multilist:
    m:multiprocessing.Process
    m.join()

print(multilist)
# for t in threadlist:
#     t:threading.Thread
#     t.join()

print('done')
