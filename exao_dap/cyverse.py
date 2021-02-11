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
