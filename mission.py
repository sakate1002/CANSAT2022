import pigpio
import picamera
import time
import traceback
import sys
import os


AIN1 = 13
AIN2 = 19
PWMA = 18

pi1 = pigpio.pi()
pi1.set_mode(AIN1, pigpio.OUTPUT)
pi1.set_mode(AIN2, pigpio.OUTPUT)
pi1.set_mode(PWMA, pigpio.OUTPUT)

motor_prior_c = 0	#Motor Speed Prior

def motor(center, t = 0.001, mode = 0):
	global motor_prior_c
	motorPC = 0.0

	#if motor wiring changed, check these val
	center = center * (-1.0)

	t1 = time.time()
	while(time.time() - t1 < t):
		if mode == 2:
			while center + 10.0 < motor_prior_c:
				motorPC = motor_prior_c + 3
				motor_prior_c = motorPC
				motorPC = int(motorPC * 10000)

				pi1.write(AIN1, 1)
				pi1.write(AIN2, 0)

				#print(motorPC)
				pi1.hardware_PWM(PWMA, 500, abs(motorPC))
			mode = 0

		#print(motor_prior_c)
		if center < motor_prior_c:
			motorPC = motor_prior_c  - 1
		elif center > motor_prior_c:
			moterPC = motor_prior_c + 1
		else:
			motorPC = motor_prior_c

		motor_prior_c = motorPC

		#print(str(motorPL) + "\t" + str(motorPR))
		motorPC = int(motorPC * 10000)

		if(mode == 1):
			motorPC = int(center * 10000)

		if motorPC > 0:
			pi1.write(AIN1, 1)
			pi1.write(AIN2, 0)
		elif motorPC < 0:
			pi1.write(AIN1, 0)
			pi1.write(AIN2, 1)
		else:
			pi1.write(AIN1, 0)
			pi1.write(AIN2, 0)

		#print(motorPL, motorPR)
		pi1.hardware_PWM(PWMA, 500, abs(motorPC))

		if(mode == 1):
			time.sleep(t)
		else:
			time.sleep(0.005)

	return [motorPC]

def motor_stop():
	pi1.hardware_PWM(PWMA, 500, 0)


def picture(path, width=320, height=240):
    
    #/dir/dir/dir/fileの時にfileの前にディレクトリが存在するか調べる関数
    #引数は/dir/dir/dir/fileの形のパス
    def dir(path):
        fd = path.rfind('/')
        dir = path[:fd]
        is_dir = os.path.isdir(dir)
        return is_dir
    
    #dir関数で調べた結果ディレクトリが存在しない場合はそのディレクトリを作成する
    def make_dir(path):
        if not dir(path):
            fd = path.rfind('/')
            directory = path[:fd]
            os.mkdir(directory)
            print('******Directory is maked******')
        else:
            print('**Directory is exist**')
    
    #ファイル名に番号をつけるための関数
    #引数f:つけたいファイル名
    #引数ext:ファイルの拡張子
    #戻り値f:ファイル名+0000.拡張子
    #戻り値の番号は増えていく
    def filename(f, ext):
        i = 0
        while 1:
            num = ""
            if len(str(i)) <= 4:
                for j in range(4 - len(str(i))):
                    num = num + "0"
                num = num + str(i)
            else:
                num = str(i)
            if not (os.path.exists(f + num + "." + ext)):
                break
            i = i + 1
        f = f + num + "." + ext
        return f

    try:
        make_dir(path)
        with picamera.PiCamera() as camera:
            #取得した画像の回転
            camera.rotation = 270
            #取得する画像の解像度を設定→どのような基準で設定するのか
            #使用するカメラの解像度は静止画解像度で3280×2464
            camera.resolution = (width, height)
            #指定したパスを持つファイルを作成
            filepath = filename(path, 'jpg')
            #そのファイルに取得した画像を入れる
            camera.capture(filepath)
    #パスが切れているときはNULL
    except picamera.exc.PiCameraMMALError:
        filepath = "Null"
        time.sleep(0.8)
    #そのほかのエラーの時はNULL
    except:
        print(traceback.format_exc())
        time.sleep(0.1)
        filepath = "Null"
    return filepath


if __name__ == "__main__":
    photoName = picture('photo/photo', 320, 240)
    motor(30, 5)
    motor_stop()
    photoName = picture('photo/photo', 320, 240)
    motor(-30, 5)
    motor_stop()