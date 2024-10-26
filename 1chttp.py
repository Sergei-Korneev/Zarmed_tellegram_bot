import config
import requests
from requests.auth import HTTPBasicAuth


# Fill in your details here to be posted to the login form.
payload = {
    'username': 'Сергей',
    'password': ''
}

# Use 'with' to ensure the session context is closed after use.
with requests.Session() as s:
    #p = s.post('http://192.168.122.133/zarmed/hs/test1/test', data=payload)
    # print the HTML returned or something more intelligent to see if it's a successful login page.
#    print(p.text)
 try:
        # An authorised request.
    r = s.get('http://192.168.122.133/zarmed/hs/client/getApp?userid=45465464&ucode=78787',timeout=config.HTTP_TIMEOUT, auth=HTTPBasicAuth(config.ONEC_USER.encode('utf-8'), config.ONEC_PASS))
    #print(s.request)
    #print(r.json())
    print(r.text)
    
    print(r.status_code)

 except requests.exceptions.Timeout:
    print("Timed out")
 except Exception:
    print('An error has occured.')
 
