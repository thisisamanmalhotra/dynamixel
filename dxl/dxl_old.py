"""
dxl library meant to work with DynamixelSDK and only Dynamixel X Series motors and MX Series motors having protocol 2.0.
To use with other devices need to change control table.
"""import os
import glob
import ctypes
from dynamixel_sdk import *

COMM_TX_FAIL = -1001
COMM_SUCCESS = 0

def get_available_ports():
    return glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyCOM*")
class Dxl:
    """
    Dxl class
    Args:
        DeviceName: Refers to the USB Device transferring the signal
        baudrate: The transfer baudrate for the data rate
        protocol: The protocol version bering used
    """
    def __init__(self,DeviceName,baudrate=57600,protocol = 2):
        self.portHandler = PortHandler(DeviceName)
        self.PROTOCOL_VERSION = protocol
        self.BAUDRATE = baudrate
        self.packetHandler = PacketHandler(self.PROTOCOL_VERSION)
        self.dxl_comm_result = COMM_TX_FAIL
        self.dxl_error = 0
        # ADDR values for X Series
        # Control Table
        self.ADDR_X_TORQUE_ENABLE = 64
        self.ADDR_X_GOAL_POSITION = 116
        self.ADDR_X_PRESENT_POSITION = 132
        self.ADDR_X_GOAL_VELOCITY = 104
        self.ADDR_X_PRESENT_VELOCITY = 104
        self.ADDR_X_MODE = 11
        self.LEN_X_GOAL_POSITION = 4
        self.LEN_X_PRESENT_POSITION = 4
        self.dxl_addparam_result = 0

        self.groupSync = GroupSyncWrite(self.portHandler, self.packetHandler, self.ADDR_X_GOAL_POSITION, 4)

        self.TORQUE_ENABLE = 1
        self.TORQUE_DISABLE = 0
        if self.portHandler.openPort():
            print "Opened port"
        else:
            print "Failed to open any port"
            input()
            quit()
        if self.portHandler.setBaudRate(self.BAUDRATE):
            print "Change baudrate succeeded"
        else:
            print "Failed to change baudrate"
            input()
            quit()

    def error(self,dxl_comm_result,dxl_error = 0):
        """
        Displays the error output
        Args:
            dxl_comm: Communications result
            dxl_error: Error number
        """
        if dxl_comm_result is not COMM_SUCCESS:
            print(self.packetHandler.getTxRxResult(self.PROTOCOL_VERSION,dxl_comm_result))
        elif dxl_error is not 0:
            print(self.getRxPacketError(self.PROTOCOL_VERSION,dxl_error))

    def scan(self, ran = 254):
        """
        Scans the given device for list of connected motors
        Args:
            ran: Range till which motors are to be pinged
        """
        _ids = []
        for i in range(ran):
            dxl_model,dxl_comm_result,dxl_error = self.packetHandler.ping(self.portHandler,i)
            if dxl_comm_result != COMM_SUCCESS:
                pass
            elif dxl_error != 0:
                pass
            else:
                _ids.append(i)
        return _ids
    
    def _read(self,DXL_ID,pos,size):
        """
        Reads a given value in the control table
        Args:
            DXL_ID: Motor ID
            pos: Location in control table
            size: Number of bytes to read
        Returns:
            Present value in the given position
        """
        dxl_present_val = 0
        dxl_comm_result,dxl_error = 0,0
        if size == 1:
            dxl_present_val,dxl_comm_result,dxl_error = self.packetHandler.read1ByteTxRx(self.portHandler, DXL_ID, pos)
        if size == 2:
            dxl_present_val,dxl_comm_result,dxl_error = self.packetHandler.read2ByteTxRx(self.portHandler, DXL_ID, pos)
        if size == 4:
            dxl_present_val,dxl_comm_result,dxl_error = self.packetHandler.read4ByteTxRx(self.portHandler, DXL_ID, pos)
        self.error(dxl_comm_result,dxl_error)
        return dxl_present_val
    
    def _write_speed(self,DXL_ID,speed):
        """
        Sets the speed of a single motor
        Args:
            DXL_ID: Motor ID
            speed: Target speed (0 - 1023)
        """
        dxl_comm_result,dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, DXL_ID, self.ADDR_X_GOAL_VELOCITY, int(speed))
        self.error(dxl_comm_result,dxl_error)

    def set_goal_position(self, ids):
        """
        Sets the goal position
        Args:
            ids: Dictionary of motor id and target position pairs
        TODO: SyncWrite doesn't work
        """
        param_array = []
        for i,angle in ids.iteritems():
            param_array = [DXL_LOBYTE(DXL_LOWORD(angle)), DXL_HIBYTE(DXL_LOWORD(angle)),DXL_LOBYTE(DXL_HIWORD(angle)), DXL_HIBYTE(DXL_HIWORD(angle))]
            print param_array
            dxl_addparam_result = self.groupSync.addParam(i, param_array)
            if dxl_addparam_result is not True:
                print("[ID:%03d] groupSyncWrite add param failed")
            del param_array[:]
        self.groupSync.txPacket()
        self.error(dxl_comm_result)
        self.groupSync.clearParam()

    def get_present_position(self, ids):
        """
        Tells the present position of given motors
        Args:
            ids: Tuple of motors ids whose position is needed
        Returns:
            Dictionary of motor id and current position pairs
        """
        present_pos = {}
        for i in ids:
            present_pos[i] = self._read(i, self.ADDR_X_PRESENT_POSITION, self.LEN_X_PRESENT_POSITION)
        return present_pos

    def set_moving_speed(self, ids):
        """
        Set the moving speed for motors
        Args:
            ids: Dictionary of motor id and speed pairs
        """
        for i,val in ids.iteritems():
            self._write_speed(i, val)

    def enable_torque(self, ids):
        """
        Enables torque in motors
        Args:
            ids:Tuple of dictionary ideas
        """
        for i in ids:
            dxl_comm_result,dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, i, self.ADDR_X_TORQUE_ENABLE, self.TORQUE_ENABLE)
            self.error(dxl_comm_result, dxl_error)

    def set_wheel_mode(self, ids, mode = 1):
        """
        Enables wheel mode.
        It's also possible to change the Operation mode to anyother mode besides wheel mode
        Need to disable torque before changing operation mode. To make changes permanent enable torque after changing Operation mode
        Args:
            ids: Tuple of motors whose Operation mode needs to be changes

        """
        for i in ids:
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, i, self.ADDR_X_MODE, mode)
            self.error(dxl_comm_result,dxl_error)
    def disable_torque(self, ids):
        """
        Disable torque
        Args:
            ids: Tuple containing motor ids whose torque is to be disabled
        """
        for i in ids:
            dxl_comm_result,dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, i, self.ADDR_X_TORQUE_ENABLE, self.TORQUE_DISABLE)
            self.error(dxl_comm_result, dxl_error)
