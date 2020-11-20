# -*- coding: utf-8 -*-

from imio.helpers.emailer import add_attachment
from imio.helpers.emailer import create_html_email
from imio.helpers.emailer import get_mail_host
from imio.helpers.emailer import send_email
from imio.helpers.testing import IntegrationTestCase

import os


class TestEmail(IntegrationTestCase):

    def setUp(self):
        super(TestEmail, self).setUp()

    def test_create_html_email(self):
        msg = '<h1>Test</h1>\n<p><a href="https://github.com/">Github site</p>'
        eml = create_html_email(msg)
        estr = eml.as_string()
        self.assertIn('Content-Type: multipart/mixed;', estr)
        self.assertIn('Content-Type: multipart/alternative;', estr)
        self.assertIn('Content-Type: text/plain; charset="utf-8"', estr)
        self.assertIn('Test =\n\n  Github site', estr)
        self.assertIn('Content-Type: text/html; charset="utf-8"', estr)
        self.assertIn('<h1>Test</h1>\n<p><a href=3D"https://github.com/">Github site</p>', estr)

    def test_add_attachment(self):
        msg = '<h1>Test</h1>\n<p><a href="https://github.com/">Github site</p>'
        eml = create_html_email(msg)
        path = os.path.dirname(__file__)
        filepath = os.path.join(path, 'barcode.png')
        add_attachment(eml, 'barcode.png', filepath=filepath)
        estr = eml.as_string()
        self.assertIn('Content-Type: multipart/mixed;', estr)
        self.assertIn('Content-Type: multipart/alternative;', estr)
        self.assertIn('Content-Type: text/plain; charset="utf-8"', estr)
        self.assertIn('Test =\n\n  Github site', estr)
        self.assertIn('Content-Type: text/html; charset="utf-8"', estr)
        self.assertIn('<h1>Test</h1>\n<p><a href=3D"https://github.com/">Github site</p>', estr)
        self.assertIn('Content-Type: application/octet-stream', estr)
        self.assertIn('Content-Transfer-Encoding: base64', estr)
        self.assertIn('Content-Disposition: attachment; filename="barcode.png"', estr)

    def test_send_email(self):
        msg = '<h1>Test</h1>\n<p><a href="https://github.com/">Github site</p>'
        eml = create_html_email(msg)
        path = os.path.dirname(__file__)
        filepath = os.path.join(path, 'barcode.png')
        add_attachment(eml, 'barcode.png', filepath=filepath)
        mail_host = get_mail_host()
        sec_send_orig = mail_host.secureSend
        mail_host.secureSend = mail_host.send
        mail_host.reset()
        send_email(eml, 'Email subject hé hé', 'noréply@from.org', 'dèst@to.org')
        self.assertIn('Subject: =?utf-8?q?Email_subject_h=C3=A9_h=C3=A9?=\n', mail_host.messages[0])
        self.assertIn('From: nor\xc3\xa9ply@from.org\n', mail_host.messages[0])
        self.assertIn('To: d\xc3\xa8st@to.org\n', mail_host.messages[0])
        mail_host.reset()
        send_email(eml, u'Email subject', '<noreply@from.org>', ['dest@to.org', 'Stéphan Geulette <seg@to.org>'])
        self.assertIn('To: dest@to.org, =?utf-8?q?St=C3=A9phan_Geulette?= <seg@to.org>\n', mail_host.messages[0])
        mail_host.reset()
        # unicode is ok if singles
        self.assertTrue(send_email(eml, u'Email subject hé hé', u'noréply@from.org', u'dèst@to.org'))
        # not ok if in list
        self.assertRaises(UnicodeEncodeError, send_email, eml, u'Email subject', '<noreply@from.org>', ['dest@to.org', u'Stéphan Geulette <seg@to.org>'])
        mail_host.secureSend = sec_send_orig
