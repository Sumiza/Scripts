
from urlrequest import UrlRequest
import os
import base64


headers = {"Authorization":"Bearer github_pat_"}

owner = ''
repo = ''

url = f'https://api.github.com/repos/{owner}/{repo}/contents/'


def uploadfile(file):
    pathlist = os.path.normpath(file).split(os.sep)
    filename = pathlist[len(pathlist)-1]
    filepath = '/'.join(pathlist)

    file64 = None
    with open(filepath,'r',encoding='utf-8') as file:
        a   = base64.b64encode(file.read().encode())
        file64 = a.decode()
    
    shaget = UrlRequest(url+filepath,method='GET',headers=headers).json()
    sha = shaget.get('sha',None)
    
    if sha:
        data = {"message":f"updating {filename}","content":file64,'sha':sha}
    else:
        data = {"message":f"uploading {filename}","content":file64}

    res = UrlRequest(url+filepath,json=data,method='PUT',headers=headers)
    print(res.text,res.status_code)


def recfilelist(path):
    for ff in os.listdir(path):

        if path:
            pathff = os.path.join(path,ff)
        else:
            pathff = ff

        if os.path.isfile(pathff):
            if not os.path.split(__file__)[1] == pathff:
                uploadfile(pathff)

        if os.path.isdir(pathff):
            if not pathff.startswith('_') and not pathff.startswith('.'):
                recfilelist(pathff)

#upload/update all the files to a github repo and subfolders
recfilelist(None)
