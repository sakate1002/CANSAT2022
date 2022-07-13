import sys
sys.path.append('/home/cansat2022/Desktop/CANSAT2022/bme280')

import bme280
import time


def pressdetect_release(thd_press_release, t_delta_release):
    global press_count_release
    global press_judge_release
    try:
        pressdata = bme280.bme280_read()
        prevpress = pressdata[1]
        time.sleep(t_delta_release) #５秒待って次の気圧の値を読むよ
        pressdata = bme280.bme280_read()
        latestpress = pressdata[1]
        deltP = latestpress - prevpress #初めにとった気圧-後にとった気圧
        if 0.0 in pressdata:
            print("bme280error!")
            press_judge_release = 2
            press_count_release = 0
        elif deltP > thd_press_release:
            press_count_release += 1
            if press_count_release > 1:
                press_judge_release = 1
                print("pressreleasejudge")
        else:
            press_count_release = 0
    except:
        press_count_release = 0
        press_judge_release = 2
    return press_count_release, press_judge_release


def pressdetect_land(anypress):
    """
    気圧情報による着地判定用
    引数はどのくらい気圧が変化したら判定にするかの閾値
    """
    global presscount_land
    global pressjudge_land
    try:
        pressdata = bme280.bme280_read()
        Prevpress = pressdata[1]
        time.sleep(1) #1秒待って次の気圧の値を読むよ
        pressdata = bme280.bme280_read()
        Latestpress = pressdata[1]
        deltP = abs(Latestpress - Prevpress) #初めにとった気圧-後にとった気圧
        if 0.0 in pressdata:
            print("bme280error!")
            presscount_land = 0
            pressjudge_land = 2
        elif deltP < anypress:
            presscount_land += 1
            if presscount_land > 4:
                pressjudge_land = 1
                print("presslandjudge")
        else:
            presscount_land = 0
    except:
        presscount_land = 0
        pressjudge_land = 2
    return presscount_land, pressjudge_land



if __name__ == '__main__':
    bme280.bme280_setup()
    bme280.bme280_calib_param()
    startTime = time.time()
    #放出判定用
    press_count_release = 0
    press_judge_release = 0
    #着地判定用
    press_count_land = 0
    press_judge_land = 0

    try:
        while 1:
            press_count_release, press_judge_release = pressdetect_release(0.3) #閾値0.3
            print(f'count{press_count_release}\tjudge{press_judge_release}')
            if press_judge_release == 1:
                print('release detected')
                break
    except KeyboardInterrupt:
        pass

    try:
        while 1:
            press_count_land, press_judge_land = pressdetect_land(0.1) #閾値0.1
            print(f'count{press_count_land}\tjudge{press_judge_land}')
            if press_judge_land == 1:
                print('land detected')
                break
    except KeyboardInterrupt:
        pass


    # try:
    #     while 1:
    #         presscount_release, pressjudge_release = pressdetect_release(0.3)
    #         print(f'count{presscount_release}\tjudge{pressjudge_release}')
    #         if pressjudge_release == 1:
    #             print('release detected')
    #             break
    #
    #     while 1:
    #         presscount_land, pressjudge_land = pressdetect_land(0.1)
    #         print(f'count{presscount_land}\tjudge{pressjudge_land}')
    #         if pressjudge_land == 1:
    #             print('land detected')
    #             break
    #
    #     print('finished')
    # except KeyboardInterrupt:
    #     print('interrupted')
    # except:
    #     print('finished')