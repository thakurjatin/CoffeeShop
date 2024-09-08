import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'fsdndp.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'https://coffeeshop-api/v1'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():

    get_header = request.headers.get("Authorization", None)

    if not get_header:
        raise AuthError({"code": "Auth_value_is_invalid_or_not_available",
                         "description":
                         "Value of Auth header is mendatory"}, 401)

    get_header_parameters = get_header.split(' ')

    if len(get_header_parameters) != 2 or not get_header_parameters:
        raise AuthError({
            'code': 'header_notvalid',
            'description': 'format is mendatory for Auth header'
            ' Bearer token'}, 401)

    elif get_header_parameters[0].lower() != 'bearer':
        raise AuthError({
            'code': 'header_notvalid',
            'description': 'format is mendatory for Auth header should start with bearer'}, 401)

    return get_header_parameters[1]


'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    if 'permissions' not in payload:
        abort(400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized user trying to access application',
            'description': 'User dont have permission to access',
        }, 401)
    return True

'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):

    urlValue = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')

    jwjson = json.loads(urlValue.read())

    unchecked = jwt.get_unverified_header(token)

    if 'kid' not in unchecked:
        raise AuthError({
            'code': 'Not Valid',
            'description': 'Auth token is not valid or not formed properly'
        }, 401)

    check_ky = {}

    for clue in jwjson['keys']:
        if clue['kid'] == unchecked['kid']:
            check_ky = {
                'kty': clue['kty'],
                'kid': clue['kid'],
                'use': clue['use'],
                'n': clue['n'],
                'e': clue['e']
            }
            break

    if check_ky:
        try:
            payload = jwt.decode(
                token,
                check_ky,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f'https://{AUTH0_DOMAIN}/'
            )
            return payload

        except jwt.JWTClaimsError:

            raise AuthError({
                'code': 'claim is not valid',
                'description': 'claim is not valid please check with owner or use correct credentials '
            }, 401)

        except Exception:

            raise AuthError({
                'code': 'incorrect header value issue with token or payload',
                'description': ' issue with token or payload'
            }, 400)




'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator