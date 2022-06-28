from xbee import on,off,str_trans
import time
while 1:
    #str_trans("Hello")
   # str_trans("Hello")
    #str_trans("Hello")
    #str_trans("Hello")
    on()
    #str_trans("bye!")
   # str_trans("Bye!")
   # str_trans("Bye!")
    #str_trans("Bye!")
    print("on")
    time.sleep(2)
    off()
    print("off")
    time.sleep(2)
# off()