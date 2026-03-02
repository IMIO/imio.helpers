# -*- coding: utf-8 -*-


try:
    from PyPDF2 import PdfReader
    from PyPDF2 import PdfWriter
except ImportError:
    from PyPDF2 import PdfFileReader as PdfReader, PdfFileWriter as PdfWriter

from imio.helpers import barcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Flowable
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus.flowables import Image

import io
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

    def __init__(self, filepath, barcode_value, x=0, y=0, tmp_path="/tmp", scale=4):
        self.filepath = filepath
        self.output = io.BytesIO()
        self.uuid = uuid.uuid4()
        self.barcode_value = barcode_value

        self.x = x
        self.y = y
        self.tmp_path = tmp_path
        self.scale = scale

    def _path(self, extension, suffix=""):
        filename = "{name}{suffix}.{ext}".format(
            name=self.uuid,
            suffix=suffix and "-{0}".format(suffix) or "",
            ext=extension,
        )
        return os.path.join(self.tmp_path, filename)

    def stamp(self):
        barcode_path = self._create_barcode()
        stamp_path = self._create_stamp(barcode_path)
        self._merge_pdf(stamp_path)
        return self.output

    def _create_barcode(self):
        path = self._path("png")
        barcode_io = barcode.generate_barcode(self.barcode_value, scale=self.scale)
        f = open(path, "wb")
        f.write(barcode_io.getvalue())
        f.close()
        return path

    def _create_stamp(self, barcode_path):
        path = self._path("pdf", suffix="stamp")
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            topMargin=0 - 2 * mm,
            rightMargin=0,
            bottomMargin=0,
            leftMargin=0 - 2 * mm,
        )
        doc.build([BarcodeFlowable(barcode_path, self.x, self.y)])
        f = open(path, "wb")
        f.write(buf.getvalue())
        f.close()
        os.remove(barcode_path)
        return path

    def _merge_pdf(self, stamp_path):
        output_writer = PdfWriter()
        stamp = PdfReader(open(stamp_path, "rb"))
        content_file = open(self.filepath, "rb")
        content = PdfReader(content_file)
        counter = 0
        for page in content.pages:
            if counter == 0:
                stamp_content = stamp.pages[0]
                (getattr(page, "merge_page", None) or page.mergePage)(stamp_content)
            (getattr(output_writer, "add_page", None) or output_writer.addPage)(page)
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
        width = width * 72.0 / 300
        height = height * 72.0 / 300
        canvas.drawImage(
            self.barcode,
            self.x * mm,
            (self.y * mm * -1) - height,
            width,
            height,
        )


def merge_pdf(*pdf_datas):
    """Merge multiple PDFs into one.

    :param pdf_datas: bytes of each PDF to merge, in order
    :return: merged PDF bytes
    """
    writer = PdfWriter()
    for data in pdf_datas:
        reader = PdfReader(io.BytesIO(data))
        for page in reader.pages:
            (getattr(writer, "add_page", None) or writer.addPage)(page)
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()
