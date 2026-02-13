# -*- coding: utf-8 -*-

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from datetime import datetime
from datetime import timedelta
from imio.helpers import AUTH_INFOS_ATTR
from imio.helpers import logger
from imio.helpers import SSO_APPS_ALGORITHM
from imio.helpers import SSO_APPS_AUDIENCE
from imio.helpers import SSO_APPS_CERTS_URL
from imio.helpers import SSO_APPS_CLIENT_ID
from imio.helpers import SSO_APPS_CLIENT_SECRET
from imio.helpers import SSO_APPS_REALM_URL
from imio.helpers import SSO_APPS_TOKEN_URL
from imio.helpers import SSO_APPS_USER_PASSWORD
from imio.helpers import SSO_APPS_USER_USERNAME
from imio.helpers.security import fplog
from jwt.exceptions import DecodeError
from persistent.mapping import PersistentMapping
from plone import api
from Products.CMFPlone.utils import safe_unicode
from zope.globalrequest import getRequest

import json
import jwt
import requests
import textwrap
import urllib


try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse


def get_auth_token(sso_url=SSO_APPS_TOKEN_URL,
                   sso_client_id=SSO_APPS_CLIENT_ID,
                   sso_client_secret=SSO_APPS_CLIENT_SECRET,
                   sso_user_username=SSO_APPS_USER_USERNAME,
                   sso_user_password=SSO_APPS_USER_PASSWORD,
                   expire_treshold=60,
                   headers={"Content-Type": "application/x-www-form-urlencoded",
                            "Cookie": "KEYCLOAK_LOCALE=fr"},
                   log=True):
    """Get the auth token and store it on the portal.
       Get it again if expired or expires in less than
       given expire_treshold seconds."""
    portal = api.portal.get()
    auth_infos = getattr(portal, AUTH_INFOS_ATTR, PersistentMapping())
    if not auth_infos or auth_infos['expires_in'] < datetime.now():
        if log is True:
            start = datetime.now()
        # first try with "refresh_token" if available
        result = None
        data = {'client_id': sso_client_id,
                'client_secret': sso_client_secret}
        if auth_infos.get('refresh_token', None):
            if log is True:
                logger.info('Getting authentication token from "refresh_token"')
            data['grant_type'] = "refresh_token"
            data['refresh_token'] = auth_infos['refresh_token']
            result = requests.post(
                sso_url, data, headers=headers)
        # may occur if very first request or "refresh_token" expired/invalid
        # in this case we get new full authentication token
        if not result or result.status_code != 200:
            data['grant_type'] = "password"
            data.pop('refresh_token', None)
            # username/password is not necessary for "refresh_token"
            data['username'] = sso_user_username
            data['password'] = sso_user_password
            if log is True:
                logger.info('Getting new authentication token')
            result = requests.post(
                sso_url, data, headers=headers)
        if log is True:
            logger.info(datetime.now() - start)
        if result.status_code == 200:
            result = json.loads(result.content)
            auth_infos['access_token'] = result['access_token']
            auth_infos['refresh_token'] = result.get('refresh_token', None)
            # store that expires_in is 60 seconds before real expires_in
            # so we may probably execute one last request
            auth_infos['expires_in'] = datetime.now() + \
                timedelta(seconds=result['expires_in'] - expire_treshold)
            setattr(portal, AUTH_INFOS_ATTR, auth_infos)
        elif log is True:
            logger.info(
                'Could not get authentication token: status={0}, content={1}'.format(
                    result.status_code, result.content))

    # logger.info(auth_infos['access_token'])
    return auth_infos.get('access_token') or result


def send_json_request(
        url,
        extra_parameters={},
        extra_headers={},
        method='GET',
        data={},
        return_as_raw=False,
        show_message=False,
        **kwargs):
    """Send a json request and returns decoded response."""
    token = get_auth_token()
    # error getting token?
    if isinstance(token, requests.Response):
        return token
    headers = {
        'Accept': 'application/json',
        'Cache-Control': 'no-store',
        'Pragma': 'no-cache',
        'expires': 'Mon, 26 Jul 1997 05:00:00 GMT',
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': "Bearer %s" % token,
    }
    headers.update(extra_headers)
    # prepare url to call, manage extra_parameters
    if extra_parameters:
        if "?" not in url:
            url = url + "?"
        extra_parameters = "&" + urllib.urlencode(extra_parameters)
        url += extra_parameters

    target = urlparse(url)
    url = target.geturl()
    # manage cache per request for 'GET'
    content = None
    extras = 'method={0} url={1}'.format(method, url)
    if method == 'GET':
        request = getRequest()
        cachekey_id = "send_json_request_cachekey"
        cache = getattr(request, cachekey_id, {})
        cachekey = "%s__%s" % (url, method)
        content = cache.get(cachekey, None)
        if content is not None:
            fplog('cached_json_call', extras=extras)
    if content is None:
        fplog('execute_json_call', extras=extras)
        start = datetime.now()
        me = {
            "GET": requests.get,
            "POST": requests.post,
            "PUT": requests.put,
            "DELETE": requests.delete}.get(method)
        response = me(url, headers=headers, json=data, **kwargs)
        content = response.content
        logger.info(datetime.now() - start)
        if response.status_code >= 300:
            logger.warn(content)
            if show_message:
                api.portal.show_message(safe_unicode(content), request=getRequest())
            return response
        # manage cache per request for 'GET'
        if method == 'GET':
            cache[cachekey] = content
            setattr(request, cachekey_id, cache)
    if content and not return_as_raw:
        return json.loads(content)
    else:
        return content


def verify_auth_token(token,
                      sso_certs_url=SSO_APPS_CERTS_URL,
                      sso_algorithm=SSO_APPS_ALGORITHM,
                      sso_audience=SSO_APPS_AUDIENCE,
                      issuer=SSO_APPS_REALM_URL,
                      groups=None,
                      log=True):
    """Verify given jwt token.

    :param token: the jwt token to verify
    :param sso_realm_url: Keycloak URL in the form 'https://<keycloak-server>/realms/<realm-name>'
    :param sso_certs_url: the url to get the sso certs, e.g. 'https://<keycloak-server>/realms/<realm-name>/protocol/openid-connect/certs'
    :param sso_algorithm: the sso algorithm used, e.g. 'RS256'
    :param sso_audience: the expected audience in the token, e.g. 'account'
    :param groups: list of groups the token must contain
    :param log: whether to log verification steps
    :return: True if the token is valid and contains the required groups, False otherwise
    """
    certs = requests.get(sso_certs_url).json()
    x5c_certs = {}
    for cert in certs['keys']:
        alg = cert['alg']
        x5c_certs[alg] = cert['x5c'][0]
    x5c_cert = x5c_certs.get(sso_algorithm, '')
    cert_pem = "-----BEGIN CERTIFICATE-----\n{}\n-----END CERTIFICATE-----".format(
        "\n".join(textwrap.wrap(x5c_cert, 64))
    )
    cert = x509.load_pem_x509_certificate(
        cert_pem.encode('ascii'),
        default_backend()
    )

    public_key = cert.public_key()

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    try:
        decoded = jwt.decode(
            token,
            public_key_pem,
            algorithms=[sso_algorithm],
            audience=sso_audience,
            issuer=issuer,
        )
    except DecodeError:
        return False

    if groups:
        user_groups = decoded.get('groups', [])
        for group in groups:
            if group not in user_groups:
                if log is True:
                    logger.warning('Token verification failed: missing group "%s"', group)
                return False
    return True
