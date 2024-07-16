
import odrive
import time
import math
# axis_number = 0
# print('good')
# my_drive = odrive.find_any()
# print('Battery Voltage is : ',str(my_drive.vbus_voltage))

# motor = my_drive.axis0.motor
# axis_right = my_drive.axis0
# axis_left = my_drive.axis1
# ctrl_right = axis_right.controller
# ctrl_left = axis_left.controller

# print(str(my_drive.axis0.controller.pos_setpoint))
# velocity = 1



# axis.controller.input_vel = velocity
# axis2.controller.input_vel = velocity    
#         # Wait for 1 second
# time.sleep(3)
        
#         # Stop the motor
# axis.controller.input_vel = 0
# axis2.controller.input_vel = 0
#         # Wait for 1 second
# time.sleep(1)

# axis.controller.input_vel = -1

# time.sleep(3)
        
#         # Stop the motor
# axis.controller.input_vel = 0
WHEEL_DIAMETER = 0.129 # 바퀴의 지름
RIGHT_MOTOR = 0
LEFT_MOTOR = 1
FORWARD = 0
BACKWARD = 1
STOP = 2
WHEEL_TO_CENTER = 0.168  # 두 바퀴 사이의 반지름 16.8cm


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
        # self.ctrl_right.config.pos_gain = 20.0
        # self.ctrl_left.config.pos_gain = 20.0

        # # self.ctrl_right.config.vel_gain = 0.848
        # # self.ctrl_left.config.vel_gain = 0.848

        # self.ctrl_right.config.vel_gain = 0.9
        # self.ctrl_left.config.vel_gain = 0.9

        # self.ctrl_right.config.vel_integrator_gain = 0.7 #0.32
        # self.ctrl_left.config.vel_integrator_gain = 0.7
        #

    def vel_estimate(self):
        right_rps = self.axis_right.encoder.vel_estimate
        left_rps = self.axis_left.encoder.vel_estimate # turn/sec

        right_vel = self.rps2mps(right_rps)
        left_vel = -self.rps2mps(left_rps)

        print(f'Right vel : {right_vel:.2f} m/s, Left vel : {left_vel:.2f} m/s')
    
    def motor_turn(self, axis, direction, velocity = 0): # m/s input
        rps = self.mps2rps(velocity) 
        print(velocity)
        if axis == RIGHT_MOTOR:
            if direction == FORWARD:
                self.ctrl_right.input_vel = rps
            elif direction == BACKWARD:
                self.ctrl_right.input_vel = -rps
            elif direction == STOP:
                self.ctrl_right.input_vel = 0
        elif axis == LEFT_MOTOR:
            if direction == FORWARD:
                self.ctrl_left.input_vel = -rps
            elif direction == BACKWARD:
                self.ctrl_left.input_vel = rps
            elif direction == STOP:
                self.ctrl_left.input_vel = 0

    def mps2rps(self, mps):
        rps = mps/(WHEEL_DIAMETER*math.pi) # wheel 2*radius = 0.129m
        return rps

    def rps2mps(self, rps):
        mps = WHEEL_DIAMETER*math.pi*rps
        return mps
    
    ############# MOVING TEST PART DOWN #############    
    def go_forward(self, velocity):
        self.motor_turn(RIGHT_MOTOR, FORWARD, velocity)
        self.motor_turn(LEFT_MOTOR, FORWARD, velocity) # m/s input
        
    def go_backward(self, velocity):
        self.motor_turn(RIGHT_MOTOR, BACKWARD, velocity)
        self.motor_turn(LEFT_MOTOR, BACKWARD, velocity)
        
    def turn_right(self, angular_velocity):
        self.motor_turn(RIGHT_MOTOR, FORWARD, angular_velocity*WHEEL_TO_CENTER)
        self.motor_turn(LEFT_MOTOR, BACKWARD, angular_velocity*WHEEL_TO_CENTER)
        
    def turn_left(self, angular_velocity):
        self.motor_turn(RIGHT_MOTOR, BACKWARD, angular_velocity*WHEEL_TO_CENTER)
        self.motor_turn(LEFT_MOTOR, FORWARD, angular_velocity*WHEEL_TO_CENTER)
    
    def moving_stop(self):
        self.motor_turn(RIGHT_MOTOR, STOP)
        self.motor_turn(LEFT_MOTOR, STOP)

    ############# USE THIS METHOD FOR MOVING #############    
    def move_base(self, velocity, angular_velocity):
        left_motor_vel = velocity - WHEEL_TO_CENTER*angular_velocity
        right_motor_vel = velocity + WHEEL_TO_CENTER*angular_velocity
        self.motor_turn(RIGHT_MOTOR, FORWARD, right_motor_vel)
        self.motor_turn(LEFT_MOTOR, FORWARD, left_motor_vel)
        pass

if __name__ == '__main__':
    robot = None
    try:
        robot = MobileRobot()
        vel = 1   # m/s
        angular_velocity = 3 # rad/s
        # print('Go forward')
        # robot.go_forward(vel)
        # for _ in range(10):
        #     robot.vel_estimate()
        #     time.sleep(0.2)
        # print('STOP')   
        # robot.moving_stop()
        # time.sleep(1)
        # print('Go backward')
        # robot.go_backward(vel)
        # for _ in range(10):
        #     robot.vel_estimate()
        #     time.sleep(0.2)
        # # time.sleep(1)
        # print('STOP')
        # robot.moving_stop()
        # time.sleep(1)
        # print('Turn left')
        # robot.turn_left(angular_velocity)
        # for _ in range(10):
        #     robot.vel_estimate()
        #     time.sleep(0.2)
        # print('STOP')
        # robot.moving_stop()
        # print('Turn Right')
        # robot.turn_right(angular_velocity)
        # for _ in range(10):
        #     robot.vel_estimate()
        #     time.sleep(0.2)
        robot.move_base(vel, angular_velocity)
        for _ in range(10):
            robot.vel_estimate()
            time.sleep(0.2)
        
        robot.moving_stop()
    

        print('done')

    except KeyboardInterrupt:
        if robot is not None:
            robot.moving_stop()
        else:
            robot = MobileRobot()
            robot.moving_stop()
        exit()
