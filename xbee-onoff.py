from xbee import on,off,str_trans
import time
while 1:
    off()
    print("off")
    time.sleep(2)
    str_trans("Bye")
    on()
    print("on")
    time.sleep(2)
    str_trans("Hello")
# off()