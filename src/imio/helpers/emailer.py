# -*- coding: utf-8 -*-

from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from plone import api
from Products.CMFPlone.utils import safe_unicode
from smtplib import SMTPException
from zope.component import getMultiAdapter

import logging
import socket

logger = logging.getLogger("imio.helpers")
EMAIL_CHARSET = 'utf-8'


def get_email_charset():
    """ Character set to use for encoding the email. """
    portal = api.portal.get()
    return portal.getProperty('email_charset', EMAIL_CHARSET)


def get_mail_host(check=False):
    """ Get the MailHost object. """
    if check:
        # check mailhost on 'smtp_host' and 'email_from_address'
        portal = api.portal.get()
        ctrl_overview = getMultiAdapter((portal, portal.REQUEST), name='overview-controlpanel')
        if not ctrl_overview.mailhost_warning():
            return api.portal.get_tool('MailHost')
    else:
        return api.portal.get_tool('MailHost')

# MAIN FUNCTIONS


def create_html_email(html, with_plain=True):
    """ Returns an email message with an html body and optionally plain body
    :param html: html body content
    :param with_plain: add plain text version (default=True)
    :return: MIMEMultipart instance
    """
    charset = get_email_charset()
    html = safe_unicode(html, charset)

    # Don't check possible body content charset ('US-ASCII', get_email_charset(), 'UTF-8')
    body_charset = charset

    html = html.encode(body_charset, 'xmlcharrefreplace')
    html_part = MIMEText(html, 'html', body_charset)

    # doing a multipart message content for text and html
    email_content = MIMEMultipart('alternative')
    email_content.epilogue = ''

    if with_plain:
        portal_transforms = api.portal.get_tool('portal_transforms')
        plain = portal_transforms.convert('html_to_text', html).getData()
        plain = safe_unicode(plain, charset)
        plain = plain.encode(body_charset, 'replace')
        text_part = MIMEText(plain, 'plain', body_charset)
        email_content.attach(text_part)

    # the email client will try to render the last part first !
    email_content.attach(html_part)

    # doing a multipart email that can "receive" attachments too
    eml = MIMEMultipart()
    eml.attach(email_content)

    return eml


@api.validation.at_least_one_of('filepath', 'content')
def add_attachment(eml, filename, filepath=None, content=None):
    """ Adds attachment to email instance
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
    part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(filename))
    eml.attach(part)


def send_email(eml, subject, mfrom, mto, mcc=None, mbcc=None):
    """ Sends an email with MailHost.
    :param eml: email instance
    :param subject: subject string
    :param mfrom: from string
    :param mto: to string or string list
    :param mcc: cc string or string list
    :param mbcc: bcc string or string list
    :return: boolean status
    """
    mail_host = get_mail_host()
    if mail_host is None:
        logger.error('Could not send email: mail host not well defined.')
        return False

    charset = get_email_charset()
    subject = safe_unicode(subject, charset)
    kwargs = {}
    # put only as parameter id defined, so mockmailhost can be used in tests with secureSend as send patch
    if mcc is not None:
        kwargs['mcc'] = mcc
    if mbcc is not None:
        kwargs['mbcc'] = mbcc
    try:
        # secureSend is protected by permission 'Use mailhost'
        # secureSend is deprecated and patched in Products/CMFPlone/patches/securemailhost.py
        # send remove from headers bcc !!
        mail_host.secureSend(eml, mto, mfrom, subject=subject, charset=charset, **kwargs)
    except (socket.error, SMTPException):
        logger.error('Could not send email to %s with subject %s', mto, subject)
        return False
    except Exception:
        raise
    # sent successfully
    return True
