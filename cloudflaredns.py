from urlrequest import UrlRequest

class CloudflareDNS():
    def __init__(self,
                authkey:str = None,
                zoneid:str = None,
                url ='https://api.cloudflare.com/client/v4/',
                recordid:str = None,
                name:str = None,
                rectype:str='A',
                content:str = None,
                ttl:int = None,
                proxied:bool = None):
        self.authkey = authkey
        self.zoneid = zoneid
        self.url = url
        self.recordid = recordid
        self.name = name
        self.type = rectype
        self.content = content
        self.ttl = ttl
        self.proxied = proxied
        self.headers = {'User-Agent':'Cloudflare DNS Updater v1.0.0',
                        'Content-Type':'application/json',
                        'Authorization': self.authkey}

    def getrecords(self,name=None,type=None):
        if name: self.name = name
        if type: self.type = type
        if self.name == None:
            raise TypeError('DNS record name missing')
        url = self.url+'zones/'+self.zoneid+'/dns_records?type='+self.type+'&name='+self.name
        answer = UrlRequest.get(url,headers=self.headers)
        record = answer.json.get('result')
        if record:
            record = record[0]
            self.recordid = record.get('id')
            if self.content == None:
                self.content = record.get('content')
            if self.ttl == None:
                self.ttl = record.get('ttl')
            if self.proxied == None:
                self.proxied = record.get('proxied')
            return record
        else:
            return None

    def send(self,name=None,type=None,ttl=None,content=None): # update or create record
        if name: self.name = name
        if type: self.type = type
        if ttl: self.ttl = ttl
        if content: self.content = content
        self.getrecords()
        url = self.url+'zones/'+self.zoneid+'/dns_records/'
        data = {"type":self.type,"name":self.name,"content":self.content,"ttl":self.ttl,"proxied":self.proxied}
        if self.recordid: #update record
            url = url+self.recordid
            answer = UrlRequest.put(url,headers=self.headers,json=data)
        else:
            answer = UrlRequest.post(url,headers=self.headers,json=data)
        return answer

    def delete(self,name=None,type=None): # delete record
        if name: self.name = name
        if type: self.type = type
        self.getrecords()
        if self.recordid:
            url = self.url+'zones/'+self.zoneid+'/dns_records/'+self.recordid
            print(url)
            answer = UrlRequest.delete(url,headers=self.headers)
            return answer
        raise TypeError('Record id not found')

# class for editing dns records via cloudflare api
authkey='Bearer g54g45ggregGRAEGreag544g5g45g'
zoneid="45t5sg54g54ge5g4yh36h53h35"
cf = CloudflareDNS(authkey=authkey,zoneid=zoneid)

cf.name = 'domain.domain' # dns record
cf.content = '192.168.1.1' # content like IP or TXT info
cf.type = 'A' # dns record type: A,AAAA,TXT...
cf.ttl = 300 # TTL for the dns record
cf.proxied = False # Toggle proxy via cloudflare

cf.send()   # Sends settings to cloudflare
            # Can take 4 arguments: name,type,ttl,content
            # will already assigned variables if left blank

cf.delete() # Deletes dns record
            # Can take 2 arguments: name,type
            # will already assigned variables if left blank

cf.getrecords() # returns json from cloudflare for current record
                # Can take 2 arguments: name,type
                # will already assigned variables if left blank
