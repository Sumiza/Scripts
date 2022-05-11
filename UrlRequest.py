
class UrlRequest:
    """
        Putting urllib.request in a class to make it easier to use
    """
    def __init__(self,
                url:str,
                data:str = "",
                json = None,
                method:str = 'GET',
                headers:dict = {},
                timeout:float = 10,
                auth:tuple = None):

        # imporing here to keep it all contained
        import urllib.request
        import urllib.error

        if not headers.get('User-Agent'): # writes in a user agent if not there
            headers['User-Agent'] = 'UrlRequest'
        if auth: # Basic Auth
            authhandle = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            authhandle.add_password(None, url, auth[0], auth[1])
            opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(authhandle))
            urllib.request.install_opener(opener)
        if json: # json formatting and adding header
            import json as jencode
            headers['content-type'] = 'application/json, charset=utf-8'
            data = jencode.dumps(json)
        data = data.encode('utf-8',errors='ignore')
        req = urllib.request.Request(url,data=data,method=method,headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as request:
                self.text = request.read().decode('utf-8',errors='backslashreplace')
                self.status = request.status
                self.headers = request.headers
        except urllib.error.HTTPError as exception:
            self.text = exception.reason
            self.status = exception.code
            self.headers = exception.headers
        except urllib.error.URLError as exception:
            self.text = exception.reason
            self.status = 400
            self.headers = ""




a = UrlRequest('https://httpbin.org/basic-auth/foo/bar', auth=('foo','bar'))
print(a.text)
print(a.status)
a = UrlRequest('https://httpbin.org/ip')
print(a.text)
print(a.status)
