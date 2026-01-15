# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import timedelta
from imio.helpers import AUTH_INFOS_ATTR
from imio.helpers import logger
from imio.helpers import SSO_APPS_CLIENT_ID
from imio.helpers import SSO_APPS_CLIENT_SECRET
from imio.helpers import SSO_APPS_URL
from imio.helpers import SSO_APPS_USER_PASSWORD
from imio.helpers import SSO_APPS_USER_USERNAME
from imio.helpers.security import fplog
from persistent.mapping import PersistentMapping
from plone import api
from Products.CMFPlone.utils import safe_unicode
from zope.globalrequest import getRequest

import json
import requests
import urllib


try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse


def get_auth_token(sso_url=SSO_APPS_URL,
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
                'client_secret': sso_client_secret,
                'username': sso_user_username,
                'password': sso_user_password}
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
