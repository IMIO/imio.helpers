# -*- coding: utf-8 -*-

from smtplib import SMTP_SSL
from zope.sendmail.mailer import SMTPMailer

import pkg_resources


try:
    pkg_resources.get_distribution("collective.solr")
except pkg_resources.DistributionNotFound:
    HAS_SOLR = False
else:
    from collective.solr.indexer import SolrIndexProcessor
    HAS_SOLR = True


def solr_index(self, obj, attributes=None):
    # Fix issue https://github.com/collective/collective.solr/issues/189
    if attributes is not None:
        attributes = None
    return SolrIndexProcessor._old_index(self, obj, attributes)


def ssl_makeMailer(self):
    """ Create a SMTPMailer with SMTP_SSL if port is 465 """
    mailer = SMTPMailer(hostname=self.smtp_host, port=int(self.smtp_port), username=self.smtp_uid or None,
                        password=self.smtp_pwd or None, force_tls=self.force_tls)
    if self.smtp_port in (465, '465'):
        mailer.smtp = SMTP_SSL
    return mailer
