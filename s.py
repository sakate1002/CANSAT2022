import time
import datetime
import sys

import sensor.axis.bmx055 as bmx055
import xbee
import SensorModule.gps.gps as gps
import sensor.environment.bme280 as bme280
from other import print_xbee
import release_land
import paradetection
import land
import paraavoidance
import other
import escape
import gpsrun0
import photo_running
import calibration
import motor

dateTime = datetime.datetime.now()

# variable for calibration
strength_l_cal = 40
strength_r_cal = -40
t_rotation_cal = 0.2
number_data = 30

# variable for GPSrun
# lat2 = 35.918548
# lon2 = 139.908896
lat2 = 35.412923
lon2 = 138.592713

th_distance = 6.5
t_adj_gps = 180

# variable for photorun
G_thd = 50
path_photo_imagerun = f'photostorage/ImageGuidance_{dateTime.month}-{dateTime.day}-{dateTime.hour}-{dateTime.minute}'

# variable for log
log_phase = other.filename('/home/pi/Desktop/cansat2021/log/phaseLog', 'txt')
log_gpsrunning = other.filename(
    '/home/pi/Desktop/cansat2021/log/gpsrunningLog', 'txt')
log_photorunning = other.filename(
    '/home/pi/Desktop/cansat2021/log/photorunning', 'txt')

def setup():
    global phase
    xbee.on()
    gps.open_gps()
    bmc050.bmc050_setup()
    bme280.bme280_setup()
    bme280.bme280_calib_param()


def close():
    gps.close_gps()
    xbee.off()


if __name__ == '__main__':
    motor.setup()

#######-----------------------Setup--------------------------------#######
    try:
        t_start = time.time()
        print_xbee('#####-----Setup Phase start-----#####')
        other.log(log_phase, "1", "Setup phase",
                  datetime.datetime.now(), time.time() - t_start)
        phase = other.phase(log_phase)
        if phase == 1:
            print_xbee(f'Phase:\t{phase}')
            setup()
            print_xbee('#####-----Setup Phase ended-----##### \n \n')
            print_xbee('####----wait----#### ')
            t_wait = 150
            for i in range(t_wait):
                print_xbee(t_wait-i)
                time.sleep(1)
    except Exception as e:
        tb = sys.exc_info()[2]
        print_xbee("message:{0}".format(e.with_traceback(tb)))
        print_xbee('#####-----Error(setup)-----#####')
        print_xbee('#####-----Error(setup)-----#####\n \n')
    #######-----------------------------------------------------------########
    
#######--------------------------gps--------------------------#######

    print_xbee('#####-----gps run start-----#####')
    other.log(log_phase, '2', 'GPSrun phase start',
              datetime.datetime.now(), time.time() - t_start)
    phase = other.phase(log_phase)
    print_xbee(f'Phase:\t{phase}')
    if phase == 7:
        gpsrun0.drive(lon2, lat2, th_distance, t_adj_gps, log_gpsrunning)
    # except Exception as e:
    #     tb = sys.exc_info()[2]
    #     print_xbee("message:{0}".format(e.with_traceback(tb)))
    #     print_xbee('#####-----Error(gpsrunning)-----#####')
    #     print_xbee('#####-----Error(gpsrunning)-----#####\n \n')

    ######------------------photo running---------------------##########
    try:
        print_xbee('#####-----photo run start-----#####')
        other.log(log_phase, '3', 'image run phase start',
                  datetime.datetime.now(), time.time() - t_start)
        phase = other.phase(log_phase)
        print_xbee(f'Phase:\t{phase}')
        if phase == 8:
            magx_off, magy_off = calibration.cal(40, -40, 60)
            photo_running.image_guided_driving(
                log_photorunning, G_thd, magx_off, magy_off, lon2, lat2, th_distance, t_adj_gps, gpsrun=True)
    except Exception as e:
        tb = sys.exc_info()[2]
        print_xbee("message:{0}".format(e.with_traceback(tb)))
        print_xbee('#####-----Error(Photo running)-----#####')
        print_xbee('#####-----Error(Photo running)-----#####\n \n')
