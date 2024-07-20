import numpy as np
import time
import keyboard

class Manipulator:
    def __init__(self, addr_list, len_list, protocol, id_list):
        self.addr_torque_enable = addr_list[0]
        self.addr_goal_position = addr_list[1]
        self.addr_moving_speed = addr_list[2]
        self.addr_present_position = addr_list[3]
        self.addr_present_velocity = addr_list[4]
        self.addr_moving = addr_list[5]

        self.len_goal_position = len_list[0]
        self.len_present_position = len_list[0]
        self.len_present_velocity = len_list[0]
        self.len_moving = len_list[0]

        self.protocol = protocol

        self.motors = id_list

        self.baudrate = 3000000
        self.devicename = 'COM5'

        self.torque_enable = 1
        self.torque_disable = 0

        self.packetHandler = PacketHandler(protocol)
        self.groupSyncWrite = GroupSyncWrite(portHandler, self.packetHandler, self.addr_goal_position, self.len_goal_position)
        self.groupSyncRead = GroupSyncRead(portHandler, self.packetHandler, self.addr_present_position, self.len_present_position)
        self.position_groupBulkRead = GroupBulkRead(portHandler, self.packetHandler)

    def torque_on(self):
        for id in self.motors:
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(portHandler, id, self.addr_torque_enable, self.torque_enable)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))
        print('\033[32m' + 'Torque On' + '\033[0m')

    def torque_off(self):
        for id in self.motors:
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(portHandler, id, self.addr_torque_enable, self.torque_disable)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))
        print('\033[31m' + 'Torque Off' + '\033[0m')

    def rad2pos(self, rad):
        return (int)(2048 + rad*2048/np.pi)
    
    def syncAdd(self, ID, pos):
        param = [DXL_LOBYTE(DXL_LOWORD(pos)), 
                DXL_HIBYTE(DXL_LOWORD(pos)), 
                DXL_LOBYTE(DXL_HIWORD(pos)), 
                DXL_HIBYTE(DXL_HIWORD(pos))]
        self.groupSyncWrite.addParam(ID, param)

    def posRead(self):
        pos = [None] * 6
        for idx, DXL_ID in enumerate(self.motors):
            dxl_present_position,_,_ = self.packetHandler.read2ByteTxRx(portHandler, DXL_ID, self.addr_present_position)
            pos[idx] = dxl_present_position
        return pos
    
    def moveTo(self, pos):
        for idx, i in enumerate(self.motors):
            self.syncAdd(i, pos[idx])
        self.groupSyncWrite.txPacket()
        self.groupSyncWrite.clearParam()

    # def slowMove(self, goal):
    #     pos = self.posRead()


    def setDefault(self):
        pos = [None] * 6
        for DXL_ID in self.motors:
            dxl_present_position, dxl_comm_result, dxl_error = self.acketHandler.read4ByteTxRx(portHandler, DXL_ID, self.addr_present_position)
            pos[DXL_ID-1] = dxl_present_position

        for index, i in enumerate(self.motors):
            self.syncAdd(i, pos[index])
        self.groupSyncWrite.txPacket()
        self.groupSyncWrite.clearParam()

# Control table address
# Control table address is different in Dynamixel model
# [torque enable, goal position, moving speed, present position, present velocity, moving]
MX_ADDR_LIST = [24, 30, 32, 36, 38, 46]
XM_ADDR_LIST = [64, 116, 128, 132, 128, 122]

# Data Byte Length
# [goal postion, present position, present velocity, moving]
MX_LEN_LIST = [2, 2, 2, 1]
XM_LEN_LIST = [4, 4, 4, 1]

# Protocol version
MX_PROTOCOL = 1.0
XM_PROTOCOL = 2.0

# Default setting
MX_DXL = [11, 12, 13, 14, 15, 16]
XM_DXL = [1, 2, 3, 4, 5, 6]


BAUDRATE                    = 3000000            # Dynamixel default baudrate : 57600
DEVICENAME                  = 'COM5'    # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

import os
from time import time

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

from dynamixel_sdk import *                    # Uses Dynamixel SDK library

portHandler = PortHandler(DEVICENAME)

if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    getch()
    quit()

# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()

if __name__ == '__main__':
    teacher = Manipulator(MX_ADDR_LIST, MX_LEN_LIST, MX_PROTOCOL, MX_DXL)
    student = Manipulator(XM_ADDR_LIST, XM_LEN_LIST, XM_PROTOCOL, XM_DXL)

    student.torque_on()
    time.sleep(5)

    while 1:
        pos = teacher.posRead()
        print(pos)
        student.moveTo(pos)
        time.sleep(0.001)
