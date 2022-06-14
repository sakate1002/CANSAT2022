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

import time
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

pi = pigpio.pi()

# variable for timeout　ちな調整可能
t_setup = 60
t_out_release = 60
t_out_release_safe = 1000
t_out_land = 40


# variable for releasejudge ちな調整可能
thd_press_release = 0.3
press_count_release = 0
press_judge_release = 0
t_delta_release = 1.3  # エレベータ:3    パラシュート落下:0.9 ?

# variable for landjudgment ちな調整可能
thd_press_land = 0.15
press_count_land = 0
press_judge_land = 0

# variable used for ParaDetection ちな調整可能
LuxThd = 100
imgpath_para = "/home/cansat2022/Desktop/Cansat2021ver/photostorage/paradetection"

# path for save
phaseLog = "/home/cansat2022/Desktop/CANSAT2022/log/phaseLog"
waitingLog = "/home/cansat2022/Desktop/CANSAT2022/log/waitingLog.txt"
releaseLog = "/home/cansat2022/Desktop/CANSAT2022/log/releaseLog.txt"
landingLog = "/home/cansat2022/Desktop/CANSAT2022/log/landingLog.txt"
meltingLog = "/home/cansat2022/Desktop/CANSAT2022/log/meltingLog.txt"
paraAvoidanceLog = "/home/cansat2022/Desktop/CANSAT2022/log/paraAvoidanceLog.txt"
path_src_panorama = '/home/cansat2022/Desktop/CANSAT2022/panorama_src'
path_dst_panoraam = '/home/cansat2022/Desktop/CANSAT2022/panorama_dst'


def setup():
    global phaseChk
    bme280.bme280_setup()
    bme280.bme280_calib_param()
    gps.openGPS()


def close():
    gps.closeGPS()
    xbee.off()


if __name__ == '__main__':
    xbee.on()
    motor.setup()
    while 1:
        xbee.str_trans('standby\t')
        if xbee.str_receive() == 's':
            xbee.str_trans('\n')
            xbee.str_trans('#####-----Program start-----#####\n \n')
            break

    try:
        t_start = time.time()
        # ------------------- Setup Phase --------------------- #
        xbee.str_trans('#####-----Setup Phase start-----#####')
        other.saveLog(phaseLog, "1", "Setup phase", time.time() - t_start, datetime.datetime.now())
        phaseChk = other.phaseCheck(phaseLog)
        xbee.str_trans(f'Phase:\t{phaseChk}')
        setup()
        xbee.str_trans('#####-----Setup Phase ended-----##### \n \n')

        # ------------------- Waiting Phase --------------------- #
        xbee.str_trans('#####-----Waiting Phase start-----#####')
        other.saveLog(phaseLog, "2", "Waiting Phase Started", time.time() - t_start, datetime.datetime.now())
        phaseChk = other.phaseCheck(phaseLog)
        xbee.str_trans(f'Phase:\t{phaseChk}')
        # if phaseChk == 2:
        #     t_wait_start = time.time()
        #     while time.time() - t_wait_start <= t_setup:
        #         Other.saveLog(waitingLog, time.time() - t_start, GPS.readGPS(), BME280.bme280_read(), TSL2572.read())
        #         print('Waiting')
        #         Xbee.str_trans('Sleep')
        #         time.sleep(1)
        xbee.str_trans('#####-----Waiting Phase ended-----##### \n \n')

        # ------------------- Release Phase ------------------- #
        xbee.str_trans('#####-----Release Phase start-----#####')
        other.saveLog(phaseLog, "3", "Release Phase Started", time.time() - t_start, datetime.datetime.now())
        phaseChk = other.phaseCheck(phaseLog)
        xbee.str_trans(f'Phase:\t{phaseChk}')
        if phaseChk == 3:
            t_release_start = time.time()
            i = 1
            try:
                while time.time() - t_release_start <= t_out_release:
                    xbee.str_trans(f'loop_release\t {i}')
                    press_count_release, press_judge_release = release.pressdetect_release(thd_press_release,
                                                                                           t_delta_release)
                    xbee.str_trans(f'count:{press_count_release}\tjudge{press_judge_release}')
                    other.saveLog(releaseLog, datetime.datetime.now(), time.time() - t_start, gps.readGPS,
                                  bme280.bme280_read(), press_count_release, press_judge_release)
                    if press_judge_release == 1:
                        xbee.str_trans('Release\n \n')
                        break
                    else:
                        xbee.str_trans('Not Release\n \n')
                    i += 1
                else:
                    # 落下試験用の安全対策（落下しないときにXbeeでプログラム終了)
                    while time.time() - t_release_start <= t_out_release_safe:
                        xbee.str_trans('continue? y/n \t')
                        if xbee.str_receive() == 'y':
                            break
                        elif xbee.str_receive() == 'n':
                            xbee.str_trans('Interrupted for safety')
                            exit()
                    xbee.str_trans('##--release timeout--##')
            except KeyboardInterrupt:
                print('interrupted')
            xbee.str_trans("######-----Released-----##### \n \n")

        # ------------------- Landing Phase ------------------- #
        xbee.str_trans('#####-----Landing Phase start-----#####')
        other.saveLog(phaseLog, "4", "Landing Phase Started", time.time() - t_start, datetime.datetime.now())
        phaseChk = other.phaseCheck(phaseLog)
        xbee.str_trans(f'Phase\t{phaseChk}')
        if phaseChk == 4:
            xbee.str_trans(f'Landing Judgement Program Start\t{time.time() - t_start}')
            t_land_start = time.time()
            i = 1
            while time.time() - t_land_start <= t_out_land:
                xbee.str_trans(f"loop_land\t{i}")
                press_count_release, press_judge_release = land.pressdetect_land(thd_press_land)
                xbee.str_trans(f'count:{press_count_release}\tjudge{press_judge_release}')
                if press_judge_release == 1:
                    xbee.str_trans('Landed')
                    break
                else:
                    xbee.str_trans('Not Landed')
                other.saveLog(landingLog, datetime.datetime.now(), time.time() - t_start, gps.readGPS(),
                              bme280.bme280_read())
                i += 1
            else:
                xbee.str_trans('Landed Timeout')
            other.saveLog(landingLog, datetime.datetime.now(), time.time() - t_start, gps.readGPS(),
                          bme280.bme280_read(), 'Land judge finished')
            xbee.str_trans('######-----Landed-----######\n \n')

        # ------------------- Melting Phase ------------------- #
        xbee.str_trans('#####-----Melting phase start#####')
        other.saveLog(phaseLog, '5', 'Melting phase start', time.time() - t_start, datetime.datetime.now())
        phaseChk = other.phaseCheck(phaseLog)
        xbee.str_trans(f'Phase:\t{phaseChk}')
        if phaseChk == 5:
            other.saveLog(meltingLog, datetime.datetime.now(), time.time() - t_start, gps.readGPS(), "Melting Start")
            melt.down()
            time.sleep(3)
            other.saveLog(meltingLog, datetime.datetime.now(), time.time() - t_start, gps.readGPS(), "Melting Finished")
        xbee.str_trans('########-----Melted-----#######\n \n')
        # ------------------- ParaAvoidance Phase ------------------- #
        print_xbee('#####-----Para avoid start-----#####')
        other.log(log_phase, '5', 'Paraavo phase start',
                    datetime.datetime.now(), time.time() - t_start)
        phase = other.phase(log_phase)
        print_xbee(f'Phase:\t{phase}')
        count_paraavo = 0
        if phase == 5:
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
        #     Xbee.str_trans('#####-----paraavoided-----#####\n \n')

        xbee.str_trans('########--Progam Finished--##########')
        close()
    except KeyboardInterrupt:
        close()
        print("Keyboard Interrupt")
    except Exception as e:
        xbee.str_trans("error")
        close()
        other.saveLog("/home/pi/Desktop/Cansat2021ver/log/errorLog.txt", t_start - time.time(), "Error")
        tb = sys.exc_info()[2]
        print("message:{0}".format(e.with_traceback(tb)))