import os
import subprocess
import time
import multiprocessing

class SSH_Vanity_Gen():
    
    def __init__(self,
                 findlist:list,
                 lettercase:bool=False,
                 findtoal:int=1,
                 passphrase:str=None,
                 comment:str='""',
                 threads:int=None,
                 rounds:int=16) -> None:
        
        self.findlist = []
        self.lettercase = lettercase

        for find in findlist:
            self.addfind(find)

        self.rounds = rounds
        self.curcount = 0
        
        self.findtotal = findtoal
        self.comment = comment
        self.passphrase = passphrase
        
        if threads:
            self.threads = threads
        else:
            self.threads = os.cpu_count()            
    
    def addfind(self,find:str) -> bool:
        if self.lettercase is False:
            find = find.casefold()
        self.findlist.append(find)
        return True
    
    def removefind(self,remove:str) -> bool:
        try: 
            self.findlist.remove(remove)
        except: 
            return False

    def subrun(self,subcall):
        subprocess.call(subcall,shell=True,stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL)

    def _genkey(self,sharedcount,foundcount,threadid:int):
        localcount = 0
        while True:
        
            if foundcount.value >= self.findtotal:
                break

            self.subrun(f'ssh-keygen -t ed25519 -f {threadid}-{localcount} -C {self.comment} -N ""')
            
            with open(f'{threadid}-{localcount}.pub') as file:
                pubkey = file.read()
            
            if self.lettercase is False:
                pubkey = pubkey.lower()
            
            for find in self.findlist:
                if find in pubkey:
                    with foundcount.get_lock():
                        foundcount.value += 1
                    if self.passphrase:
                        self.subrun(f'ssh-keygen -p -a {self.rounds} -f {threadid}-{localcount} -N {self.passphrase}')
                    os.rename(f'{threadid}-{localcount}.pub',f'{threadid}-{localcount}-{find}.pub')
                    os.rename(f'{threadid}-{localcount}',f'{threadid}-{localcount}-{find}')
                    self.foundone(threadid,localcount,find,pubkey)
                else:
                    os.remove(f'{threadid}-{localcount}.pub')
                    os.remove(f'{threadid}-{localcount}')

            localcount += 1
            with sharedcount.get_lock():
                sharedcount.value += 1

    def foundone(self,threadid,localcount,find,pubkey):
        # print(f'{threadid}-{localcount}-{find}:',pubkey)
        pass
        
    def start(self):
        self.multilist = []
        sharedcount = multiprocessing.Value('i',0)
        foundcount = multiprocessing.Value('i',0)
        for threadid in range(self.threads):
            process = multiprocessing.Process(target=self._genkey,args=(sharedcount,foundcount,threadid))
            process.start()
            self.multilist.append(process)

        print(f'{len(self.multilist)} processes have started')
        self._waiting(sharedcount,foundcount)
    
    def status(self,sharedcount,foundcount):
        # print(sharedcount.value,foundcount.value)
        pass

    def _waiting(self,sharedcount,foundcount):

        while foundcount.value < self.findtotal:
            self.status(sharedcount,foundcount)
            time.sleep(5)

        for process in self.multilist:
            process:multiprocessing.Process
            process.join()

        print('Done')
    
    def stop(self):
        self.findtotal = 0

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('')

    class s(SSH_Vanity_Gen):

        def foundone(self, threadid, localcount, find, pubkey):
            print(threadid, localcount, find, pubkey,)
        
        def status(self, sharedcount, foundcount):
            print(f'Keys Generated: {sharedcount.value}, Keys Found: {foundcount.value}')

    a = s(['Cooler'],findtoal=5)
    a.start()
