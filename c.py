from xbee import str_trans
from bme280 import bme280_read , bme280_setup
bme280_setup()
a = bme280_read()
str_trans(a)