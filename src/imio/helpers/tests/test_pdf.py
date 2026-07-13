# -*- coding: utf-8 -*-


from imio.helpers.pdf import merge_pdf
from io import BytesIO
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
from reportlab.pdfgen import canvas

import re
import unittest


def _make_pdf(n_pages=2):
    """Create a simple PDF with n_pages pages using reportlab."""
    buf = BytesIO()
    c = canvas.Canvas(buf)
    for i in range(n_pages):
        c.drawString(100, 750, "Page %d" % (i + 1))
        c.showPage()
    c.save()
    return buf.getvalue()


def _pdf_page_count(pdf_data):
    """Return the number of pages in pdf_data using PyPDF2."""
    return len(PdfReader(BytesIO(pdf_data)).pages)


class TestPdf(unittest.TestCase):
    def test_merge_pdf(self):
        # merge_pdf merges multiple PDFs producing combined page count
        pdf_2p = _make_pdf(2)
        pdf_3p = _make_pdf(3)
        result = merge_pdf(pdf_2p, pdf_2p)
        self.assertEqual(_pdf_page_count(result), 4)
        result = merge_pdf(pdf_2p, pdf_3p, pdf_2p)
        self.assertEqual(_pdf_page_count(result), 7)

        # merge_pdf raises an exception when given invalid PDF data
        self.assertRaises(PdfReadError, merge_pdf, b"not a pdf", b"not a pdf")

    def test_merge_pdf_recovers_missing_root(self):
        # a source PDF whose trailer lacks /Root must not break the merge
        no_root = re.sub(b"/Root\\s+\\d+\\s+\\d+\\s+R", b"", _make_pdf(1), count=1)
        self.assertRaises(KeyError, _pdf_page_count, no_root)  # confirms the fixture
        result = merge_pdf(no_root, _make_pdf(2))
        self.assertEqual(_pdf_page_count(result), 3)

    def test_merge_pdf_no_root_no_catalog_raises(self):
        # unrecoverable: trailer lacks /Root and no /Catalog object exists
        no_root = re.sub(b"/Root\\s+\\d+\\s+\\d+\\s+R", b"", _make_pdf(1), count=1)
        unrecoverable = no_root.replace(b"/Catalog", b"/Xatalog")
        self.assertRaises(PdfReadError, merge_pdf, unrecoverable, _make_pdf(1))
