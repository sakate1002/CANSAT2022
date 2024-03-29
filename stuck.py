import time
import datetime
import random
from other import print_xbee

import xbee
import motor
import gps_navigate
import gps
import bmx055
import other


def ue_jug():
    ue_count = 0
    """
    ローバーの状態を確認する関数
    通常状態：True
    逆さになってる：False
    加速度センサZ軸の正負で判定する
    """
    while 1:
        za = []
        for i in range(3):
            accData = bmx055.acc_dataRead()
            za.append(accData[2])
            time.sleep(0.2)
        z = max(za)

        if z >= 7.5:
            xbee.str_trans('Upward')
            print('上だよ')
            break
        else:
            xbee.str_trans(f'Upside-down{ue_count}')
            print(f'下だよ{ue_count}')
            print(f'acc: {z}')
            if ue_count > 2:
                #motor.move(20, -25, 1, False)
                motor.move(85, -85, 1, False)
            elif ue_count > 4:
                #motor.move(50, -65, 1, False)
                motor.move(90, -90, 1, False)
            elif ue_count > 6:
                
                #motor.move(70, -90, 1, False)
                motor.move(95, -95, 1, False)
            else:
                #motor.move(11, -13, 1, False)
                motor.move(80, -80, 1, False)
            time.sleep(2)
            ue_count += 1

def ue_jugkai():
    ue_count = 0
    """
    ローバーの状態を確認する関数
    通常状態：True
    逆さになってる：False
    加速度センサZ軸の正負で判定する
    """
    while 1:
        xa = []
        za = []
        for i in range(3):
            accData = bmx055.acc_dataRead()
            xa.append(accData[0])
            za.append(accData[2])
            time.sleep(0.2)
        x = max(xa)
        z = max(za)

        if z >= 7.5 and x > 0:
            xbee.str_trans('Upward')
            print('上だよ')
            break
        else:
            xbee.str_trans(f'Upside-down{ue_count}')
            print(f'下だよ{ue_count}')
            print(f'acc: {z}')
            if ue_count > 2:
                #motor.move(13, -16, 0.1, False)
                motor.move(85, -85, 0.1, False)
            elif ue_count > 4:
                #motor.move(16, -19, 0.1, False)
                motor.move(90, -90, 0.1, False)
            elif ue_count > 6:
                #motor.move(19, -21, 0.1, False)
                motor.move(95, -95, 0.1, False)
            elif ue_count > 8:
                #motor.move(22, -24, 0.1, False)
                motor.move(99, -99, 0.1, False)
            else:
                #motor.move(16, 15, 0.1, False)
                motor.move(80, -80, 0.1, False)
            time.sleep(2)
            ue_count += 1

def stuck_jug(lat1, lon1, lat2, lon2, thd=1.0):
    data_stuck = gps_navigate.vincenty_inverse(lat1, lon1, lat2, lon2)
    if data_stuck['distance'] <= thd:
        print_xbee(str(data_stuck['distance']) + '----!!!    stuck   !!!')
        return False
    else:
        print_xbee(str(data_stuck['distance']) + '-----not stucked')
        return True


def random(a, b, k):
    ns = []
    while len(ns) < k:
        n = random.randint(a, b)
        if not n in ns:
            ns.append(n)
    return ns



def stuck_avoid_move(x):
    if x == 0:
        print_xbee('sutck_avoid_move():0')
        motor.move(80, 80, 5)
        motor.move(80, -80, 5)
        motor.move(40,-40,1)

    elif x == 1:
        print_xbee('sutck_avoid_move():1')
        motor.move(-60, -60, 5)
        motor.move(-80, 80, 5)
        motor.move(40,-40,1)
        
    elif x == 2:
        print_xbee('sutck_avoid_move():2')
        motor.move(100, 100, 5)
        motor.move(80, -80, 5)
        motor.move(40,-40,1)

    elif x == 3:
        print_xbee('sutck_avoid_move():3')
        motor.move(-100, -100, 5)
        motor.move(100, -100, 5)
        motor.move(40,-40,1)

    elif x == 4:
        print_xbee('sutck_avoid_move():4')
        motor.move(-40, -40, 5)
        motor.move(80, -80, 5)
        motor.move(40,-40,1)

    elif x == 5:
        print_xbee('sutck_avoid_move():5')
        motor.move(40, 40, 5)
        motor.move(100, -100, 5)
        motor.move(40,-40,1)

    elif x == 6:
        print_xbee('sutck_avoid_move():6')
        motor.move(100, 100, 5)
        motor.move(100, -100, 5)
        motor.move(40,-40,1)



def stuck_avoid():
    print_xbee('start stuck  avoid')
    flag = False
    while 1:
        lat_old, lon_old = gps.location()
        # 0~6
        for i in range(7):
            stuck_avoid_move(i)
            lat_new, lon_new = gps.location()
            bool_stuck = stuck_jug(lat_old, lon_old, lat_new, lon_new, 1)
            if bool_stuck == True:
                flag = True
                break
        if flag:
            break
        # 3,2,1,0
        for i in range(7):
            stuck_avoid_move(7 - i)
            lat_new, lon_new = gps.location()
            bool_stuck = stuck_jug(lat_old, lon_old, lat_new, lon_new, 1)
            if bool_stuck == False:
                flag = True
                break
        if flag:
            break
        random = random(0, 6, 7)
        for i in range(7):
            stuck_avoid_move(random[i])
            lat_new, lon_new = gps.location()
            bool_stuck = stuck_jug(lat_old, lon_old, lat_new, lon_new, 1)
            if bool_stuck == False:
                flag = True
                break
        if flag:
            break
    print_xbee('complete stuck avoid')


if __name__ == '__main__':
    motor.setup()
    ue_jug()
    while 1:
        a = int(input('出力入力しろ'))
        b = float(input('時間入力しろ'))
        motor.move(a, a, b)
