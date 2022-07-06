import sys
sys.path.append('/home/cansat2022/Desktop/CANSAT2022/SensorModule/gps')
sys.path.append('/home/cansat2022/Desktop/CANSAT2022/SensorModule/communication')
sys.path.append('/home/cansat2022/Desktop/CANSAT2022/SensorModule/9-axis')
sys.path.append('/home/cansat2022/Desktop/CANSAT2022/SensorModule/camera')
sys.path.append('/home/cansat2022/Desktop/CANSAT2022/SensorModule/melt')
sys.path.append('/home/cansat2022/Desktop/CANSAT2022/SensorModule/environmental')
sys.path.append('/home/cansat2022/Desktop/CANSAT2022/SensorModule/motor')
sys.path.append('/home/cansat2022/Desktop/CANSAT2022/SensorModule/illuminance')
sys.path.append('/home/cansat2022/Desktop/CANSAT2022/detection')
sys.path.append('/home/cansat2022/Desktop/CANSAT2022/other')
sys.path.append('/home/cansat2022/Desktop/CANSAT2022/test')
sys.path.append('/home/cansat2022/Desktop/CANSAT2022/calibration')

import mission
import time
import take
import datetime
import pigpio
import xbee
import bmx055
import bme280
import gps
import melt
import paradetection
import paraavoidance
import other
import calibration
import release
import land
import motor
import stuck
import escape
from other import print_xbee

dateTime = datetime.datetime.now()

# variable for timeout
t_out_release = 120
t_out_land = 30
t_out_release_safe = 1000

# variable for release
thd_press_release = 0.3
t_delta_release = 1  #時間を伸ばす！エレベーター

# variable for landing
thd_press_land = 0.15

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
log_phase = other.filename('/home/cansat2022/Desktop/CANSAT2022/log/phaseLog', 'txt')
log_release = other.filename(
    '/home/cansat2022/Desktop/CANSAT2022/log/releaselog', 'txt')
log_landing = other.filename(
    '/home/cansat2022/Desktop/CANSAT2022/log/landingLog', 'txt')
log_phototest = other.filename('/home/cansat2022/Desktop/CANSAT2022/log/phototest', 'txt')
log_melting = other.filename(
    '/home/cansat2022/Desktop/CANSAT2022/log/meltingLog', 'txt')
log_paraavoidance = other.filename(
    '/home/cansat2022/Desktop/CANSAT2022/log/paraAvoidanceLog', 'txt')
log_magrunning = other.filename(
    '/home/cansat2022/Desktop/CANSAT2022/log/MagrunningLog', 'txt')
path_paradete = '/home/cansat2022/Desktop/CANSAT2022/photo_paradete/paradete'

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
                press_count_release, press_judge_release = release.pressdetect_release(
                    thd_press_release, t_delta_release)
                print_xbee(
                    f'count:{press_count_release}\tjudge{press_judge_release}')
                other.log(log_release, datetime.datetime.now(), time.time() - t_start, gps.gps_data_read(),
                          bme280.bme280_read(), press_count_release, press_judge_release)
                if press_judge_release == 1:
                    print_xbee('Release\n \n')
                    break
                else:
                    print_xbee('Not Release\n \n')
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
                press_count_release, press_judge_release = land.pressdetect_land(
                    thd_press_land)
                print_xbee(
                    f'count:{press_count_release}\tjudge{press_judge_release}')
                if press_judge_release == 1:
                    print_xbee('Landed\n \n')
                    break
                else:
                    print_xbee('Not Landed\n \n')
                other.log(log_landing, datetime.datetime.now(), time.time() - t_start,
                          gps.gps_data_read(), bme280.bme280_read())
                i += 1
            else:
                print_xbee('Landed Timeout')
            other.log(log_landing, datetime.datetime.now(), time.time() - t_start, gps.gps_data_read(), bme280.bme280_read(),
                      'Land judge finished')
            print_xbee('######-----Landed-----######\n \n')
    except Exception as e:
        tb = sys.exc_info()[2]
        print_xbee("message:{0}".format(e.with_traceback(tb)))
        print_xbee('#####-----Error(Landing)-----#####')
        print_xbee('#####-----Error(Landing)-----#####\n \n')
    # #######-----------------------------------------------------------########

    #######--------------------------Photo Test----------------------#######

    print_xbee('#####-----Photo test start####')
    other.log(log_phase, '4', 'Phototest phase start',
              datetime.datetime.now(), time.time() - t_start)
    phase = other.phase(log_phase)
    print_xbee(f'Phase:\t{phase}')
    if phase == 4:
        other.log(log_phototest, datetime.datetime.now(), time.time() - t_start,
                  gps.gps_data_read(), "Phototest Start")
        take.picture()
        other.log(log_phototest, datetime.datetime.now(), time.time() - t_start,
                  gps.gps_data_read(), "Phototest Finished")
    print_xbee('########-----Photed-----#######\n \n')
    #######--------------------------Escape--------------------------#######

    print_xbee('#####-----Melting phase start#####')
    other.log(log_phase, '5', 'Melting phase start',
              datetime.datetime.now(), time.time() - t_start)
    phase = other.phase(log_phase)
    print_xbee(f'Phase:\t{phase}')
    if phase == 5:
        # 落下試験用の安全対策（落下しないときにXbeeでプログラム終了)
        while time.time() - t_release_start <= t_out_release_safe:
            xbee.str_trans('continue? y/n \t')
            if xbee.str_receive() == 'y':
                break
            elif xbee.str_receive() == 'n':
                xbee.str_trans('Interrupted for safety')
                exit()
        other.log(log_melting, datetime.datetime.now(), time.time() - t_start,
                  gps.gps_data_read(), "Melting Start")
        escape.escape()
        other.log(log_melting, datetime.datetime.now(), time.time() - t_start,
                  gps.gps_data_read(), "Melting Finished")
    print_xbee('########-----Melted-----#######\n \n')
    # except Exception as e:
    #     tb = sys.exc_info()[2]
    #     print_xbee("message:{0}".format(e.with_traceback(tb)))
    #     print_xbee('#####-----Error(melting)-----#####')
    #     print_xbee('#####-----Error(melting)-----#####\n \n')
    #######-----------------------------------------------------------########

    #######--------------------------Center Motor Check--------------------------#######

    print_xbee('#####-----Cmotor phase start#####')
    other.log(log_phase, '6', 'Cmotor phase start',
              datetime.datetime.now(), time.time() - t_start)
    phase = other.phase(log_phase)
    print_xbee(f'Phase:\t{phase}')
    if phase == 6:
        other.log(log_melting, datetime.datetime.now(), time.time() - t_start,
                  gps.gps_data_read(), "Cmotor Start")
        mission()
        other.log(log_melting, datetime.datetime.now(), time.time() - t_start,
                  gps.gps_data_read(), "Cmotor Finished")
    print_xbee('########-----Cmotored-----#######\n \n')

    #######--------------------------Paraavo--------------------------#######

    print_xbee('#####-----Para avoid start-----#####')
    other.log(log_phase, '6', 'Paraavo phase start',
              datetime.datetime.now(), time.time() - t_start)
    phase = other.phase(log_phase)
    print_xbee(f'Phase:\t{phase}')
    count_paraavo = 0
    if phase == 6:
        while count_paraavo < 3:
            flug, area, gap, photoname = paradetection.para_detection(
                path_paradete, 320, 240, 200, 10, 120, 1)
            print_xbee(
                f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}\n \n')
            other.log(log_paraavoidance, datetime.datetime.now(), time.time() -
                      t_start, gps.gps_data_read(), flug, area, gap, photoname)
            paraavoidance.parachute_avoidance(flug, gap)
            if flug == -1 or flug == 0:
                count_paraavo += 1
    print_xbee('#####-----ParaAvo Phase ended-----##### \n \n')
    # except Exception as e:
    #     tb = sys.exc_info()[2]
    #     print_xbee("message:{0}".format(e.with_traceback(tb)))
    #     print_xbee('#####-----Error(paraavo)-----#####')
    #     print_xbee('#####-----Error(paraavo)-----#####\n \n')
    #######-----------------------------------------------------------########

    