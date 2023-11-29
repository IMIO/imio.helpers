# -*- coding: utf-8 -*-

from collective.MockMailHost.MockMailHost import MockMailHost
from imio.helpers.emailer import add_attachment
from imio.helpers.emailer import create_html_email
from imio.helpers.emailer import get_mail_host
from imio.helpers.emailer import InvalidEmailAddress
from imio.helpers.emailer import InvalidEmailAddressCharacters
from imio.helpers.emailer import InvalidEmailAddressFormat
from imio.helpers.emailer import send_email
from imio.helpers.emailer import validate_email_address
from imio.helpers.emailer import validate_email_addresses
from imio.helpers.testing import IntegrationTestCase

import os
import six


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
        if six.PY2:
            self.assertIn('Test =\n\n  Github site', estr)
        elif six.PY3:
            self.assertIn('Test=20\n  Github site', estr)
        self.assertIn('Content-Type: text/html; charset="utf-8"', estr)
        self.assertIn('<h1>Test</h1>\n<p><a href=3D"https://github.com/">Github site</p>', estr)

    def test_add_attachment(self):
        msg = '<h1>Test</h1>\n<p><a href="https://github.com/">Github site</p>'
        eml = create_html_email(msg)
        path = os.path.dirname(__file__)
        if six.PY3:
            barcode_resource = "barcode_python3_zint_60x60_156bytes.png"
        else:
            barcode_resource = "barcode_python2_zint_60x60_278bytes.png"
        filepath = os.path.join(path, barcode_resource)
        add_attachment(eml, 'barcode.png', filepath=filepath)
        estr = eml.as_string()
        self.assertIn('Content-Type: multipart/mixed;', estr)
        self.assertIn('Content-Type: multipart/alternative;', estr)
        self.assertIn('Content-Type: text/plain; charset="utf-8"', estr)
        if six.PY2:
            self.assertIn('Test =\n\n  Github site', estr)
        elif six.PY3:
            self.assertIn('Test=20\n  Github site', estr)
        self.assertIn('Content-Type: text/html; charset="utf-8"', estr)
        self.assertIn('<h1>Test</h1>\n<p><a href=3D"https://github.com/">Github site</p>', estr)
        self.assertIn('Content-Type: application/octet-stream', estr)
        self.assertIn('Content-Transfer-Encoding: base64', estr)
        self.assertIn('Content-Disposition: attachment; filename="barcode.png"', estr)

    def test_send_email(self):
        msg = '<h1>Test</h1>\n<p><a href="https://github.com/">Github site</p>'
        eml = create_html_email(msg)
        path = os.path.dirname(__file__)
        if six.PY3:
            barcode_resource = "barcode_python3_zint_60x60_156bytes.png"
        else:
            barcode_resource = "barcode_python2_zint_60x60_278bytes.png"
        filepath = os.path.join(path, barcode_resource)
        add_attachment(eml, 'barcode.png', filepath=filepath)
        mail_host = get_mail_host()
        MockMailHost.secureSend = MockMailHost.send
        mail_host.reset()
        if six.PY3:
            # Python 3 raises an error with accented characters in emails
            # see https://github.com/zopefoundation/Products.MailHost/issues/29
            # and https://stackoverflow.com/questions/52133735/how-do-i-send-email-to-addresses-with-non-ascii-characters-in-python
            send_email(eml, 'Email subject hé hé', 'noreply@from.org', 'dest@to.org')
            self.assertIn(b'Subject: =?utf-8?q?Email_subject_h=C3=A9_h=C3=A9?=\n', mail_host.messages[0])
            self.assertIn(b'From: noreply@from.org\n', mail_host.messages[0])
            self.assertIn(b'To: dest@to.org\n', mail_host.messages[0])
        else:
            send_email(eml, 'Email subject hé hé', 'noréply@from.org', 'dèst@to.org')
            self.assertIn('Subject: =?utf-8?q?Email_subject_h=C3=A9_h=C3=A9?=\n', mail_host.messages[0])
            self.assertIn('From: nor\xc3\xa9ply@from.org\n', mail_host.messages[0])
            self.assertIn('To: d\xc3\xa8st@to.org\n', mail_host.messages[0])
        mail_host.reset()
        send_email(eml, u'Email subject', '<noreply@from.org>', ['dest@to.org', 'Stéphan Geulette <seg@to.org>'])
        if six.PY3:
            self.assertIn(b'To: dest@to.org, =?utf-8?q?St=C3=A9phan_Geulette?= <seg@to.org>\n', mail_host.messages[0])
        else:
            self.assertIn('To: dest@to.org, =?utf-8?q?St=C3=A9phan_Geulette?= <seg@to.org>\n', mail_host.messages[0])
        mail_host.reset()
        if six.PY3:
            self.assertTrue(send_email(eml, u'Email subject hé hé', u'noreply@from.org', u'dest@to.org'))
            self.assertTrue(send_email(eml, u'Email subject', '<noreply@from.org>',
                                       ['dest@to.org', u'Stéphan Geulette <seg@to.org>']))
        else:
            # unicode is ok if singles
            self.assertTrue(send_email(eml, u'Email subject hé hé', u'noréply@from.org', u'dèst@to.org'))
            # not ok if in list
            self.assertRaises(UnicodeEncodeError, send_email, eml, u'Email subject', '<noreply@from.org>',
                              ['dest@to.org', u'Stéphan Geulette <seg@to.org>'])

    def test_validate_email_address(self):
        self.assertTupleEqual(validate_email_address('name@domain.org'), (u'', u'name@domain.org'))
        self.assertTupleEqual(validate_email_address(u'name@domain.org'), (u'', u'name@domain.org'))
        self.assertTupleEqual(validate_email_address('"Real Name" <name@domain.org>'),
                              (u'Real Name', u'name@domain.org'))
        self.assertTupleEqual(validate_email_address('Real Name <name@domain.org>'),
                              (u'Real Name', u'name@domain.org'))
        self.assertTupleEqual(validate_email_address('name@domain.org (Real Name)'),
                              (u'Real Name', u'name@domain.org'))
        # errors on format
        self.assertRaises(InvalidEmailAddressFormat, validate_email_address, '<>')
        self.assertRaises(InvalidEmailAddressFormat, validate_email_address, '()')
        self.assertRaises(InvalidEmailAddressFormat, validate_email_address, '<,name@domain.org>')
        self.assertRaises(InvalidEmailAddressFormat, validate_email_address, '(name@domain.org)')
        # errors on email
        self.assertRaises(InvalidEmailAddress, validate_email_address, '[name@domain.org]')
        self.assertRaises(InvalidEmailAddress, validate_email_address, ',name@domain.org')
        self.assertRaises(InvalidEmailAddress, validate_email_address, 'Real Name <na me@domain.org>')
        self.assertRaises(InvalidEmailAddress, validate_email_address, 'na me@domain.org')
        self.assertRaises(InvalidEmailAddress, validate_email_address, 'name|domain.org')
        self.assertRaises(InvalidEmailAddress, validate_email_address, 'name@domainorg')
        self.assertRaises(InvalidEmailAddress, validate_email_address, 'na<me@domain.org')
        self.assertRaises(InvalidEmailAddress, validate_email_address, 'name@domain.or(g')
        self.assertRaises(InvalidEmailAddress, validate_email_address, 'name@domain.or)g')
        # errors on realname
        self.assertRaises(InvalidEmailAddressCharacters, validate_email_address, 'Stéphan <stephan@domain.org>')

    def test_validate_email_addresses(self):
        self.assertListEqual(validate_email_addresses('name@domain.org'), [(u'', u'name@domain.org')])
        self.assertListEqual(validate_email_addresses(u'name@domain.org'), [(u'', u'name@domain.org')])
        self.assertListEqual(validate_email_addresses('"Real Name" <name@domain.org>'),
                             [(u'Real Name', u'name@domain.org')])
        self.assertListEqual(validate_email_addresses('Real Name <name@domain.org>'),
                             [(u'Real Name', u'name@domain.org')])
        self.assertListEqual(validate_email_addresses('name@domain.org (Real Name)'),
                             [(u'Real Name', u'name@domain.org')])
        self.assertListEqual(validate_email_addresses('name1@domain.org, name2@domain.org'),
                             [(u'', u'name1@domain.org'), (u'', u'name2@domain.org')])
        self.assertListEqual(validate_email_addresses('Real Name <name1@domain.org>, name2@domain.org'),
                             [(u'Real Name', u'name1@domain.org'), (u'', u'name2@domain.org')])
        self.assertListEqual(validate_email_addresses('Real Name <name1@domain.org>, "Other Name" <name2@domain.org>'),
                             [(u'Real Name', u'name1@domain.org'), (u'Other Name', u'name2@domain.org')])
        self.assertListEqual(validate_email_addresses('"Real, Name" <name@domain.org>'),
                             [(u'Real, Name', u'name@domain.org')])
        self.assertListEqual(validate_email_addresses('"Real, Name" <name1@domain.org>, '
                                                      '"Other, Name" <name2@domain.org>'),
                             [(u'Real, Name', u'name1@domain.org'), (u'Other, Name', u'name2@domain.org')])
        # errors on format
        self.assertRaises(InvalidEmailAddressFormat, validate_email_addresses, '<>')
        self.assertRaises(InvalidEmailAddressFormat, validate_email_addresses, '()')
        self.assertRaises(InvalidEmailAddressFormat, validate_email_addresses, '(name@domain.org)')
        # errors on email
        self.assertRaises(InvalidEmailAddress, validate_email_addresses, '[name@domain.org]')
        self.assertRaises(InvalidEmailAddress, validate_email_addresses, 'Real Name <na me@domain.org>')
        self.assertRaises(InvalidEmailAddress, validate_email_addresses, 'na me@domain.org')
        self.assertRaises(InvalidEmailAddress, validate_email_addresses, 'Real, Name <name@domain.org>')
        self.assertRaises(InvalidEmailAddress, validate_email_addresses, 'name|domain.org')
        self.assertRaises(InvalidEmailAddress, validate_email_addresses, 'name@domainorg')
        self.assertRaises(InvalidEmailAddress, validate_email_addresses, 'na<me@domain.org')
        self.assertRaises(InvalidEmailAddress, validate_email_addresses, 'name@domain.or(g')
        self.assertRaises(InvalidEmailAddress, validate_email_addresses, 'name@domain.or)g')
        # errors on realname
        self.assertRaises(InvalidEmailAddressCharacters, validate_email_addresses, 'Stéphan <stephan@domain.org>')
