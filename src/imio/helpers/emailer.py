# -*- coding: utf-8 -*-
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from email.utils import getaddresses
from email.utils import parseaddr
from imio.helpers import _
from imio.pyutils.utils import safe_encode
from past.types import basestring
from plone import api
from Products.MailHost.MailHost import _encode_address_string
from six import iteritems
from smtplib import SMTPException
from unidecode import unidecode
from zope import schema
from zope.component import getMultiAdapter

import csv
import logging
import re
import socket


try:
    from plone.base.utils import safe_text as safe_text
except ImportError:
    from Products.CMFPlone.utils import safe_unicode as safe_text

try:
    from Products.CMFDefault.exceptions import EmailAddressInvalid
    from Products.CMFDefault.utils import checkEmailAddress
except ImportError:
    from Products.CMFPlone.RegistrationTool import checkEmailAddress
    from Products.CMFPlone.RegistrationTool import EmailAddressInvalid


logger = logging.getLogger("imio.helpers")
EMAIL_CHARSET = "utf-8"


def get_email_charset():
    """Character set to use for encoding the email."""
    portal = api.portal.get()
    return portal.getProperty("email_charset", EMAIL_CHARSET)


def get_mail_host(check=False):
    """Get the MailHost object.

    :param check: bool. Check if mailhost configuration is correct.
    :return: MailHost tool
    """
    if check:
        # check mailhost on 'smtp_host' and 'email_from_address'
        portal = api.portal.get()
        ctrl_overview = getMultiAdapter((portal, portal.REQUEST), name="overview-controlpanel")
        if not ctrl_overview.mailhost_warning():
            return api.portal.get_tool("MailHost")
    else:
        return api.portal.get_tool("MailHost")


# MAIN FUNCTIONS


def create_html_email(html, with_plain=True):
    """Returns an email message with an html body and optionally plain body.

    :param html: html body content
    :param with_plain: add plain text version (default=True)
    :return: MIMEMultipart instance
    :rtype: MIMEMultipart
    """
    charset = get_email_charset()
    html = safe_text(html, charset)

    # Don't check possible body content charset ('US-ASCII', get_email_charset(), 'UTF-8')
    body_charset = charset

    html = html.encode("ascii", "xmlcharrefreplace")
    html_part = MIMEText(html, "html", body_charset)

    # doing a multipart message content for text and html
    email_content = MIMEMultipart("alternative")
    email_content.epilogue = ""

    if with_plain:
        portal_transforms = api.portal.get_tool("portal_transforms")
        plain = portal_transforms.convert("html_to_text", html).getData()
        plain = safe_text(plain, charset)
        plain = plain.encode(body_charset, "replace")
        text_part = MIMEText(plain, "plain", body_charset)
        email_content.attach(text_part)

    # the email client will try to render the last part first !
    email_content.attach(html_part)

    # doing a multipart email that can "receive" attachments too
    eml = MIMEMultipart()
    eml.attach(email_content)

    return eml


@api.validation.at_least_one_of("filepath", "content")
def add_attachment(eml, filename, filepath=None, content=None):
    """Adds attachment to email instance.
    Must pass at least filepath or content.

    :param eml: email instance
    :param filename: file name string to store in header
    :param filepath: attachment file disk path
    :param content: attachment binary content
    """
    # Add as application/octet-stream: email client can usually download this automatically as attachment
    part = MIMEBase("application", "octet-stream")
    if filepath:
        # don't check file existence. Exception is preferred
        with open(filepath, "rb") as attachment:
            part.set_payload(attachment.read())
    if content:
        part.set_payload(content)

    encoders.encode_base64(part)
    # filename must be utf8 to be correctly displayed in gmail
    # in gmail with unicode: Content-Disposition: "attachment; filename=\"Réponse candidature ouvrier communal.odt\""
    # in gmail with utf8: Content-Disposition: attachment; filename="Réponse candidature ouvrier communal.odt" => OK
    part.add_header("Content-Disposition", "attachment", filename=safe_encode(filename))
    eml.attach(part)


def send_email(eml, subject, mfrom, mto, mcc=None, mbcc=None, replyto=None, immediate=False):
    """Sends an email with MailHost.

    :param eml: email instance
    :param subject: subject string
    :param mfrom: from string
    :param mto: to string or string list or (name, address) list
    :param mcc: cc string or string list or (name, address) list
    :param mbcc: bcc string or string list or (name, address) list
    :param replyto: reply-to string or string list or (name, address) list
    :param immediate: send email immediately without queuing (default False)
    :return: status
    :rtype: bool
    """
    mail_host = get_mail_host()
    if mail_host is None:
        logger.error("Cannot send email: mail host not well defined.")
        return False, "Mail host not well defined"

    charset = get_email_charset()
    subject = safe_text(subject, charset)
    # Convert all our address list inputs
    addrs = {
        "From": _email_list_to_string(mfrom, charset),
        "To": _email_list_to_string(mto, charset),
        "Cc": _email_list_to_string(mcc, charset),
        "reply-to": _email_list_to_string(replyto, charset),
    }
    mbcc = _email_list_to_string(mbcc, charset)
    # Add extra headers
    _addHeaders(
        eml, Subject=Header(subject, charset), **dict((k, Header(v, charset)) for k, v in iteritems(addrs) if v)
    )
    # Handle all recipients to add bcc: smtplib sends to all but a recipient not found in header is considered as bcc...
    # bug in python 3.10.12 with getaddresses and parameters like ["xx@yy.be", "", ""]
    all_recipients = [
        formataddr(pair) for pair in getaddresses([addr for addr in (addrs["To"], addrs["Cc"], mbcc) if addr])
    ]
    try:
        # send is protected by permission 'Use mailhost'
        # send remove from headers bcc but if in all_recipients, it is handled as bcc in email...
        mail_host.send(eml.as_string(), all_recipients, addrs["From"], immediate=immediate, charset=charset)
    except (socket.error, SMTPException) as e:
        logger.error(u"Cannot send email to '{}' with subject '{}': {}".format(mto, subject, e))
        return False, "Could not send email : {}".format(e)
    # sent successfully
    return True, ""


def _email_list_to_string(addr_list, charset="utf8"):
    """SecureMailHost's secureSend can take a list of email addresses
    in addition to a simple string.  We convert any email input into a
    properly encoded string."""
    if addr_list is None:
        return ""
    if isinstance(addr_list, basestring):
        addr_str = addr_list
    else:
        # if the list item is a string include it, otherwise assume it's a
        # (name, address) tuple and turn it into an RFC compliant string

        addresses = (isinstance(a, basestring) and a or formataddr(a) for a in addr_list)
        addr_str = ", ".join(str(_encode_address_string(a, charset)) for a in addresses)
    return addr_str


def _addHeaders(message, **kwargs):
    for key, value in iteritems(kwargs):
        del message[key]
        message[key] = value


class InvalidEmailAddressFormat(schema.ValidationError):
    """Exception for invalid address format with real name part."""

    __doc__ = _(u"Invalid email address format: 'real name <email>' or 'email (real name)'")


class InvalidEmailAddress(schema.ValidationError):
    """Exception for invalid address.
    `doc` method is used to return a dynamic message with real tested address.
    """

    def __init__(self, eml, *args, **kwargs):
        self.eml = eml

    def doc(self):
        return _(u"Invalid email address: '${eml}'", mapping={"eml": self.eml})


class InvalidEmailAddressCharacters(schema.ValidationError):
    """Exception for invalid realname.
    `doc` method is used to return a dynamic message with real tested address.
    """

    def __init__(self, value, *args, **kwargs):
        self.value = value

    def doc(self):
        return _(u"Realname: '${value}' cannot contain accented or special characters", mapping={"value": self.value})


def validate_email_address(value):
    """Email validator for email address with possible real name part.

    :param value: email value
    :return: tuple containing real name and address
    :rtype: tuple
    """
    if not value:
        return True
    eml = safe_text(value)
    realname = u""
    complex_form = any([b in eml and e in eml for b, e in ("<>", "()")])
    # Use parseaddr only when necessary to avoid correction like 'a @d.c' => 'a@d.c'
    # or to avoid bad split like 'a<a@d.c' => 'a@d.c'
    if complex_form:
        if '""' in eml:  # '"\\"' ends with '""' and must be corrected. We choose to un-double the doublequotes
            eml = re.sub(r'""([^"<]+)""\s*<(.*)>', r'"\1" <\2>', eml)
        realname, eml = parseaddr(eml)
        if not realname and not eml:
            raise InvalidEmailAddressFormat(value)
        if realname != unidecode(realname):
            raise InvalidEmailAddressCharacters(realname)
        # we check if the email has not been corrected by parseaddr, removing some characters like space
        if eml not in value:
            raise InvalidEmailAddress(u"'{}' => '{}' ?".format(value, eml))
    try:
        checkEmailAddress(eml)
    except EmailAddressInvalid:
        raise InvalidEmailAddress(eml)
    return realname, eml.lower()


def validate_email_addresses(value):
    """Email validator for email addresses (with possible real name part) separated by ','.

    :param value: email value
    :return: True
    """
    if not value:
        return True
    ret = []
    # we need to multiply doublequotes, otherwise they are removed by csv
    value = value.replace('"', '"""')
    # split addresses using csv
    for line in csv.reader([safe_encode(value)], delimiter=",", quotechar='"', skipinitialspace=True):
        for eml in line:
            ret.append(validate_email_address(eml))
    return ret
