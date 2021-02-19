r'''
CyVerse integration
===================

Getting OAuth2 keys and secrets
-------------------------------

Use the Agave API to create a new OAuth2 client (server to you, client
to them) and set ``callbackUrl`` appropriately::

    curl -sku "<your cyverse username>:<your cyverse password>" \
        -X POST -d clientName=exao_dap_dev \
        -d "tier=Unlimited" \
        -d "description=ExAO-DAP dev client" \
        -d "callbackUrl=http://localhost:8000/complete/cyverse-oauth2/" \
        'https://agave.iplantc.org/clients/v2/?pretty=true'

which will hopefully produce a response like the following::

    {
        "status": "success",
        "message": "Client created successfully.",
        "version": "2.0.0-SNAPSHOT-rc3fad",
        "result": {
            "description": "ExAO-DAP dev client",
            "name": "exao_dap_dev",
            "consumerKey": "abcd1234",
            "_links": {
                "subscriber": {
                    "href": "https://agave.iplantc.org/profiles/v2/josephlong"
                },
                "self": {
                    "href": "https://agave.iplantc.org/clients/v2/exao_dap_dev"
                },
                "subscriptions": {
                    "href": "https://agave.iplantc.org/clients/v2/exao_dap_dev/subscriptions/"
                }
            },
            "tier": "Unlimited",
            "consumerSecret": "abcd1234",
            "callbackUrl": "http://localhost:8000/complete/cyverse-oauth2/"
        }
    }

``consumerKey`` becomes ``settings.SOCIAL_AUTH_CYVERSE_OAUTH2_KEY`` and
``consumerSecret`` becomes ``settings.SOCIAL_AUTH_CYVERSE_OAUTH2_SECRET``

'''
from social_core.backends.oauth import BaseOAuth2
import fsspec
import irods_fsspec
irods_fsspec.register()
from django.conf import settings
from urllib.parse import urlparse
from irods.session import iRODSSession
# from irods.models import Collection, CollectionAccess, CollectionUser, User
# IRODS_ACCESS_TYPE_OWN = 1200
# IRODS_ACCESS_TYPE_MODIFY = 1120
# IRODS_ACCESS_TYPE_READ = 1050
import threading
_LOCAL = threading.local()
# IRODS_PORT = 1247


# def irods_config_from_url(url):
#     result = urlparse(url)
#     if result.username is not None:
#         try:
#             user, zone = result.username.split('+')
#         except ValueError:
#             user = result.username
#             zone = None
#     else:
#         user = None
#         zone = None
#     return {
#         'user': user,
#         'zone': zone,
#         'password': result.password,
#         'host': result.hostname,
#         'port': result.port if result.port is not None else IRODS_PORT,
#     }
from urllib.parse import urlparse
IRODS_HOME = urlparse(settings.IRODS_URL).path

def irods_get_session():
    if not hasattr(_LOCAL, 'session'):
        config = irods_fsspec.irods_config_from_url(settings.IRODS_URL)
        session = iRODSSession(**config)
        _LOCAL.session = session
    return _LOCAL.session

def irods_get_fs():
    if not hasattr(_LOCAL, 'irodsfs'):
        session = irods_get_session()
        fs = fsspec.filesystem('irods', session=session)
        _LOCAL.irodsfs = fs
    return _LOCAL.irodsfs

def irods_check_access(path):
    fs = irods_get_fs()
    return fs.exists(path)
    

class CyVerseOAuth2(BaseOAuth2):
    """CyVerse OAuth authentication backend"""
    name = 'cyverse-oauth2'
    ID_KEY = 'username'
    AUTHORIZATION_URL = 'https://agave.iplantc.org/authorize'
    ACCESS_TOKEN_URL = 'https://agave.iplantc.org/token'
    # redirect should go to http(s)://.../complete/cyverse-oauth2/
    ACCESS_TOKEN_METHOD = 'POST'
    # packing token into redirect gives "invalid_callback: Registered
    # callback does not match with the provided url." so disable:
    REDIRECT_STATE = False

    SCOPE_SEPARATOR = ','
    DEFAULT_SCOPE = ['PRODUCTION']
    EXTRA_DATA = [
        ('id', 'id'),
        ('expires', 'expires')
    ]

    def get_user_id(self, details, response):
        return response['result']['username']

    def get_user_details(self, response):
        """Return user details from CyVerse account"""
        result = response['result']
        return {
            'username': result['username'],
            'email': result['email'],
            'fullname': result['full_name'],
            'first_name': result['first_name'],
            'last_name': result['last_name'],
        }

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        url = 'https://agave.iplantc.org/profiles/v2/me'
        return self.get_json(url, headers={'Authorization': f'Bearer {access_token}'})
