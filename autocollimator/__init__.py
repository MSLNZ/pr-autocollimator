from base64 import b64decode
from collections import namedtuple
from io import BytesIO
import re

import requests
import cv2 as cv
import numpy as np

__author__ = 'Measurement Standards Laboratory of New Zealand'
__copyright__ = '\xa9 2022, ' + __author__
__version__ = '0.1.0.dev0'

_v = re.search(r'(\d+)\.(\d+)\.(\d+)[.-]?(.*)', __version__).groups()

version_info = namedtuple('version_info', 'major minor micro releaselevel')(int(_v[0]), int(_v[1]), int(_v[2]), _v[3])
""":obj:`~collections.namedtuple`: Contains the version information as a (major, minor, micro, releaselevel) tuple."""


def crosshair(*, host='pr-autocollimator', debug=False, show=False,
              origin=None, threshold=None, pixels_per_arcmin=None):
    """Fetch information about the current location of the crosshair.

    Parameters
    ----------
    host : :class:`str`, optional
        The hostname or IP address of the Raspberry Pi.
    debug : :class:`bool`, optional
        Whether to return a binary image of the localized crosshair and the
        projections along the x and y axes as an <img> html tag.
    show : :class:`bool`, optional
        Whether to return an image of the localized crosshair as an
        <img> html tag.
    origin : :class:`list`, optional
        The [x, y] location of the origin in pixel units.
    threshold : :class:`int`, optional
        A value between [0, 255] to filter the crosshair from the image.
    pixels_per_arcmin : :class:`float`, optional
        The conversion factor to convert pixel units to arcmin units.

    Returns
    -------
    :class:`dict` or :class:`str`
        If `debug` or `show` is enabled then the <img> html tag as
        a string. Otherwise, a dictionary containing the location of the
        crosshair and the image is returned.
    """
    params = {}
    if debug:
        params['debug'] = 1
    if show:
        params['show'] = 1
    if origin:
        params['origin'] = f'{origin[0]},{origin[1]}'
    if threshold:
        params['threshold'] = str(threshold)
    if pixels_per_arcmin:
        params['pixels_per_arcmin'] = str(pixels_per_arcmin)

    reply = requests.get(f'http://{host}/crosshair', params=params)
    reply.raise_for_status()

    if debug or show:
        return reply.content.decode()

    json = reply.json()
    buffer = BytesIO(b64decode(json['image']))
    arr = np.frombuffer(buffer.getvalue(), dtype=np.uint8)
    image = cv.imdecode(arr, flags=cv.IMREAD_UNCHANGED)
    json['image'] = image
    return json


def saveas(filename, image, params=None):
    """Save the image to a file.

    Parameters
    ----------
    filename : :class:`str`
        The name of the file to save to.
    image : :class:`numpy.ndarray`
        The image in OpenCV format.
    params : :class:`tuple`, optional
        Format-specific parameters encoded as pairs (paramId_1, paramValue_1, paramId_2, paramValue_2, ...).
        See :ref:`ImwriteFlags <https://docs.opencv.org/3.4/d8/d6a/group__imgcodecs__flags.html#ga292d81be8d76901bff7988d18d2b42ac>`_

    Returns
    -------
    :class:`bool`
        Whether calling this function was successful.
    """
    return cv.imwrite(filename, image, params=params)
