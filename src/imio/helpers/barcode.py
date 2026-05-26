# -*- coding: utf-8 -*-

import six
import subprocess


PIL_RASTER_FILETYPES = {"PNG", "GIF", "BMP", "JPG", "JPEG", "TIF", "TIFF"}
PIL_FORMAT_ALIASES = {"JPG": "JPEG", "TIF": "TIFF"}


def generate_barcode(data, executable='zint', barcode=92, scale=2, filetype='PNG', extra_args=None,
                     resize=None):
    """Generate a barcode with zint in BytesIO and return it
    :param data: barcode content string
    :param executable: executable used to generate barcode
    :param barcode: barcode type number
    :param scale: scale of generated output
    :param filetype: image
    :param extra_args: additional arguments for zint, for example ["--secure=2"]
    :param resize: optional float to rescale the generated image (e.g. 0.75 for 75%).
                   Only applies to raster filetypes (PNG, GIF, BMP, JPG, TIF).
                   Uses PIL/Pillow with LANCZOS resampling.
    :return: BytesIO handler
    """
    output = six.BytesIO()

    command = [
        executable,
        # '--directpng',  # no more used in version 2.6.0, and replaced by 2 following parameters
        "--direct",
        "--filetype={0}".format(filetype),
        "--barcode={0}".format(barcode),
        "--scale={0}".format(scale),
    ]
    if extra_args:
        command += extra_args
    # Data must be the last argument
    command.append("--data={0}".format(data))

    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output.write(process.stdout.read())
    process.stdout.close()
    process.wait()

    if resize and resize != 1 and filetype.upper() in PIL_RASTER_FILETYPES:
        from PIL import Image

        resample = Image.LANCZOS
        output.seek(0)
        img = Image.open(output)
        new_size = (int(round(img.width * resize)), int(round(img.height * resize)))
        img = img.resize(new_size, resample)
        resized = six.BytesIO()
        pil_format = PIL_FORMAT_ALIASES.get(filetype.upper(), filetype.upper())
        img.save(resized, format=pil_format)
        output = resized

    output.seek(0)
    return output
