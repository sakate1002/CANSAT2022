import sys
sys.path.append('/home/cansat2022/CANSAT2022/SensorModule/gps')
sys.path.append('/home/cansat2022/CANSAT2022/SensorModule/communication')
sys.path.append('/home/cansat2022/CANSAT2022/SensorModule/9-axis')
sys.path.append('/home/cansat2022/CANSAT2022/SensorModule/camera')
sys.path.append('/home/cansat2022/CANSAT2022/SensorModule/melt')
sys.path.append('/home/cansat2022/CANSAT2022/SensorModule/environmental')
sys.path.append('/home/cansat2022/CANSAT2022/SensorModule/motor')
sys.path.append('/home/cansat2022/CANSAT2022/SensorModule/illuminance')
sys.path.append('/home/cansat2022/CANSAT2022/detection')
sys.path.append('/home/cansat2022/CANSAT2022/other')
sys.path.append('/home/cansat2022/CANSAT2022/test')
sys.path.append('/home/cansat2022/CANSAT2022/calibration')

import mission
import time
import sensor.camera.take as take
import datetime
import pigpio
import sensor.communication.xbee as xbee
import sensor.axis.bmx055 as bmx055
import sensor.environment.bme280 as bme280
import sensor.gps.gps as gps
import other
import calibration
import release_land
import land
import stuck
from other import print_xbee
from sensor.communication.xbee import str_trans

dateTime = datetime.datetime.now()

# variable for timeout
t_out_release = 120
t_out_land = 30
t_out_release_safe = 1000

# variable for release
thd_press_release = 0.3
t_delta_release = 2  #時間を伸ばす！エレベーター

# variable for landing
thd_press_land = 0.1

log_phase = other.filename('/home/cansat2022/CANSAT2022/log/phaseLog', 'txt')
log_release = other.filename(
    '/home/cansat2022/CANSAT2022/log/releaselog', 'txt')
log_landing = other.filename(
    '/home/cansat2022/CANSAT2022/log/landingLog', 'txt')

def setup():
    global phase
    xbee.on()
    gps.open_gps()
    bmx055.bmx055_setup()
    bme280.bme280_setup()
    bme280.bme280_calib_param()


def close():
    gps.close_gps()
    xbee.off()

if __name__ == '__main__':

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
            t_wait = 3
            for i in range(t_wait):
                print_xbee(t_wait-i)
                time.sleep(1)
    except Exception as e:
        tb = sys.exc_info()[2]
        print_xbee("message:{0}".format(e.with_traceback(tb)))
        print_xbee('#####-----Error(setup)-----#####')
        print_xbee('#####-----Error(setup)-----#####\n \n')
    #######-----------------------------------------------------------########

    #######--------------------------Release--------------------------#######
    print_xbee('#####-----Release Phase start-----#####')
    other.log(log_phase, "2", "Release Phase Started",
              datetime.datetime.now(), time.time() - t_start)
    phase = other.phase(log_phase)
    print_xbee(f'Phase:\t{phase}')
    if phase == 2:
        t_release_start = time.time()
        i = 1
        try:
            while time.time() - t_release_start <= t_out_release:
                print_xbee(f'loop_release\t {i}')
                press_count_release, press_judge_release = release_land.pressdetect_release(thd_press_release,t_delta_release)
                print_xbee(
                    f'count:{press_count_release}\tjudge{press_judge_release}')
                other.log(log_release, datetime.datetime.now(), time.time() - t_start,
                          bme280.bme280_read(), press_count_release, press_judge_release)
                a = bme280.bme280_read()
                str_trans(a)
                if press_judge_release == 1:
                    print_xbee('Release\n \n')
                    print("release")
                    break
                else:
                    print_xbee('Not Release\n \n')
                    print("not release")
                i += 1
            else:
                print_xbee('##--release timeout--##')
            print_xbee("######-----Released-----##### \n \n")
        except Exception as e:
            tb = sys.exc_info()[2]
            print_xbee("message:{0}".format(e.with_traceback(tb)))
            print_xbee('#####-----Error(Release)-----#####')
            print_xbee('#####-----Error(Release)-----#####\n \n')

    #######--------------------------Landing--------------------------#######
    try:
        print_xbee('#####-----Landing phase start-----#####')
        other.log(log_phase, '3', 'Landing phase',
                  datetime.datetime.now(), time.time() - t_start)
        phase = other.phase(log_phase)
        print_xbee(f'Phase:\t{phase}')
        if phase == 3:
            print_xbee(
                f'Landing Judgement Program Start\t{time.time() - t_start}')
            t_land_start = time.time()
            i = 1
            while time.time() - t_land_start <= t_out_land:
                print_xbee(f"loop_land\t{i}")
                press_count_land, press_judge_land = release_land.pressdetect_land(thd_press_land)
                print_xbee(
                    f'count:{press_count_land}\tjudge{press_judge_land}')
                if press_judge_land == 1:
                    print_xbee('Landed\n \n')
                    print("landed")
                    break
                else:
                    print_xbee('Not Landed\n \n')
                    print("not landed")
                other.log(log_landing, datetime.datetime.now(), time.time() - t_start, bme280.bme280_read())
                str_trans(a)
                i += 1
            else:
                print_xbee('Landed Timeout')
            other.log(log_landing, datetime.datetime.now(), time.time() - t_start, bme280.bme280_read(),
                      'Land judge finished')
            print_xbee('######-----Landed-----######\n \n')
    except Exception as e:
        tb = sys.exc_info()[2]
        print_xbee("message:{0}".format(e.with_traceback(tb)))
        print_xbee('#####-----Error(Landing)-----#####')
        print_xbee('#####-----Error(Landing)-----#####\n \n')
    # #######-----------------------------------------------------------########


