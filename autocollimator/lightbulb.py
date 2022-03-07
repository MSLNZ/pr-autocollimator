import RPi.GPIO as GPIO


class Lightbulb(object):

    def __init__(self, channel=19):
        """Control the state of the autocollimator's lightbulb.

        Parameters
        ----------
        channel : :class:`int`, optional
            The GPIO channel that controls the voltage regulator.
        """
        super(Lightbulb, self).__init__()

        self._channel = channel
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(channel, GPIO.OUT, initial=GPIO.LOW)

    def close(self) -> None:
        """Turn off the lightbulb and clean up GPIO resources."""
        self.turn_off()
        GPIO.cleanup()

    def toggle(self) -> None:
        """Toggle the state of the lightbulb.

        If it is currently on then turn it off.
        If it is currently off then turn it on.
        """
        GPIO.output(self._channel, not GPIO.input(self._channel))

    def turn_on(self) -> None:
        """Turn the lightbulb on."""
        GPIO.output(self._channel, GPIO.HIGH)

    def turn_off(self) -> None:
        """Turn the lightbulb off."""
        GPIO.output(self._channel, GPIO.LOW)
