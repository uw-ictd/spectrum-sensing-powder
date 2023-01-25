#!/bin/sh
#
# Install the RF monitor and its dependencies.
#
# Temp ettus cache
CACHE="https://www.emulab.net/downloads/ettus/binaries/cache"

wget -O - http://repos.emulab.net/emulab.key | sudo apt-key add -
if [ $? -ne 0 ]; then
    echo 'apt-key add failed'
    exit 1
fi

RELEASE="$(. /etc/os-release ; echo $UBUNTU_CODENAME)"

REPO="powder"

# WTF! The tabs before priority actually matter.
echo "http://boss/mirror/repos.emulab.net/$REPO/ubuntu	priority:1" | sudo tee -a /etc/apt/emulab-$REPO-mirrorlist.txt &&
    echo "http://repos.emulab.net/$REPO/ubuntu	priority:2" | sudo tee -a /etc/apt/emulab-$REPO-mirrorlist.txt &&
    echo "deb mirror+file:/etc/apt/emulab-$REPO-mirrorlist.txt $RELEASE main" | sudo tee -a /etc/apt/sources.list.d/$REPO.list
if [ $? -ne 0 ]; then
    echo "creating $REPO failed"
    exit 1
fi

REPO="powder-endpoints"

# WTF! The tabs before priority actually matter.
echo "http://boss/mirror/repos.emulab.net/$REPO/ubuntu	priority:1" | sudo tee -a /etc/apt/emulab-$REPO-mirrorlist.txt &&
    echo "http://repos.emulab.net/$REPO/ubuntu	priority:2" | sudo tee -a /etc/apt/emulab-$REPO-mirrorlist.txt &&
    echo "deb mirror+file:/etc/apt/emulab-$REPO-mirrorlist.txt $RELEASE main" | sudo tee -a /etc/apt/sources.list.d/$REPO.list
if [ $? -ne 0 ]; then
    echo "creating $REPO failed"
    exit 1g
fi

sudo apt-get update -y
if [ $? -ne 0 ]; then
    echo 'apt-get update failed'
    exit 1
fi

sudo apt-get -y install --no-install-recommends uhd-host libuhd-dev gnuradio gpsd-clients
if [ $? -ne 0 ]; then
    echo 'apt-get install UHD failed'
    exit 1
fi

sudo apt-get -y install --no-install-recommends gnuradio-dev cmake swig
if [ $? -ne 0 ]; then
    echo 'apt-get install LoRa dependencies failed'
    exit 1
fi

sudo uhd_images_downloader -b $CACHE -t b2xx
if [ $? -ne 0 ]; then
    echo 'uhd_images_downloader failed'
    exit 1
fi

cd /usr/lib/x86_64-linux-gnu/
sudo ln -s liborc-0.4.so.0.28.0 liborc-0.4.so

#
# This sets the X11 geometry for uhd_fft. It does not take a --geometry arg.
#
GENIUSER=`geni-get user_urn | awk -F+ '{print $4}'`
HOMEDIR="/users/$GENIUSER"
sudo -u $GENIUSER tar xf /local/repository/uhd_fft-config.tar -C $HOMEDIR

#
# Marker that says we completed the install.
#
sudo touch /etc/.txready
exit 0
