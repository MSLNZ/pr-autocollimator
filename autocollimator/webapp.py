import os

import cv2 as cv
from flask import (
    jsonify,
    render_template,
    request,
    make_response,
    send_from_directory,
    Flask,
    Response,
)

from .autocollimator import AutoCollimator
from .utils import (
    add_marker,
    locate_crosshair,
    locate_origin,
    to_arcmin,
    to_base64,
    to_bytes,
    to_img_tag,
    plot_crosshair,
)


# RESOLUTIONS = {
#     0: '640x480',
#     1: '960x720',
#     2: '1280x960',
#     3: '1600x1200',
#     4: '1920x1440',
#     5: '2240x1680',
#     6: '2560x1920',  # pixels_per_arcmin=17.9
#     7: '3200x2400'
# }

autocollimator = AutoCollimator()

origin_args = {}
origin_position = {}

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )


@app.route('/<string:path>')
def page_not_found(**ignore):
    """Return page not found for all undefined routes."""
    autocollimator.initialize_stream_enabled = False
    autocollimator.index_stream_enabled = False
    return make_response(
        render_template('page_not_found.html', url_root=request.url_root),
        404
    )


@app.route('/')
def index():
    """Fast video streaming home page for alignment purposes."""
    autocollimator.index_stream_enabled = True
    autocollimator.initialize_stream_enabled = False
    while not autocollimator.initialize_stream_done:
        pass
    return render_template('index.html')


@app.route('/index_stream')
def index_stream():
    """Fast video streaming route."""
    def stream():
        autocollimator.index_stream_done = False
        while autocollimator.index_stream_enabled:
            frame = autocollimator.frame()
            yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'
        autocollimator.index_stream_done = True

    autocollimator.resolution('720p')
    autocollimator.turn_led_on()
    return Response(stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/initialize')
def initialize():
    """Initialize the settings."""
    global origin_args
    origin_args = request.args
    autocollimator.initialize_stream_enabled = True
    autocollimator.index_stream_enabled = False
    while not autocollimator.index_stream_done:
        pass
    return render_template('initialize.html')


@app.route('/initialize_stream')
def initialize_stream():
    """Locate the origin and the crosshair."""
    def stream():
        global origin_position
        i = 0
        autocollimator.initialize_stream_done = False
        while autocollimator.initialize_stream_enabled:
            i += 1
            image = autocollimator.capture()
            origin_position = locate_origin(image, thresh=threshold)
            add_marker(image, origin_position, (255, 255, 255))
            crosshair_position = locate_crosshair(image)
            add_marker(image, crosshair_position, (0, 255, 0))

            height, width = image.shape[:2]
            cv.putText(image, f'{i:06d}', (10, 25), cv.FONT_HERSHEY_DUPLEX,
                       1, (127, 127, 127), thickness=1)
            cv.putText(image, f'{width}x{height}', (10, 50), cv.FONT_HERSHEY_DUPLEX,
                       1, (127, 127, 127), thickness=1)

            yield b'Content-Type: image/jpeg\r\n\r\n' + to_bytes(image) + b'\r\n--frame\r\n'
        autocollimator.initialize_stream_done = True

    threshold = origin_args.get('threshold', default=20, type=int)
    autocollimator.resolution('2560x1920')
    autocollimator.turn_led_on()
    return Response(stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/crosshair')
def crosshair():
    """Locate the crosshair."""
    result = {}

    autocollimator.initialize_stream_enabled = False
    autocollimator.index_stream_enabled = False
    autocollimator.turn_led_off()

    image = autocollimator.capture()

    threshold = request.args.get('threshold', default=25, type=int)
    pixels_per_arcmin = request.args.get('pixels_per_arcmin', default=17.9, type=float)
    org = request.args.get('origin')
    if org is None:
        if not origin_position:
            h, w = image.shape[:2]
            xy0 = {'x': w//2, 'y': h//2}
        else:
            xy0 = {'x': origin_position['x'], 'y': origin_position['y']}
    else:
        x0, y0 = org.split(',')
        xy0 = {'x': float(x0), 'y': float(y0)}

    crosshair_ = locate_crosshair(image, thresh=threshold)
    result['x_pixel'] = crosshair_['x']
    result['y_pixel'] = crosshair_['y']

    if request.args.get('debug', default=0, type=int):
        return to_img_tag(plot_crosshair(crosshair_))

    arcmin = to_arcmin(crosshair_, xy0, pixels_per_arcmin=pixels_per_arcmin)
    result['x_arcmin'] = arcmin['x']
    result['y_arcmin'] = arcmin['y']

    degree_per_arcmin = 60.0
    if arcmin['x'] is not None:
        result['x_degree'] = arcmin['x'] / degree_per_arcmin
    if arcmin['y'] is not None:
        result['y_degree'] = arcmin['y'] / degree_per_arcmin

    autocollimator.turn_led_on()
    image = autocollimator.capture()
    autocollimator.turn_led_off()
    if arcmin['x'] is not None and arcmin['y'] is not None:
        add_marker(image, crosshair_, (0, 255, 0), label='({x:.1f}, {y:.1f})'.format(**arcmin))

    result['image'] = to_base64(image)
    if request.args.get('show', default=0, type=int):
        return to_img_tag(result['image'])

    return jsonify(result)


@app.route('/shutdown')
def shutdown():
    """Close the application and shutdown the Raspberry Pi."""
    autocollimator.close()
    os.system('sudo shutdown now')


def run():
    """Console script to start the webapp."""
    try:
        app.run(host='0.0.0.0', port=80, threaded=True)
    except KeyboardInterrupt:
        pass
    finally:
        autocollimator.close()
