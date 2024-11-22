from urlrequest import UrlRequest
import json
import time

AccountSid = ''
authkey = ""
query = ""


res = UrlRequest.get(f'https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/AvailablePhoneNumbers/US/Local.json?Contains={query}&PageSize=10000',auth=(AccountSid,authkey),timeout=60)

print(res)
print(res.text)
with open('numbers.txt','a') as numfile:
    numfile.write(res.text)
