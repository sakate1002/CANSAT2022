from xbee import on,off
import time
while 1:
    off()
    time.sleep(2)
    on()
    time.sleep(2)
# off()