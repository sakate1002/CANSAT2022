from gpiozero import Motor
import time
import stuck

def setup2():
    """
    motorを使うときに必要な初期化を行う関数
    """
    global motor_c
    Cpin1, Cpin2 = 
    motor_c = Motor(Cpin1, Cpin2)

def motor_continue2(strength_c):
    """
    モータを連続的に動かすための関数
    引数は-100~100
    """
    strength_c = strength_c / 100
    if strength_c >= 0:
        motor_c.forward(strength_c)
        
    # 後進
    elif strength_c < 0:
        motor_c.backward(abs(strength_c))

def motor_stop2(x=1):
    """
    motor_move()とセットで使用
    """
    motor_c.stop()
    time.sleep(x)

def motor_move2(strength_c, t_moving):
    """
    引数は左のmotorの強さ、右のmotorの強さ、走る時間。
    strength_l、strength_rは-1~1で表す。負の値だったら後ろ走行。
    必ずmotor_stop()セットで用いる。めんどくさかったら下にあるmotor()を使用
    """
    strength_c = strength_l / 100
    # 前進するときのみスタック判定
    if strength_c >= 0:
        motor_c.forward(strength_c)
        time.sleep(t_moving)
    # 後進
    elif strength_c < 0:
        motor_c.backward(abs(strength_c))
        time.sleep(t_moving)

def deceleration2(strength_c):
    """
    穏やかに減速するための関数
    """
    for i in range(10):
        coefficient_power = 10 - i
        coefficient_power /= 10
        motor_move2(strength_c * coefficient_power, 0.1)
        if i == 9:
            motor_stop2(0.1)

def move2(strength_c, t_moving, ue=False):
    """
    一定時間モータを動かすための関数
    strengthは-100~100
    t_movingはモータを動かす時間
    ueは機体が逆さまかどうか判断するのをmotor関数内で行うかどうか(True/False)
    """
    if ue:
        stuck.ue_jug()
    motor_move2(strength_c, t_moving)

if __name__ == '__main__':
    setup2()
    while 1:
        command = input('操作\t')
        if command == 'a':
            move2(40, 80, 2)
        elif command == 'w':
            move2(80, 80, 2)
        elif command == 'd':
            move2(80, 40, 2)
        elif command == 's':
            move2(-50, -50, 2)
        elif command == 'manual':
            l = float(input('左の出力は？'))
            r = float(input('右の出力は？'))
            t = float(input('移動時間は？'))
            time.sleep(0.8)
            move2(l, r, t)
        else:
            print('もう一度入力してください')