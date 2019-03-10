[DBC](http://socialledge.com/sjsu/index.php/DBC_Format) based CAN to MQTT brigde
===

This is a generic CAN 2 MQTT bridge build with Python 3

### Setup

This package is based upon the following dependencies:

* [python-can](https://python-can.readthedocs.io/en/master/)
* [cantools](https://github.com/eerimoq/cantools)
* [phao](http://www.eclipse.org/paho/)

Install all required Python 3 dependencies on a rasperry:

    sudo apt-get install python3-pip python3-can
    pip3 install paho-mqtt cantools

### Usage

Copy your DBC files into the root directory.

Copy config.example.yaml to config.yaml and modify it.

Run `./main.py` or `python3 main.py`
