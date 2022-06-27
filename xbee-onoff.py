from xbee import on,off
import time
while 1:
    off()
    print("off")
    time.sleep(2)
    on()
    print("on")
    time.sleep(2)
# off()