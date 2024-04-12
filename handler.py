import requests
import msal
import logging
from config.config import Config
config= Config()

log=logging.getLogger(__name__)
log.setLevel(logging.INFO)

def post(url,headers,data):
    try:
        response=requests.post(url=url,headers=headers,data=data)
        response.raise_for_status
        return response
    except Exception as e:
        log.error(f"error in Http post request : {e}")

def get_embed_url(report_id):
    try:
        report_id= str(report_id)
        embed_url = f'{config.BASE_URL}?reportId={report_id}&groupId={config.GROUP_ID}'
        return embed_url
    except Exception as e:
        log.error(f"error generating embed url: {e}")


def get_access_token():
    try:
        client = msal.PublicClientApplication(config.APP_ID, authority=config.AUTHORITY_URL)
        response= client.acquire_token_by_username_password(username=config.USERNAME, password=config.PASSWORD, scopes=[config.SCOPE])
        access_token= response.get("access_token")
        log.info(f"get_access_token: {response}")
        return access_token
    except Exception as e:
        log.error(f"error generating access token: {e}")


