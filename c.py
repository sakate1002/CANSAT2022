import time
import xbee
from xbee import str_trans , str_receive
from gps import open_gps , read_gps , close_gps
import escape

xbee.str_trans('continue? y/n \t')
if xbee.str_receive() == 'y':
    pass

elif xbee.str_receive() == 'n':
    xbee.str_trans('Interrupted for safety')
    exit()

escape.escape()