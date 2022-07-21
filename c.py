import time
from sensor.communication.xbee import str_trans
from sensor.gps.gps import open_gps , read_gps , close_gps
open_gps()
while True :
    a = read_gps()
    str_trans(a)
    time.sleep(1)
close_gps()
