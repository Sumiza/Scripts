


from urlrequest import UrlRequest
import json

# servers:
# https://1.1.1.1/dns-query?
# https://dns.google/resolve?
# https://dns.alidns.com/resolve?

class DoHcheck:
    def __init__(self,server:str='https://1.1.1.1/dns-query?',domain:str='google.com',type:str='a',timeout:float=10):
        self.server = server
        self.domain = domain
        self.type = type
        self.timeout = timeout

    def __str__(self):
        r = self.runurl(self.type)
        if r['Status'] == 0:
            return str(r['Answer'][0]['data'])
        return str("Error")
    
    def runurl(self,type):
        self.type = type
        url = f'{self.server}name={self.domain}&type={self.type}'
        header = {'accept': 'application/dns-json'}
        r = UrlRequest(url,timeout=self.timeout,headers=header)
        return r.json

    def check(self,*args):
        allres = {}
        for arg in args:
            allres[arg] = self.runurl(type=arg)
        return allres




a = DoHcheck('https://dns.alidns.com/resolve?','github.com').check('A','AAAA','MX','TXT','NS','SOA','CNAME','PTR','SRV','SPF')
# a = DoHcheck('https://dns.alidns.com/resolve?','github.com')
print(json.dumps(a,indent=4))
print(type(a))
# print(a['a']['Status'])
print(a)

