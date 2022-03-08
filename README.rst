Uses a Raspberry Pi HQ camera to acquire an image of the eyepiece of the autocollimator
to determine the location of the crosshair.

.. image:: https://raw.githubusercontent.com/MSLNZ/pr-autocollimator/main/resources/assembly.jpg

Install
=======
To install the package on a Raspberry Pi run,

.. code-block:: console

   sudo apt install git
   git clone https://github.com/MSLNZ/pr-autocollimator.git
   source pr-autocollimator/rpi-setup.sh

To install the package on a computer that is not a Raspberry Pi use the `MSL Package Manager`_

.. code-block:: console

   pip install msl-package-manager
   msl install pr-autocollimator

Usage
=====
The web application starts automatically (via an @reboot cron job) when the Raspberry Pi is turned on.

There are 4 endpoints that should be called in the following recommended order:

*NOTE: The hostname of the Raspberry Pi has been configured to be* ``pr-autocollimator``
*in these examples. You may need to modify the URL for your Raspberry Pi based on your hostname.*

1. http://pr-autocollimator

    Visit this URL in a web browser to align the autocollimator with the polygon mirror.
    The image resolution is lower and the update rate is much faster.

2. http://pr-autocollimator/initialize

    Visit this URL in a web browser after you have finished aligning the autocollimator with the
    polygon mirror. It displays the location of the origin and the crosshair.

    Accepts the following parameters:

    * ``threshold`` - A value between [0, 255] to filter the axes from the image.

    For example,

    * ``http://pr-autocollimator/initialize?threshold=40``

3. http://pr-autocollimator/crosshair

    Call this endpoint from a script (or visit the URL in a web browser for quick debugging)
    when you want to determine the location of the crosshair.

    Accepts the following parameters:

        * ``threshold`` - A value between [0, 255] to filter the crosshair from the image.
        * ``origin`` - The location of the origin as comma-separated values (in pixel units).
          If not specified then the program uses the value that was determined from the last
          call to ``http://pr-autocollimator/initialize``
        * ``pixels_per_arcmin`` - The conversion factor to convert pixel units to arcmin units.
        * ``debug`` - Whether to return an html <img> tag of the binary image of the localized
          crosshair and the projections along the x and y axes. To enable *debug* mode use
          ``debug=1`` in the URL parameter. The default value is 0.
        * ``show`` - Whether to return an html <img> tag of the localized crosshair. To enable
          *show* mode use ``show=1`` in the URL parameter. The default value is 0.

    Some examples,

    * ``http://pr-autocollimator/crosshair?debug=1``
    * ``http://pr-autocollimator/crosshair?show=1``
    * ``http://pr-autocollimator/crosshair?threshold=40``
    * ``http://pr-autocollimator/crosshair?threshold=40&origin=1340,960&pixels_per_arcmin=20``

    You can call this endpoint from Python

    .. code-block:: pycon

       >>> import autocollimator
       >>> crosshair = autocollimator.crosshair()
       >>> crosshair.keys()
       dict_keys(['x_pixel', 'y_pixel', 'x_arcmin', 'y_arcmin', 'x_degree', 'y_degree', 'image'])
       >>> crosshair['x_arcmin'], crosshair['y_arcmin']
       (-4.0140337610487595, -1.759120713580572)
       >>> autocollimator.saveas('crosshair_image.jpeg', crosshair['image'])
       True

4. http://pr-autocollimator/shutdown

    Call this endpoint from a script (or visit the URL in a web browser) to shut down the Raspberry Pi.

    You can call this endpoint from Python

    .. code-block:: pycon

       >>> import autocollimator
       >>> autocollimator.shutdown()

Hardware
========
The following hardware is used:

* Raspberry Pi 4 (running buster, *NOT* bullseye)
* Raspberry Pi High Quality Camera
* Raspberry Pi HQ Camera Lens - 6mm Wide Angle
* Duinotech (NeoPixel) RGB LED Ring - 24x LEDs, 72mm outer diameter

Schematics
==========
The circuits to power the lightbulb of the autocollimator and to control the LED ring can
be soldered to a prototype shield and attached to the Raspberry Pi.

.. image:: https://raw.githubusercontent.com/MSLNZ/pr-autocollimator/main/resources/rpi-hat.jpg

.. image:: https://raw.githubusercontent.com/MSLNZ/pr-autocollimator/main/resources/schematic.jpg

.. _MSL Package Manager: https://msl-package-manager.readthedocs.io/en/stable/
