from urlrequest import UrlRequest
import json

header = {'Authorization': 'Bearer '}
query = ''
res = UrlRequest(f'https://api.telnyx.com/v2/available_phone_numbers?filter[phone_number][ends_with]={query}&filter[country_code]=US&filter[phone_number_type]=local&filter[limit]=500&filter[best_effort]=true&filter[reservable]=true',headers=header)
print(res)

for numset in json.loads(res.text)['data']:
    print(numset['phone_number'],numset['region_information'][1]['region_name'],numset['region_information'][3]['region_name'])
    with open('telnyx.txt','a') as telfile:
        telfile.write(f"{numset['phone_number']},{numset['region_information'][1]['region_name']},{numset['region_information'][3]['region_name']}\n")
