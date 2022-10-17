import requests
import multiprocessing as mp

class Check():

    def __init__(
            self,timeout=10,
            header:dict=None,
            method:str='GET',
            returnexception:bool=False,) -> None:

        self.timeout = timeout
        self.method = method
        self.header = header
        self.returnexception = returnexception

    def _checksite(self,url:str) -> list:
        try:
            if self.method == 'GET':
                response = requests.get(url,timeout=self.timeout,headers=self.header)
            elif self.method == 'POST':
                response = requests.post(url,timeout=self.timeout,headers=self.header)
        except Exception as e:
            if self.returnexception:
                response = e
            else:
                response = None
        return [url,response]

    def first(self,urllist:list) -> list:
        with mp.Pool(len(urllist)) as pool:
            for urlres in pool.imap_unordered(self._checksite,(urllist)):
                if isinstance(urlres[1],(requests.models.Response)):
                    pool.terminate()
                    return [urlres]
                
    def all(self,urllist:list) -> list:
        with mp.Pool(len(urllist)) as pool:
            res = pool.imap(self._checksite,(urllist))
            pool.close()
            pool.join()
            return [res for res in res]