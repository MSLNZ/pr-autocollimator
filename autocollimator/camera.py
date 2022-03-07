from io import BytesIO

import picamera
import numpy as np


class Camera(object):

    def __init__(self, **kwargs):
        """All keywords arguments are passed to :class:`picamera.PiCamera`."""
        self._camera = picamera.PiCamera(**kwargs)
        self._initialize_array()

    def frame(self):
        """Capture a frame for fast video streaming.

        Returns
        -------
        :class:`bytes`
            The frame.
        """
        with BytesIO() as buffer:
            self._camera.capture(buffer, format='jpeg', use_video_port=True)
            buffer.seek(0)
            return buffer.read()

    def capture(self):
        """Capture an image into an OpenCV array.

        Returns
        -------
        :class:`numpy.ndarray`
            The image as an OpenCV array.
        """
        self._camera.capture(self._array, format='bgr')
        return self._array.reshape((self._height, self._width, 3))

    def close(self):
        """Close the connection to the camera."""
        self._camera.close()

    def set_resolution(self, resolution):
        """Set the resolution of the camera."""
        self._camera.resolution = resolution
        self._initialize_array()

    def _initialize_array(self):
        self._width, self._height = self._camera.resolution
        self._array = np.empty((self._width * self._height * 3,), dtype=np.uint8)
