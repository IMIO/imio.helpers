# -*- coding: utf-8 -*-

import six
import subprocess


def generate_barcode(data, executable='zint', barcode=92, scale=2, filetype='PNG', extra_args=""):
    """Generate a barcode with zint in BytesIO and return it

    :param data: barcode content string
    :param executable: executable used to generate barcode
    :param barcode: barcode type number
    :param scale: scale of generated output
    :param filetype: image
    :param extra_args: additional arguments for zint, for example '--secure=2'
    :return: BytesIO handler
    """
    output = six.BytesIO()

    command = [
        executable,
        '--direct',
        f'--filetype={filetype}',
        f'--barcode={barcode}',
        f'--scale={scale}',
        *extra_args.split(),
        f'--data={data}',
    ]

    with subprocess.Popen(command, stdout=subprocess.PIPE) as process:
        output.write(process.stdout.read())
        process.stdout.close()
        process.wait()

    output.seek(0)
    return output