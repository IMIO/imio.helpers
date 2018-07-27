# -*- coding: utf-8 -*-

from cStringIO import StringIO
from imio.helpers import barcode
from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Flowable
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus.flowables import Image

import os
import uuid


class BarcodeStamp(object):
    """
    Example of usage
    ---
    BarcodeStamp(
        'file.pdf',
        '12345678901234567890',
        x=25,
        y=34,
    )
    """

    def __init__(self,
                 filepath,
                 barcode_value,
                 x=0,
                 y=0,
                 tmp_path='/tmp',
                 scale=4):
        self.filepath = filepath
        self.output = StringIO()
        self.uuid = uuid.uuid4()
        self.barcode_value = barcode_value

        self.x = x
        self.y = y
        self.tmp_path = tmp_path
        self.scale = scale

    def _path(self, extension, suffix=''):
        filename = '{name}{suffix}.{ext}'.format(
            name=self.uuid,
            suffix=suffix and '-{0}'.format(suffix) or '',
            ext=extension,
        )
        return os.path.join(self.tmp_path, filename)

    def stamp(self):
        barcode_path = self._create_barcode()
        stamp_path = self._create_stamp(barcode_path)
        self._merge_pdf(stamp_path)
        return self.output

    def _create_barcode(self):
        path = self._path('png')
        barcode_io = barcode.generate_barcode(self.barcode_value, scale=self.scale)
        f = open(path, 'w')
        f.write(barcode_io.getvalue())
        f.close()
        return path

    def _create_stamp(self, barcode_path):
        path = self._path('pdf', suffix='stamp')
        io = StringIO()
        doc = SimpleDocTemplate(
            io,
            pagesize=A4,
            topMargin=0 - 2 * mm,
            rightMargin=0,
            bottomMargin=0,
            leftMargin=0 - 2 * mm,
        )
        doc.build([BarcodeFlowable(barcode_path, self.x, self.y)])
        f = open(path, 'w')
        f.write(io.getvalue())
        f.close()
        os.remove(barcode_path)
        return path

    def _merge_pdf(self, stamp_path):
        output_writer = PdfFileWriter()
        stamp = PdfFileReader(open(stamp_path, 'rb'))
        content_file = open(self.filepath, 'rb')
        content = PdfFileReader(content_file)
        counter = 0
        for page in content.pages:
            if counter == 0:
                stamp_content = stamp.getPage(0)
                page.mergePage(stamp_content)
            output_writer.addPage(page)
            counter += 1
        output_writer.write(self.output)
        os.remove(stamp_path)


class BarcodeFlowable(Flowable):

    def __init__(self, barcode, x, y):
        Flowable.__init__(self)
        self.barcode = barcode
        self.x = x
        self.y = y

    def draw(self):
        canvas = self.canv
        img = Image(self.barcode)
        width, height = img.wrapOn(canvas, 0, 0)
        width = width * 72. / 300
        height = height * 72. / 300
        canvas.drawImage(
            self.barcode,
            self.x * mm,
            (self.y * mm * -1) - height,
            width,
            height,
        )
