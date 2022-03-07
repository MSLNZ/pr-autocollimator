pr-autocollimator
=================
Uses a Raspberry Pi HQ camera to determine the location of the crosshair on the autocollimator.

Install
=======
Use the `MSL Package Manager`_

.. code-block:: console

   msl install pr-autocollimator

Usage
=====
The web application starts automatically (via an @reboot cronjob).

There are 4 endpoints that should be called in the recommended order:

1. http://pr-autocollimator

    Use this endpoint when aligning the autocollimator with the polygon mirror.
    The image resolution is lower and the update rate is much faster.

2. http://pr-autocollimator/initialize

    Call this endpoint second. It finds the location of the origin and the crosshair.
    Also accepts a ``threshold`` parameter, value between [0, 255] that you can
    include as a URL parameter if the origin cannot be found, e.g.,
    ``http://pr-autocollimator/initialize?threshold=40``

3. http://pr-autocollimator/crosshair

    Call this endpoint every time you want to know the location of the crosshair.
    Accepts the following parameters:

        * ``threshold`` - A value between [0, 255] to filter the crosshair from the image.
        * ``origin`` - The location of the origin as comma-separated values. If not specified
          then uses the value that was determined from the last call to
          ``http://pr-autocollimator/initialize``
        * ``pixels_per_arcmin`` - The conversion factor to convert pixels coordinates to arcmin.
        * ``plot`` - Whether to return a plot of the crosshair instead of JSON data.
          The value is either 0 (JSON) or 1 (plot).

    Some examples,

    * ``http://pr-autocollimator/crosshair?plot=1``
    * ``http://pr-autocollimator/crosshair?threshold=40``
    * ``http://pr-autocollimator/crosshair?threshold=40&origin=1340,960&pixels_per_arcmin=20``

4. http://pr-autocollimator/shutdown

    Call this endpoint when you want to shutdown the Raspberry Pi.


.. _MSL Package Manager: https://msl-package-manager.readthedocs.io/en/stable/
