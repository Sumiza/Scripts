"""
    wrapper for urllib.request.urlopen
    very limited drop-in replacement for requests when cant import requests
    and need to use the built in urllib.request library
"""
class UrlRequest:
    """
        urllib.request in a class to make it easier to use
    """
    def __init__(self,
                url:str,
                data:str = "",
                json = None,
                method:str = 'GET',
                headers:dict = None,
                timeout:float = 10,
                auth:tuple = None):

        # importing here to keep it all contained
        # so can copy and paste this code into other scripts
        # pylint: disable=import-outside-toplevel
        import urllib.request
        import urllib.error
        import json as jsonclass

        if headers is None: # python quirk with default mutables
            headers = {}

        if not headers.get('User-Agent'): # writes in a user agent if not there
            headers['User-Agent'] = 'UrlRequest'

        if auth: # Basic Auth
            authhandle = urllib.request.HTTPPasswordMgrWithPriorAuth()
            authhandle.add_password(None, url, auth[0], auth[1],is_authenticated=True)
            opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(authhandle))
            urllib.request.install_opener(opener)

        if json: # json formatting and adding header
            headers['content-type'] = 'application/json, charset=utf-8'
            data = jsonclass.dumps(json)

        data = data.encode('utf-8',errors='ignore')
        req = urllib.request.Request(url,data=data,method=method,headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=timeout) as request:
                self.text = request.read().decode('utf-8',errors='backslashreplace')
                self.status_code = request.status
                self.headers = dict(request.headers)
                try:
                    self.json = jsonclass.loads(self.text)
                except jsonclass.JSONDecodeError:
                    self.json = {"error":"No JSON returned"}

        except urllib.error.HTTPError as exception:
            self.text = exception.reason
            self.status_code = exception.code
            self.headers = dict(exception.headers)
            self.json = {"error":f'{exception.reason}'}

        # catches connection errors
        # comment out if you want to catch them yourself
        except urllib.error.URLError as exception:
            self.text = exception.reason
            self.status_code = 483 # unused code
            self.headers = {}
            self.json = {"error":f'{exception.reason}'}

    def __str__(self):
        return str(self.status_code)

    # next part is for drop-in replacement for requests
    # doesnt really do anything else
    # pylint: disable=no-self-argument,no-method-argument,missing-function-docstring
    def get(*args,**kwargs):
        return UrlRequest(*args,**kwargs,method='GET')
    def post(*args,**kwargs):
        return UrlRequest(*args,**kwargs,method='POST')
    def put(*args,**kwargs):
        return UrlRequest(*args,**kwargs,method='PUT')
    def delete(*args,**kwargs):
        return UrlRequest(*args,**kwargs,method='DELETE')
    def head(*args,**kwargs):
        return UrlRequest(*args,**kwargs,method='HEAD')
    def patch(*args,**kwargs):
        return UrlRequest(*args,**kwargs,method='PATCH')

if __name__ == '__main__':
    a = UrlRequest('https://httpbin.org/ip')
    print(a.text)
    print(a.status_code)
    print(a.headers)
    print(a.json)
    a = UrlRequest("https://httpbin.org/basic-auth/user/password",auth=('user','password'))
    print(a.text)
    a = UrlRequest("https://httpbin.org/post",method="POST",json={"hello":"world"})
    print(a.text)
    #drop in for requests
    a = UrlRequest.get("https://httpbin.org/headers",headers={"hello":"world header test"})
    print(a.text)
