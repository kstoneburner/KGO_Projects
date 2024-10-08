# Authentication in Requests with HTTPBasicAuth
import requests
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth1Session
auth = HTTPBasicAuth('default', 'winplus')

TARGET = "172.24.124.148"
PORT = 8080

headers = { 
	"Character encoding" : "UTF-8",
	"Data format" : "JSON"
	}

#print(requests.get('172.24.124.148:8080', auth=auth))
#print(requests.get('http://172.24.124.148:8080', headers=headers, auth=auth))


#endpoint = "url to the API"
#http_headers = {'Authorization': 'Bearer ' + result['access_token'],
#                'Accept': 'application/json',
#                'Content-Type': 'application/json'}
#data = requests.get(endpoint, headers=http_headers, stream=False).json()


#print(code)
parameters = {
    "code": "code",
    "client_id": "default",
    "client_secret": "winplus",
    "redirect_uri": 'http://172.24.124.148:8080/api/v1/sysdevices',
    "response_type": "code",
    "grant_type": "authorization_code"
}

parameters = {
    "username": "default",
    "password": "winplus",
    "grant_type": "password"
}

#response = requests.post('http://172.24.124.148:8080/token', headers=headers, params = parameters)
#print(response)
#access_token = response["access_token"]

#>>> from requests_oauthlib import OAuth1Session
#>>> twitter = OAuth1Session('client_key',
#                            client_secret='client_secret',
#                            resource_owner_key='resource_owner_key',
#                            resource_owner_secret='resource_owner_secret')
#url = 'https://api.twitter.com/1/account/settings.json'
#r = twitter.get(url)

url = 'https://172.24.124.148:8080/Token'

prompter = OAuth1Session('client_key',
                            client_secret='default',
                            resource_owner_key='resource_owner_key',
                            resource_owner_secret='winplus')

import logging
import http.client as http_client

http_client.HTTPConnection.debuglevel = 1

logging.basicConfig() 
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


client_id = "1234"
client_secret = "1234"
username = 'default'
password = 'winplus'

from oauthlib.oauth2 import LegacyApplicationClient

from requests_oauthlib import OAuth2Session

oauth = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))

token = oauth.fetch_token(token_url=url,
        username=username, password=password, client_id=client_id,
        client_secret=client_secret)