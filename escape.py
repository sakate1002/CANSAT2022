import motor
import melt2
import stuck

def escape(t_melt=3):
    melt2.down(t_melt)
    stuck.ue_jug()

if __name__ == '__main__':
    motor.setup()
    escape()