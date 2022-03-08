#!/bin/bash

ENV="autocolenv"

# install the dependencies for opencv-python==4.5.4.60
sudo apt-get install --yes libaom0 libatk-bridge2.0-0 libatk1.0-0 libatlas3-base libatspi2.0-0 libavcodec58 libavformat58 libavutil56 libbluray2 libcairo-gobject2 libcairo2 libchromaprint1 libcodec2-0.8.1 libcroco3 libdatrie1 libdrm2 libepoxy0 libfontconfig1 libgdk-pixbuf2.0-0 libgfortran5 libgme0 libgraphite2-3 libgsm1 libgtk-3-0 libharfbuzz0b libilmbase23 libjbig0 libmp3lame0 libmpg123-0 libogg0 libopenexr23 libopenjp2-7 libopenmpt0 libopus0 libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 libpixman-1-0 librsvg2-2 libshine3 libsnappy1v5 libsoxr0 libspeex1 libssh-gcrypt-4 libswresample3 libswscale5 libthai0 libtheora0 libtiff5 libtwolame0 libva-drm2 libva-x11-2 libva2 libvdpau1 libvorbis0a libvorbisenc2 libvorbisfile3 libvpx5 libwavpack1 libwayland-client0 libwayland-cursor0 libwayland-egl1 libwebp6 libwebpmux3 libx264-155 libx265-165 libxcb-render0 libxcb-shm0 libxcomposite1 libxcursor1 libxdamage1 libxfixes3 libxi6 libxinerama1 libxkbcommon0 libxrandr2 libxrender1 libxvidcore4 libzvbi0

# install the dependencies for numpy==1.21.4
sudo apt-get install --yes libatlas3-base libgfortran5

# create the virtual environment
sudo apt-get install --yes python3-venv
python3 -m venv $ENV
source $ENV/bin/activate
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools wheel

# install pr-autocollimator
cd pr-autocollimator
python -m pip install .
cd ..

# deactivate the virtual environment
deactivate

# ANSI escape codes
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
RESET='\033[0m'

echo
echo -e "${YELLOW}Make sure that the camera interface is enable in the Raspberry Pi Configuration.${RESET}"
echo -e "${YELLOW}Also, edit crontab to start the web application on reboot, run${RESET}"
echo -e "${CYAN}sudo crontab -e${RESET}"
echo -e "${CYAN}then append the following line to the file,${RESET}"
echo -e "${CYAN}@reboot /home/pi/$ENV/bin/autocollimator >/home/pi/autocollimator.log 2>&1${RESET}"
echo
