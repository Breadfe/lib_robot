
import odrive
import time
import math

wheel_diameter = 0.129

class MobileRobot:
    def __init__(self):
        self.my_drive = odrive.find_any()
        print('Battery Voltage is : ',str(self.my_drive.vbus_voltage))
        self.motor_right = self.my_drive.axis0.motor
        self.motor_left = self.my_drive.axis1.motor
        
        self.axis_right = self.my_drive.axis0
        self.axis_left = self. my_drive.axis1
        
        

        self.axis_right.requested_state = 8
        self.axis_left.requested_state = 8


        self.ctrl_right = self.axis_right.controller
        self.ctrl_left = self.axis_left.controller


        # Parameters
        self.ctrl_right.config.pos_gain = 20.0
        self.ctrl_left.config.pos_gain = 20.0

        # self.ctrl_right.config.vel_gain = 0.848
        # self.ctrl_left.config.vel_gain = 0.848

        self.ctrl_right.config.vel_gain = 0.9
        self.ctrl_left.config.vel_gain = 0.9

        self.ctrl_right.config.vel_integrator_gain = 0.32
        self.ctrl_left.config.vel_integrator_gain = 0.32
        #

    def vel_estimate(self):
        right_rps = self.axis_right.encoder.vel_estimate
        left_rps = self.axis_right.encoder.vel_estimate # turn/sec

        right_vel = self.rps2mps(right_rps)
        left_vel = self.rps2mps(left_rps)

        print(f'Right vel : {right_vel:.2f} m/s, Left vel : {left_vel:.2f} m/s')
    
    
    def go_forward(self, velocity):
        rps = self.mps2rps(velocity) 
        self.ctrl_right.input_vel = rps
        self.ctrl_left.input_vel = -rps

    def go_backward(self, velocity):
        rps = self.mps2rps(velocity) 
        self.ctrl_right.input_vel = -rps
        self.ctrl_left.input_vel = rps
        
    
    def turn_right(self, angular_velocity):
        pass
    
    def turn_left(self, angular_velocity):
        pass
    
    def moving_stop(self):
        self.ctrl_right.input_vel = 0
        self.ctrl_left.input_vel = 0

    def mps2rps(self, mps):
        rps = vel/(wheel_diameter*math.pi) # wheel 2*radius = 0.129m
        return rps

    def rps2mps(self, rps):
        mps = wheel_diameter*math.pi*rps
        return mps

if __name__ == '__main__':
    try:
        robot = MobileRobot()
        vel = 1   # m/s

        robot.go_forward(vel)
        for _ in range(10):
            robot.vel_estimate()
            time.sleep(0.2)
        robot.moving_stop()
        time.sleep(1)
        robot.go_backward(vel)
        for _ in range(10):
            robot.vel_estimate()
            time.sleep(0.2)
        # time.sleep(1)
        robot.moving_stop()

        print('done')

    except KeyboardInterrupt:
        exit()
