from urlrequest import UrlRequest
import json
import time

api_username = ''
api_password = ''

jsonresponse = '&content_type=json'
method = 'getStates'

res = UrlRequest.get(f'https://voip.ms/api/v1/rest.php?api_username={api_username}&api_password={api_password}&method={method}{jsonresponse}')
print(res)
print(res.text)

jstate = json.loads(res.text)
for state in jstate['states']:
    time.sleep(10)
    print(state['state'] + '\n'+'*'*20)

    method = 'searchDIDsUSA'
    state = state['state']
    types = 'ends'
    query = ''
    res = UrlRequest.get(f'https://voip.ms/api/v1/rest.php?api_username={api_username}&api_password={api_password}&method={method}&state={state}&type={types}&query={query}{jsonresponse}',timeout=30)
    print(res.text)
    j = json.loads(res.text)
    try:
        for pdict in j['dids']:
            pnr = pdict['did'][0:3]+'-'+pdict['did'][3:6]+'-'+pdict['did'][6:10]
            print(pnr,pdict['ratecenter'],pdict['state'])
            with open('numbers.txt','a') as numfile:
                numfile.write(f"{pnr},{pdict['ratecenter']},{pdict['state']}\n")
    except:
        print('nothing found')
