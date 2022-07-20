import datetime
import time

import mission
import gps_navigate
import gps
import bmx055
import motor #motor.move(l,r,t)
import motor3
import xbee
import calibration
import stuck
import other


def angle_goal(magx_off, magy_off, lon2, lat2):
    """
    ゴールとの相対角度を算出する関数

    -180~180度
    """
    magdata = bmx055.mag_dataRead()
    mag_x = magdata[0]
    mag_y = magdata[1]
    theta = calibration.angle(mag_x, mag_y, magx_off, magy_off)
    direction = calibration.calculate_direction(lon2, lat2) #逆開放によるゴールまでの距離の計算
    azimuth = direction["azimuth1"] #ゴールまでの方位角
    angle_relative = azimuth - theta #相対角度 = 方位角 - ローバの向きと北の偏角
    if angle_relative >= 0:
        angle_relative = angle_relative if angle_relative <= 180 else angle_relative - 360
    else:
        angle_relative = angle_relative if angle_relative >= -180 else angle_relative + 360
    return angle_relative


def adjust_direction(theta, magx_off, magy_off, lon2, lat2):
    """
    方向調整
    """
    stuck_count = 1 #調整阪手
    t_small = 0.1 #調整阪手
    t_big = 0.2 #調整阪手
    force = 35 #調整阪手
    while 30 < theta <= 180 or -180 < theta < -30: #ゴールとの相対角度が-30°~30°未満になるまでループ
        if stuck_count >= 16:
            ##方向調整が不可能な場合はスタックしたとみなして、もう一度キャリブレーションからスタート##
            other.print_xbee(
                "!!!!can't ajdust direction.   start stuck avoid!!!!!")
            stuck.stuck_avoid()
            magx_off, magy_off = calibration.cal(40, 40, 30)
            stuck_count = -1
        if stuck_count % 7 == 0:
            other.print_xbee('Increase output')
            force += 10
        if 30 <= theta <= 60: #さらに細かく方向調整するのもありかも？阪手
            other.print_xbee(
                f'theta = {theta}\t---rotation_ver1 (stuck:{stuck_count})')
            motor.move(force, force, t_small)

        elif 60 < theta <= 180:
            other.print_xbee(
                f'theta = {theta}\t---rotation_ver2 (stuck:{stuck_count})')
            motor.move(force, force, t_big)

        elif -60 <= theta <= -30:
            other.print_xbee(
                f'theta = {theta}\t---rotation_ver3 (stuck:{stuck_count})')
            motor.move(-force, -force, t_small)
        elif -180 < theta < -60:
            other.print_xbee(
                f'theta = {theta}\t---rotation_ver4 (stuck:{stuck_count})')
            motor.move(-force, -force, t_big)
        else:
            print(f'theta = {theta}')

        stuck_count += 1
        stuck.ue_jug()
        theta = angle_goal(magx_off, magy_off, lon2, lat2) #ゴールとの相対角度 = theta　阪手
        print('Calculated angle_relative: {theta}')
        time.sleep(1)
    other.print_xbee(f'theta = {theta} \t rotation finished!!!')


def drive(lon2, lat2, thd_distance, t_adj_gps, logpath='/home/cansat2022/CANSAT2022/log/gpsrunningLog', t_start=0):
    """
    GPS走行の関数
    統合する場合はprintをXbee.str_transに変更，other.saveLogのコメントアウトを外す
    """
    strength_l = 0
    strength_r = 0
    direction = calibration.calculate_direction(lon2, lat2)
    goal_distance_old = direction['distance']
    mission_distance = int(goal_distance_old) * 0.5
    goal_distance = direction['distance']
    
    while goal_distance >= thd_distance:

        t_stuck_count = 1
        stuck.ue_jug()
        goal_distance = direction['distance']
        mission_count = 0
        if mission_count < 1:
            if (mission_distance - 10) < goal_distance and goal_distance < (mission_distance + 10):
                adjust_direction(theta, magx_off, magy_off, lon2, lat2)
                mission.mission()
                mission_count += 1
                pass

            else:
                pass
        
        else:
            pass

        # ------------- calibration -------------#
        # xbee.str_trans('calibration Start')
        other.print_xbee('##--calibration Start--##\n')
        magx_off, magy_off = calibration.cal(40, 40, 30)
        print(f'magx_off: {magx_off}\tmagy_off: {magy_off}\n')
        theta = angle_goal(magx_off, magy_off, lon2, lat2)
        adjust_direction(theta, magx_off, magy_off, lon2, lat2)

        t_cal = time.time()
        lat_old, lon_old = gps.location()
        while time.time() - t_cal <= t_adj_gps: #ここの秒数がキャリブレーションを次に行うまでの時間になる
            lat1, lon1 = gps.location()
            lat_new, lon_new = lat1, lon1
            direction = gps_navigate.vincenty_inverse(lat1, lon1, lat2, lon2)
            azimuth, goal_distance = direction["azimuth1"], direction["distance"]
            other.print_xbee(
                f'lat: {lat1}\tlon: {lon1}\tdistance: {goal_distance}\tazimuth: {azimuth}\n')

            if t_stuck_count % 8 == 0:
                ##↑何秒おきにスタックジャッジするかを決める##
                if stuck.stuck_jug(lat_old, lon_old, lat_new, lon_new, 2): #スタックの基準（閾値は調整）サカイェ
                    pass
                else:
                    stuck.stuck_avoid()
                    pass
                lat_old, lon_old = gps.location()

            if goal_distance <= thd_distance:
                break
            else:
                for _ in range(25):
                    magdata = bmx055.mag_dataRead()
                    mag_x = magdata[0]
                    mag_y = magdata[1]

                    theta = calibration.angle(mag_x, mag_y, magx_off, magy_off)
                    angle_relative = azimuth - theta
                    if angle_relative >= 0:
                        angle_relative = angle_relative if angle_relative <= 180 else angle_relative - 360
                    else:
                        angle_relative = angle_relative if angle_relative >= -180 else angle_relative + 360
                    theta = angle_relative
                    
                    if theta >= 0:
                        if theta <= 15:
                            adj = 0
                        elif theta <= 90:
                            adj = 20
                        else:
                            adj = 30
                    else:
                        if theta >= -15:
                            adj = 0
                        elif theta >= -90:
                            adj = -20
                        else:
                            adj = -30
                    print(f'angle ----- {theta}')
                    strength_l, strength_r = 65 + adj, -70 - adj
                    motor.motor_continue(strength_l, strength_r)
                    time.sleep(0.04)
            t_stuck_count += 1
            other.log(logpath, datetime.datetime.now(), time.time() - t_start, lat1, lon1, direction['distance'], angle_relative)
            motor.deceleration(strength_l, strength_r)
            time.sleep(2)
            lat_new, lon_new = gps.location()

        direction = calibration.calculate_direction(lon2, lat2)
        goal_distance = direction['distance']
        other.print_xbee(f'-----distance: {goal_distance}-----')

if __name__ == '__main__':
    # lat2 = 35.918548
    # lon2 = 139.908896
    # lat2 = 35.9234892
    # lon2 = 139.9118744
    #lat2, lon2 = 35.921247, 139.910953
    lat2 = 35.9240157
    lon2 = 139.9112665
    gps.open_gps()
    bmx055.bmx055_setup()
    motor.setup()

    drive(lon2, lat2, thd_distance=5, t_adj_gps=20) 