from io import BytesIO
from base64 import b64encode

import cv2 as cv
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


def adaptive_threshold(image, *, radius=2, use_mean=True, c=0):
    """Apply adaptive thresholding to an image.

    Parameters
    ----------
    image : :class:`numpy.ndarray`
        The image object. The image must be in greyscale, if it is not then
        it will first be converted to be.
    radius : :class:`int`, optional
        Radius of the pixel neighborhood that is used to calculate a threshold
        value, e.g., radius=2 uses a 5x5 area.
    use_mean : :class:`bool`, optional
        Decides which adaptive thresholding algorithm to use. If :data:`True`
        then uses ``cv2.ADAPTIVE_THRESH_MEAN_C`` else uses
        ``cv2.ADAPTIVE_THRESH_GAUSSIAN_C``.
    c : :class:`int`, optional
        A constant which is subtracted from the mean or weighted mean calculated.

    Returns
    -------
    The image with adaptive threshold applied.
    """
    if radius < 1:
        return image
    if image.ndim > 2:
        image = greyscale(image)
    method = cv.ADAPTIVE_THRESH_MEAN_C if use_mean else cv.ADAPTIVE_THRESH_GAUSSIAN_C
    size = 2 * radius + 1
    return cv.adaptiveThreshold(image, 255, method, cv.THRESH_BINARY_INV, size, c)


def threshold(image, value, *, inverse=True):
    """Apply a threshold to an image.

    Parameters
    ----------
    image : :class:`numpy.ndarray`
        The image object.
    value : :class:`int`
        The threshold value, between 0 and 255.
    inverse : :class:`bool, optional
        Whether to invert black and white values.

    Returns
    -------
    The image with the threshold applied.
    """
    image = greyscale(image)
    inv = cv.THRESH_BINARY_INV if inverse else cv.THRESH_BINARY
    _, out = cv.threshold(image, value, 255, inv)
    return out


def greyscale(image):
    """Convert an image to greyscale.

    Parameters
    ----------
    image : :class:`numpy.ndarray`
        The image object.

    Returns
    -------
    The image converted to greyscale.
    """
    if image.ndim == 2:
        return image
    return cv.cvtColor(image, cv.COLOR_BGR2GRAY)


def roi(image, x, y, w, h):
    """Select a region of interest from an image.

    Parameters
    ----------
    image : :class:`numpy.ndarray`
        The image object.
    x : :class:`int` or :class:`float`
        The x value of the top-left corner.
        If a :class:`float` then a number between 0 and 1.
    y : :class:`int` or :class:`float`
        The y value of the top-left corner.
        If a :class:`float` then a number between 0 and 1.
    w : :class:`int` or :class:`float`
        The width of the cropped region. If a :class:`float`
        then a number between 0 and 1.
    h : :class:`int` or :class:`float`
        The height of the cropped region. If a :class:`float`
        then a number between 0 and 1.

    Returns
    -------
    The cropped image.
    """
    height, width = image.shape[:2]

    # rescale the input parameters if any of the parameters is a float
    if isinstance(x, float) or isinstance(y, float) or isinstance(w, float) or isinstance(h, float):
        x = int(width * x)
        y = int(height * y)
        w = int(width * w)
        h = int(height * h)

    new = np.ones(image.shape, dtype=np.uint8) * 255
    new[y:y+h, x:x+w] = image[y:y+h, x:x+w]
    return new


def filter_crosshair(image, *, bgr1=(50, 50, 90), bgr2=(120, 120, 170)):
    """Filter the crosshair from an image.

    Parameters
    ----------
    image : :class:`numpy.ndarray`
        The image object.
    bgr1 : :class:`tuple`, optional
        The (blue, green, red) lower bound.
    bgr2 : :class:`tuple`, optional
        The (blue, green, red) upper bound.

    Returns
    -------
    :class:`numpy.ndarray`
        A new image, with the same shape as the input image, with only the
        crosshair visible.
    """
    return cv.inRange(image, bgr1, bgr2)


def closing(image, *, radius=2, iterations=3):
    """Apply closing to an image.

    Parameters
    ----------
    image : :class:`numpy.ndarray`
        The image object.
    radius : :class:`int`, optional
        The number of pixels to include in each direction. For example, if
        radius=1 then use 1 pixel in each direction from the central pixel,
        i.e., 3x3 area.
    iterations : :class:`int`, optional
        The number of times dilation and erosion are applied.

    Returns
    -------
    The image with closing applied.
    """
    if radius < 1:
        return image
    d = 2 * radius + 1
    kernel = np.ones((d, d), dtype=np.uint8)
    return cv.morphologyEx(image, cv.MORPH_CLOSE, kernel, iterations=iterations)


def normalize(image, axis):
    """Project an axis then normalize.

    Parameters
    ----------
    image : :class:`numpy.ndarray`
        The image object.
    axis : :class:`int`
        The axis to normalize (0 or 1).

    Returns
    -------
    :class:`numpy.ndarray`
        The projected and normalized data.
    """
    summed = np.sum(image, axis=axis)
    maximum = np.max(summed)
    if maximum == 0:
        return summed
    return summed / maximum


def fit(data, *, n=10):
    """Find the location of projected data along an axis via a gaussian fit.

    Parameters
    ----------
    data : :class:`numpy.ndarray`
        The projected data along an axis.
    n : :class:`int`, optional
        The number of neighbouring pixels to include in the fit.

    Returns
    -------
    :class:`float`
        The location determined by a gaussian fit.
    """
    def gauss(value, *p):
        a, mu, sigma = p
        return a * np.exp(-(value - mu) ** 2 / (2. * sigma ** 2))

    max_index = np.argmax(data)
    guess = [1., max_index, 1.]
    x_range = np.arange(min(data.size, max(0, max_index - n)),
                        max(0, min(max_index + n, data.size + 1)), 1)
    try:
        params, _ = curve_fit(gauss, x_range, data[x_range], p0=guess)
        return params[1]
    except IndexError:
        return 0


def plot_crosshair(crosshair):
    """Return a base64 string of the image that was used to locate the crosshair.

    Parameters
    ----------
    crosshair : :class:`dict`
        The location of the crosshair.

    Returns
    -------
    :class:`str`
        A base64 string of the plot.
    """
    x_size = crosshair['x_projection'].size
    y_size = crosshair['y_projection'].size

    size = 10
    fig = plt.figure(figsize=(size, size * y_size / x_size))

    ax_image = plt.axes([0.0, 0.0, 0.9, 0.9])
    ax_x = plt.axes([0.0, 0.9, 0.9, 0.1])
    ax_y = plt.axes([0.9, 0.0, 0.1, 0.9])

    ax_image.set_axis_off()
    ax_x.set_axis_off()
    ax_y.set_axis_off()

    ax_x.plot(crosshair['x_projection'])
    ax_y.plot(crosshair['y_projection'], np.flip(np.arange(y_size)))

    ax_x.set_xlim((0, crosshair['x_projection'].size - 1))
    ax_y.set_ylim((0, crosshair['y_projection'].size - 1))

    ax_image.imshow(crosshair['image'])

    bbox = ax_x.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    ax_image.figure.set_size_inches(bbox.width, h=bbox.width * y_size / x_size)

    x0, y0 = crosshair['x'], crosshair['y']
    if x0 is not None and y0 is not None:
        ax_image.text(x0, y0, f'({x0:.1f}, {y0:.1f})', color='white', size=16,
                      verticalalignment='bottom', horizontalalignment='left')
        ax_image.text(x0, y0, f'X', color='white', size=10,
                      verticalalignment='center', horizontalalignment='center')

    with BytesIO() as buffer:
        plt.savefig(buffer, format='jpeg')
        buffer.seek(0)
        b64 = b64encode(buffer.read()).decode()

    plt.close(fig=fig)
    return b64


def add_marker(image, position, colour, label=None):
    """Add a marker location to an image.

    Parameters
    ----------
    image : :class:`numpy.ndarray`
        The image object.
    position : :class:`dict`
        The position to place the marker.
    colour : :class:`tuple
        The colour to draw the marker.
    label : :class:`str`, optional
        The text to display next to the marker. If not specified when uses the
        `position` x and y values.
    """
    x = position['x']
    y = position['y']

    if x is None or y is None:
        return

    font_face = cv.FONT_HERSHEY_DUPLEX
    font_scale = 1
    thickness = 1
    (size_x, size_y), baseline = cv.getTextSize('X', font_face, font_scale, thickness)

    if label is None:
        label = f'({x:.1f}, {y:.1f})'
    pos = (round(x)+10, round(y)-10)
    cv.putText(image, label, pos, font_face, font_scale, colour, thickness=thickness)

    pos = (round(x - size_x / 2), round(y + size_y / 2))
    cv.putText(image, 'X', pos, font_face, font_scale, colour, thickness=thickness)


def locate_crosshair(image, *, thresh=None):
    """Locate the crosshair.

    Parameters
    ----------
    image : :class:`numpy.ndarray`
        The image object.
    thresh : :class:`int`, optional
        The threshold value. If :data:`None` then filter the crosshair from the
        image based on RGB values.

    Returns
    -------
    :class:`dict`
        The location of the crosshair (in pixel units), the processed image
        and the x and y projections.
    """
    if thresh is None:
        img = filter_crosshair(image)
        img = closing(img)
    else:
        img = threshold(image, thresh, inverse=False)

    x_projection = normalize(img, axis=0)
    y_projection = normalize(img, axis=1)

    try:
        x, y = fit(x_projection), fit(y_projection)
    except:
        x, y = None, None

    if x is not None and x < 1:
        x = None
    if y is not None and y < 1:
        y = None

    return {'x': x, 'y': y, 'image': img, 'x_projection': x_projection,
            'y_projection': y_projection}


def locate_origin(image, *, thresh=20):
    """Locate the origin (where the x and y axes intersect).

    Parameters
    ----------
    image : :class:`numpy.ndarray`
        The image object.
    thresh : :class:`int`, optional
        The threshold value.

    Returns
    -------
    :class:`dict`
        The location of the origin, in pixel units, and the processed image.
    """
    img = roi(image, 0.4, 0.4, 0.2, 0.2)
    img = threshold(img, thresh)
    img = closing(img)
    x = fit(normalize(img, axis=0))
    y = fit(normalize(img, axis=1))
    return {'x': x, 'y': y, 'image': img}


def to_bytes(image):
    """Convert an opencv image to bytes.

    Parameters
    ----------
    image : :class:`numpy.ndarray`
        The image object.

    Returns
    -------
    :class:`bytes`
        The image as bytes.
    """
    _, buf = cv.imencode('.jpeg', image)
    return buf.tobytes()


def to_base64(image):
    """Convert an opencv image to a base64 string.

    Parameters
    ----------
    image : :class:`numpy.ndarray`
        The image object.

    Returns
    -------
    :class:`str`
        The image as a base64 string.
    """
    if image.size == 0:
        return ''
    return b64encode(to_bytes(image)).decode()


def to_img_tag(b64):
    """Create an Img html tag from a base64 string.

    Parameters
    ----------
    b64 : :class:`str`
        A base 64 string.

    Returns
    -------
    :class:`str`
        The <img> tag.
    """
    return f'<img src="data:image/jpeg;base64, {b64}"/>'


def to_arcmin(crosshair, origin, pixels_per_arcmin):
    """Convert the crosshair location from pixels to arcmin.

    Parameters
    ----------
    crosshair : :class:`dict`
        The location of the crosshair.
    origin : :class:`dict`
        The location of the origin.
    pixels_per_arcmin : :class:`float`
        The pixels/arcmin conversion factor.

    Returns
    -------
    :class:`dict`
        The coordinates of the crosshair, in arcmin units.
    """
    try:
        return {
            'x': (crosshair['x'] - origin['x']) / pixels_per_arcmin,
            'y': (origin['y'] - crosshair['y']) / pixels_per_arcmin,
        }
    except TypeError:
        return {'x': None, 'y': None}
