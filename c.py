from xbee import str_trans
from gps import read_gps
from bme280 import bme280_read()
str_trans(bme280_read())