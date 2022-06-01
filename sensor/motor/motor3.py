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

motor_prior_l = 0	#Left Motor Speed Prior
motor_prior_r = 0	#Right Motor Speed Prior

def motor(left, right, t = 0.001, mode = 0):
	global motor_prior_l
	global motor_prior_r
	motorPL = 0.0
	motorPR = 0.0

	#if motor wiring changed, check these val
	left = left * (-1.0)
	right = right * (-1.0)

	t1 = time.time()
	while(time.time() - t1 < t):
		if mode == 2:
			while left + 10.0 < motor_prior_l:
				motorPL = motor_prior_l + 3
				motorPR = motor_prior_r + 3
				motor_prior_l = motorPL
				motor_prior_r = motorPR
				motorPL = int(motorPL * 10000)
				motorPR = int(motorPR * 10000)

				pi1.write(AIN1, 1)
				pi1.write(AIN2, 0)

				#print(motorPL, motorPR)
				pi1.hardware_PWM(PWMA, 500, abs(motorPL))
			mode = 0

		#print(motor_prior_l, motor_prior_r)
		if left < motor_prior_l:
			motorPL = motor_prior_l  - 1
		elif left > motor_prior_l:
			motorPL = motor_prior_l + 1
		else:
			motorPL = motor_prior_l

		if right < motor_prior_r:
			motorPR = motor_prior_r - 1
		elif right > motor_prior_r:
			motorPR = motor_prior_r + 1
		else :
			motorPR = motor_prior_r

		motor_prior_l = motorPL
		motor_prior_r = motorPR
		#print(str(motorPL) + "\t" + str(motorPR))
		motorPL = int(motorPL * 10000)
		motorPR = int(motorPR * 10000)

		if(mode == 1):
			motorPL = int(left * 10000)
			motorPR = int(right * 10000)

		if motorPL > 0:
			pi1.write(AIN1, 1)
			pi1.write(AIN2, 0)
		elif motorPL < 0:
			pi1.write(AIN1, 0)
			pi1.write(AIN2, 1)
		else:
			pi1.write(AIN1, 0)
			pi1.write(AIN2, 0)

		#print(motorPL, motorPR)
		pi1.hardware_PWM(PWMA, 500, abs(motorPL))

		if(mode == 1):
			time.sleep(t)
		else:
			time.sleep(0.005)

	return [motorPL, motorPR]

def motor_stop():
	pi1.hardware_PWM(PWMA, 500, 0)
	pi1.hardware_PWM(PWMB, 500, 0)

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
					L = float(input("input left motor "))
					f = 1
					if L > 100 or L < -100:
						f = 0
				if f == 1:
					R = float(input("input right motor "))
					f = 2
					if R > 100 or L < -100:
						f = 1
				if f == 2:
					T = float(input("input time "))
					f = 3
				if f == 3:
					M = float(input("input mode "))
					if M == 0 or M == 1:
						motor(L, R, T, M)
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

		