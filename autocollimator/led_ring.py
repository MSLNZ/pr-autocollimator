from rpi_ws281x import PixelStrip


class LEDRing(object):

    def __init__(self, *, number=24, channel=18, **kwargs):
        """The LED ring (NeoPixel) from Duinotech (Adafruit).

        Parameters
        ----------
        number : :class:`int`, optional
            The number of LED's that the NeoPixel has.
        channel : :class:`int`, optional
            The GPIO channel that is connected to the DATA IN on the NeoPixel.
        kwargs
            All additional keyword arguments are passed to :class:`rpi_ws281x.PixelStrip`.
        """
        self._neopixel = PixelStrip(number, channel, **kwargs)
        self._neopixel.begin()

    def num_leds(self):
        """Get the number of LEDs in the ring.

        Returns
        -------
        :class:`int`
            The number of LEDs in the ring.
        """
        return self._neopixel.numPixels()

    def set_brightness(self, brightness, *, update=False):
        """Set the brightness percentage of all LED's.

        Parameters
        ----------
        brightness : :class:`int` or :class:`float`
            The brightness percentage, between [0, 100].
        update : :class:`bool`, optional
            Whether to update the LED brightness immediately or to just set the
            brightness in the buffer.
        """
        b = round(255.0 * min(max(0, brightness), 100) / 100.0)
        self._neopixel.setBrightness(b)
        if update:
            self.update()

    def set_rgb(self, index, red, green, blue, *, update=False):
        """Set the RGB value of an LED.

        Parameters
        ----------
        index : :class:`int`
            The index of the LED to change the colour of.
        red : :class:`int`
            The red value, between [0, 255].
        green : :class:`int`
            The green value, between [0, 255].
        blue : :class:`int`
            The green value, between [0, 255].
        update : :class:`bool`, optional
            Whether to update the LED colour immediately or to just set the
            colour in the buffer.
        """
        self._neopixel.setPixelColorRGB(index, red, green, blue)
        if update:
            self.update()

    def update(self):
        """Update the display with the data from the buffer."""
        self._neopixel.show()
