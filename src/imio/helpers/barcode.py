# -*- coding: utf-8 -*-

import six
import subprocess


def generate_barcode(data, executable='zint', barcode=92, scale=2, filetype='PNG'):
    """Generate a barcode with zint in StringIO and return it

    :param data: barcode content string
    :param executable: executable used to generate barcode
    :param barcode: barcode type number
    :param scale: scale of generated output
    :param filetype: image type
    :return: StringIO handler
    """

    output = six.BytesIO()

    command = [
        executable,
        # '--directpng',  # no more used in version 2.6.0, and replaced by 2 following parameters
        '--direct',
        '--filetype={0}'.format(filetype),
        '--barcode={0}'.format(barcode),
        '--scale={0}'.format(scale),
        '--data={0}'.format(data),
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output.write(process.stdout.read())
    output.seek(0)
    return output
