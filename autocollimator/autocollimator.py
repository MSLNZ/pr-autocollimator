import threading

from .camera import Camera
from .led_ring import LEDRing
from .lightbulb import Lightbulb


class AutoCollimator(object):

    def __init__(self):
        """The autocollimator assembly consists of the camera, lightbulb and LED ring."""
        super(AutoCollimator, self).__init__()
        self._lock = threading.Lock()

        self._camera = Camera()
        self._lightbulb = Lightbulb()
        self._leds = LEDRing()

        self.index_stream_enabled = False
        self.index_stream_done = True
        self.initialize_stream_enabled = False
        self.initialize_stream_done = True

    def frame(self):
        """Capture a frame for fast video streaming.

        Returns
        -------
        :class:`bytes`
            The frame.
        """
        with self._lock:
            return self._camera.frame()

    def capture(self):
        """Capture an image into an OpenCV array.

        Returns
        -------
        :class:`numpy.ndarray`
            The image as an OpenCV array.
        """
        with self._lock:
            return self._camera.capture()

    def close(self):
        """Close the connection to the camera and turn off the lightbulb and LED ring."""
        self.initialize_stream_enabled = False
        self.index_stream_enabled = False
        with self._lock:
            try:
                self._camera.close()
            except:
                pass
            try:
                self._lightbulb.turn_off()
            except:
                pass
            try:
                self._leds.set_brightness(0, update=True)
            except:
                pass

    def resolution(self, resolution):
        """Set the resolution of the camera."""
        self._camera.set_resolution(resolution=resolution)

    def turn_lightbulb_off(self):
        """Turn the lightbulb off."""
        with self._lock:
            self._lightbulb.turn_off()

    def turn_lightbulb_on(self):
        """Turn the lightbulb on."""
        with self._lock:
            self._lightbulb.turn_on()

    def turn_led_off(self):
        """Turn the LED's off."""
        with self._lock:
            self._leds.set_brightness(0, update=True)

    def turn_led_on(self, *, brightness=50, greyscale=127, indices=None):
        """Turn the specified LED's on.

        Parameters
        ----------
        brightness : :class:`int`, optional
            The brightness percentage, between [0, 100].
        greyscale : :class:`int`, optional
            The greyscale value, between [0, 255].
        indices : :class:`list` of :class:`int`, optional
            The LED indices to turn on. Default is to turn all on.
        """
        with self._lock:
            if indices is None:
                indices = list(range(self._leds.num_leds()))
            self._leds.set_brightness(brightness)
            for index in indices:
                self._leds.set_rgb(index, greyscale, greyscale, greyscale)
            self._leds.update()
