from xbee import on,off,str_trans
import time
while 1:
    str_trans("Bye")
    on()
    str_trans("Hello")
    print("on")
    time.sleep(2)
    off()
    print("off")
    time.sleep(2)
# off()