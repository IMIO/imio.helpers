# -*- coding: utf-8 -*-

import cStringIO
import subprocess


def generate_barcode(data, executable='zint', barcode=92, scale=2):
    """Generate a barcode with zint in StringIO and return it"""
    output = cStringIO.StringIO()
    command = [
        executable,
        # '--directpng',  # no more used in version 2.6.0, and replaced by 2 following parameters
        '--direct',
        '--filetype=PNG',
        '--barcode={0}'.format(barcode),
        '--scale={0}'.format(scale),
        '--data={0}'.format(data),
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output.write(process.stdout.read())
    output.seek(0)
    return output
