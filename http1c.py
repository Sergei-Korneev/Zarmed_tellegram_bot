import config
import requests
from requests.auth import HTTPBasicAuth
from os import getenv

ONEC_USER = getenv("ONEC_USER")
ONEC_PASS = getenv("ONEC_PASS")

def DBRequest (url = ""):
 
    # Use 'with' to ensure the session context is closed after use.
 with requests.Session() as s:
    
  try:
    # An authorised request.
    r = s.get('http://' + config.ONEC_IP + '/' + config.ONEC_DB  + '/hs/' + url,
              timeout=config.HTTP_TIMEOUT,
              auth=HTTPBasicAuth(ONEC_USER.encode('utf-8'), ONEC_PASS))
     
    if r.status_code == 200:
     return [ r.status_code,  r.json(), "" ]
    else: 
     return [ r.status_code, "" , r.text ]
 

  except requests.exceptions.Timeout:
    return [ 1,  "", "Timed out" ]
  except requests.exceptions.ConnectionError:
    return [ 2,  "", "Connection error" ]  
  except Exception:
    return [ 3,  "", "An unknown error has occured." ] 
 

