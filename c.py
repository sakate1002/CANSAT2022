from xbee import str_trans
from bme280 import bme280_read , bme280_setup , writeReg , bme280_calib_param
#writeReg()
bme280_setup()
bme280_calib_param()
a = bme280_read()
str_trans(a)