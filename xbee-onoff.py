from xbee import on,off,str_trans
import time
while 1:
    str_trans("Hello")
    str_trans("Hello")
    str_trans("Hello")
    str_trans("Hello")
    off()
    str_trans("bye!")
    str_trans("Bye!")
    str_trans("Bye!")
    str_trans("Bye!")
    print("off")
    time.sleep(2)
    on()
    print("on")
    time.sleep(2)
# off()