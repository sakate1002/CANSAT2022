import pigpio
import time
import traceback
import sys

AIN1 = 13
AIN2 = 19
PWMA = 18

pi1 = pigpio.pi()
pi1.set_mode(AIN1, pigpio.OUTPUT)
pi1.set_mode(AIN2, pigpio.OUTPUT)
pi1.set_mode(PWMA,pigpio.OUTPUT)

motor_prior_c = 0	#Motor Speed Prior

def motor(c, t = 0.001, mode = 0):
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

				#print(motorPL, motorPR)
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
			motorPL = int(center * 10000)

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

if __name__ == "__main__":
	try:
		#motor(50, 0, 3)
		#motor(0, 50, 3)
		#motor(-50, 0, 3)
		#motor(0, -50, 3)
		#motor(0, 0, 2, 0)
		#motor_stop()
		f = 0
		while 1:
			try:
				if f == 0:
					C = float(input("input center motor "))
					f = 1
					if C > 100 or C < -100:
						f = 1
				if f == 1:
					T = float(input("input time "))
					f = 2
				if f == 2:
					M = float(input("input mode "))
					if M == 0 or M == 1:
						motor(C, T, M)
						motor(0, 0, 2)
						motor_stop()
						f = 0
					else:
						f = 3
			except KeyboardInterrupt:
				print("Emergency!")
				motor(0, 0, 3)
				motor_stop()
				sys.exit()
			except:
				pass
	except KeyboardInterrupt:
		motor(0, 0, 3)
		motor_stop()
	except:
		print(traceback.format_exc())
		motor_stop()

		