from xbee import str_trans
from gps import open_gps , read_gps , close_gps
open_gps()
a = read_gps()
str_trans(a)
close_gps()
