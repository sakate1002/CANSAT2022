import os
import time
from smbus import SMBus
import pigpio

import bme280
import bmx055
import gps
import xbee


pi = pigpio.pi()


##### for only acc
ACC_ADDRESS = 0x19
ACC_REGISTER_ADDRESS = 0x02
i2c = SMBus(1)


def bmx055_setup():
    # --- BMC050Setup --- #
    # Initialize ACC
    try:
        i2c.write_byte_data(ACC_ADDRESS, 0x0F, 0x03)
        time.sleep(0.1)
        i2c.write_byte_data(ACC_ADDRESS, 0x10, 0x0F)
        time.sleep(0.1)
        i2c.write_byte_data(ACC_ADDRESS, 0x11, 0x00)
        time.sleep(0.1)
    except:
        time.sleep(0.1)
        print("BMC050 Setup Error")
        i2c.write_byte_data(ACC_ADDRESS, 0x0F, 0x03)
        time.sleep(0.1)
        i2c.write_byte_data(ACC_ADDRESS, 0x10, 0x0F)
        time.sleep(0.1)
        i2c.write_byte_data(ACC_ADDRESS, 0x11, 0x00)
        time.sleep(0.1)


def acc_data_Read():
    # --- Read Acc Data --- #
    accData = [0, 0, 0, 0, 0, 0]
    value = [0.0, 0.0, 0.0]
    for i in range(6):
        try:
            accData[i] = i2c.read_byte_data(
                ACC_ADDRESS, ACC_REGISTER_ADDRESS + i)
        except:
            pass

    for i in range(3):
        value[i] = (accData[2 * i + 1] * 16) + (int(accData[2 * i] & 0xF0) / 16)
        value[i] = value[i] if value[i] < 2048 else value[i] - 4096
        value[i] = value[i] * 0.0098 * 1

    return value

print('---xbee---')
try:
    xbee.on()
    for i in range(10):
        xbee.str_trans(str(i) + '  : reseive?')
except:
    print('error : xbee')
    
print('----i2cdetect----')
os.system('i2cdetect -y 1')

print('\n---Environment---')
try:
    bme280.bme280_setup()
    bme280.bme280_calib_param()
    for _ in range(5):
        bme_data = bme280.bme280_read()
        print(bme_data)
        time.sleep(1)
except:
    print('error : env')


print('---mag---')
try:
    bmx055.bmx055_setup()
    for _ in range(5):
        mag_data = bmx055.mag_dataRead()
        print(mag_data)
        time.sleep(0.2)
except:
    print('error : mag')

print('---acc---')
try:
    bmx055_setup()
    for _ in range(5):
        acc_data = bmx055.acc_dataRead()
        print(acc_data)
        time.sleep(0.2)
except:
    print('error : acc')

print('---xbee---')
try:
    xbee.on()
    for i in range(10):
        xbee.str_trans(str(i) + '  : reseive?')
except:
    print('error : xbee')

print('---gps---')
try:
    gps.open_gps()
    data = gps.gps_data_read()
    print(data)
except:
    print('error : gps')

def all():
    print('---xbee---')
    try:
        xbee.on()
        for i in range(10):
            xbee.str_trans(str(i) + '  : reseive?')
    except:
        print('error : xbee')
    
    print('----i2cdetect----')
    os.system('i2cdetect -y 1')

    print('\n---Environment---')
    try:
        bme280.bme280_setup()
        bme280.bme280_calib_param()
        for _ in range(5):
            bme_data = bme280.bme280_read()
            print(bme_data)
            time.sleep(1)
    except:
        print('error : env')


    print('---mag---')
    try:
        bmx055.bmx055_setup()
        for _ in range(5):
            mag_data = bmx055.mag_dataRead()
            print(mag_data)
            time.sleep(0.2)
    except:
            print('error : mag')

    print('---acc---')
    try:
        bmx055_setup()
        for _ in range(5):
            acc_data = bmx055.acc_dataRead()
            print(acc_data)
            time.sleep(0.2)
    except:
        print('error : acc')

    print('---xbee---')
    try:
        xbee.on()
        for i in range(10):
            xbee.str_trans(str(i) + '  : reseive?')
    except:
        print('error : xbee')

    print('---gps---')
    try:
        gps.open_gps()
        data = gps.gps_data_read()
        print(data)
    except:
        print('error : gps')