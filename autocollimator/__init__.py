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


def crosshair(host='pr-autocollimator'):
    """Locate the crosshair."""
    reply = requests.get(f'http://{host}/crosshair')
    json = reply.json()

    buffer = BytesIO(b64decode(json['image']))
    arr = np.frombuffer(buffer.getvalue(), dtype=np.uint8)
    image = cv.imdecode(arr, flags=cv.IMREAD_UNCHANGED)
    json['image'] = image
    return json
