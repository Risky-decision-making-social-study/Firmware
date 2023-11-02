# python Port of https://github.com/sosandroid/AMS_AS5048B

import time
from enum import Enum

import numpy as np
import smbus

# Default addresses for AS5048B
AS5048_ADDRESS = 0x40  # 0b10000 + ( A1 & A2 to GND)
AS5048B_PROG_REG = 0x03
AS5048B_ADDR_REG = 0x15
AS5048B_ZEROMSB_REG = 0x16  # bits 0..7
AS5048B_ZEROLSB_REG = 0x17  # bits 0..5
AS5048B_GAIN_REG = 0xFA
AS5048B_DIAG_REG = 0xFB
AS5048B_MAGNMSB_REG = 0xFC  # bits 0..7
AS5048B_MAGNLSB_REG = 0xFD  # bits 0..5
AS5048B_ANGLMSB_REG = 0xFE  # bits 0..7
AS5048B_ANGLLSB_REG = 0xFF  # bits 0..5
AS5048B_RESOLUTION = pow(2, 14)  # 16384.0  # 14 bits

#  Moving Exponential Average on angle - beware heavy calculation for some Arduino boards
#  This is a 1st order low pass filter
#  Moving average is calculated on Sine et Cosine values of the angle to provide an extrapolated accurate angle value.
EXP_MOVAVG_N = 5  # history length impact on moving average impact - keep in mind the moving average will be impacted by the measurement frequency too
EXP_MOVAVG_LOOP = 1  # number of measurements before starting mobile Average - starting with a simple average - 1 allows a quick start. Value must be 1 minimum

# unit consts - just to make the units more readable


MASK_14BITS = 0x3FFF
MASK_6BITS = 0x3F


class AS5048B(object):
    """
    docstring
    """

    units: Enum = Enum(
        'units', 'RAW TRN DEG RAD GRAD MOA SOA MILNATO MILSE MILRU')

    # variables
    __debugFlag: bool
    __clockWise: bool
    __chipAddress: np.uint8
    __addressRegVal: np.uint8
    __zeroRegVal: np.uint16
    __lastAngleRaw: np.double
    __movingAvgExpAngle: np.double = 0.
    __movingAvgExpSin: np.double = 0.
    __movingAvgExpCos: np.double = 0.
    __movingAvgExpAlpha: np.double = 0.
    __movingAvgCountLoop: int

    def __init__(self, *, address=AS5048_ADDRESS):
        """Class initialisation

        Args:
            address ([type], optional): I2C address for AS5048B. Defaults to Default address for AS5048B.
        """
        self.__chipAddress = address
        self.bus: smbus = smbus.SMBus(1)

        self.__clockWise = True
        self.__lastAngleRaw = 0.0
        self.__zeroRegVal = self.zeroRegR()
        self.__addressRegVal = self.addressRegR()

        self.resetMovingAvgExp()

    def cleanup(self):
        # TODO cleanup
        pass

    def setClockWise(self, cw: bool = True):
        """ Set / unset clock wise counting - sensor counts CCW natively

        Args:
            cw (bool, optional): true: CW, false: CCW. Defaults to True.
        """

        self.__clockWise = cw
        self.__lastAngleRaw = 0.0
        self.resetMovingAvgExp()

    def progRegister(self, regVal):
        """writes OTP control register

        Args:
            regVal ([type]): register value
        """

        self.__writeReg(AS5048B_PROG_REG, regVal)
        return

    def doProg(self):
        """Burn values to the slave address OTP register
        """

        # enable special programming mode
        self.progRegister(0xFD)
        time.sleep(10)

        # set the burn bit: enables automatic programming procedure
        self.progRegister(0x08)
        time.sleep(10)

        # disable special programming mode
        self.progRegister(0x00)
        time.sleep(10)

    def doProgZero(self):
        """Burn values to the zero position OTP register
        """
        # this will burn the zero position OTP register like described in the datasheet
        # enable programming mode
        self.progRegister(0x01)
        time.sleep(10)

        # set the burn bit: enables automatic programming procedure
        self.progRegister(0x08)
        time.sleep(10)

        # read angle information (equals to 0)
        self.__readReg16(AS5048B_ANGLMSB_REG)
        time.sleep(10)

        # enable verification
        self.progRegister(0x40)
        time.sleep(10)

        # read angle information (equals to 0)
        self.__readReg16(AS5048B_ANGLMSB_REG)
        time.sleep(10)

    def addressRegW(self, regVal: np.uint8):
        """write I2C address value (5 bits) into the address register

        Args:
            regVal (np.uint8): register value
        """
        # write the new chip address to the register
        self.__writeReg(AS5048B_ADDR_REG, regVal)

        # update our chip address with our 5 programmable bits
        # the MSB is internally inverted, so we flip the leftmost bit
        self.__chipAddress = ((regVal << 2) | (
            self.__chipAddress & 0b11)) ^ (1 << 6)

    def addressRegR(self) -> np.uint8:
        """reads I2C address register value

        Returns:
            np.uint8: register value
        """
        return self.__readReg8(AS5048B_ADDR_REG)

    def setZeroReg(self):
        """sets current angle as the zero position
        """
        # Issue closed by @MechatronicsWorkman and @oilXander. The last sequence avoids any offset for the new Zero position
        self.zeroRegW(np.uint16(0x00))
        newZero: np.uint16 = MASK_14BITS - self.angleR()
        self.zeroRegW(newZero)

    def zeroRegW(self, regVal: np.uint16):
        """ writes the 2 bytes Zero position register value

        Args:
            regVal (np.uint16): register value
        """
        regVal = int(MASK_14BITS - regVal)

        self.__writeReg(AS5048B_ZEROMSB_REG, np.uint8(regVal >> 6))
        self.__writeReg(AS5048B_ZEROLSB_REG, np.uint8(regVal & MASK_6BITS))
        pass

    def zeroRegR(self) -> np.uint16:
        """reads the 2 bytes Zero position register value

        Returns:
            np.uint16: register value trimmed on 14 bits
        """
        return MASK_14BITS - self.__readReg16(AS5048B_ZEROMSB_REG)

    def magnitudeR(self) -> np.uint16:
        """reads the 2 bytes magnitude register value

        Returns:
            np.uint16: register value trimmed on 14 bits
        """
        return self.__readReg16(AS5048B_MAGNMSB_REG)

    def angleRegR(self) -> np.uint16:
        """reads the 2 bytes angle register value

        Returns:
            np.uint16: register value trimmed on 14 bits
        """
        return self.__readReg16(AS5048B_ANGLMSB_REG)

    def getAutoGain(self) -> np.uint8:
        """reads the 1 bytes auto gain register value

        Returns:
            np.uint8: register value
        """
        return self.__readReg8(AS5048B_GAIN_REG)

    def getDiagReg(self):
        """reads the 1 bytes auto gain register value

        Returns:
            np.uint8: register value
        """
        return self.__readReg8(AS5048B_DIAG_REG)

    def angleR(self, unit: Enum = None, newVal: bool = True) -> np.double:
        """reads current angle value and converts it into the desired unit

        Args:
            unit (int, optional): The unit of the angle. Sensor raw value as default. Defaults to RAW.
            newVal (bool, optional): have a new measurement or use the last read one. True as default. Defaults to True.

        Returns:
            np.double: Double angle value converted into the desired unit
        """
        if unit is None:
            unit = self.units.RAW

        angleRaw: np.double

        if (newVal):
            if(self.__clockWise):
                angleRaw = np.double(MASK_14BITS -
                                     self.__readReg16(AS5048B_ANGLMSB_REG))
            else:
                angleRaw = np.double(self.__readReg16(AS5048B_ANGLMSB_REG))

            self.__lastAngleRaw = angleRaw

        else:
            angleRaw = self.__lastAngleRaw

        return self.__convertAngle(unit, angleRaw)

    def updateMovingAvgExp(self):
        """Performs an exponential moving average on the angle.
                        Works on Sine and Cosine of the angle to avoid issues 0°/360° discontinuity
        """
        angle: np.double = self.angleR(self.units.RAD, True)

        if (self.__movingAvgCountLoop < EXP_MOVAVG_LOOP):
            self.__movingAvgExpSin += np.sin(angle)
            self.__movingAvgExpCos += np.cos(angle)
            if (self.__movingAvgCountLoop == (EXP_MOVAVG_LOOP - 1)):
                self.__movingAvgExpSin = self.__movingAvgExpSin / EXP_MOVAVG_LOOP
                self.__movingAvgExpCos = self.__movingAvgExpCos / EXP_MOVAVG_LOOP

            self.__movingAvgCountLoop += 1

        else:
            movavgexpsin: np.double = self.__movingAvgExpSin + \
                self.__movingAvgExpAlpha * \
                (np.sin(angle) - self.__movingAvgExpSin)
            movavgexpcos: np.double = self.__movingAvgExpCos + \
                self.__movingAvgExpAlpha * \
                (np.cos(angle) - self.__movingAvgExpCos)
            self.__movingAvgExpSin = movavgexpsin
            self.__movingAvgExpCos = movavgexpcos
            self.__movingAvgExpAngle = self.__getExpAvgRawAngle()

    def getMovingAvgExp(self, unit: Enum = None) -> np.double:
        """sent back the exponential moving averaged angle in the desired unit

        Args:
            unit (int, optional): the unit of the angle. Sensor raw value as default. Defaults to RAW.

        Returns:
            np.double: exponential moving averaged angle value
        """
        if unit is None:
            unit = self.units.RAW
        return self.__convertAngle(unit, self.__movingAvgExpAngle)

    def resetMovingAvgExp(self):
        """reset the exponential moving averaged angle
        """
        self.__movingAvgExpAngle = 0.0
        self.__movingAvgCountLoop = 0
        self.__movingAvgExpAlpha = 2.0 / (EXP_MOVAVG_N + 1.0)

    # private methods
    def __readReg8(self, address: np.uint8) -> np.uint8:
        return self.bus.read_byte_data(self.__chipAddress, AS5048B_ANGLMSB_REG)

    def __readReg16(self, address: np.uint8) -> np.uint16:
        # 16 bit value got from 2x8bits registers (7..0 MSB + 5..0 LSB) => 14 bits value

        value: np.uint16 = (self.bus.read_byte_data(
            self.__chipAddress, address)) << 6 | (self.bus.read_byte_data(
                self.__chipAddress, address+1))

        return value & MASK_14BITS

    def __writeReg(self, address: np.uint8, value: np.uint8):
        self.bus.write_byte_data(self.__chipAddress, address, value)

    def __convertAngle(self, unit: Enum,  angle: np.double) -> np.double:

        # RAW, TRN, DEG, RAD, GRAD, MOA, SOA, MILNATO, MILSE, MILRU
        conversions = {
            "RAW_comment": "Sensor raw measurement",
            self.units.RAW: angle,
            "TRN_comment": "full turn ratio",
            self.units.TRN: (angle / AS5048B_RESOLUTION),
            "DEG_comment": "degree",
            self.units.DEG: (angle / AS5048B_RESOLUTION) * 360.0,
            "RAD_comment": "Radian",
            self.units.RAD: (angle / AS5048B_RESOLUTION) * 2 * np.pi,
            "MOA_comment": "minute of arc",
            self.units.MOA: (angle / AS5048B_RESOLUTION) * 60.0 * 360.0,
            "SOA_comment": "second of arc",
            self.units.SOA: (angle / AS5048B_RESOLUTION) * 60.0 * 60.0 * 360.0,
            "GRAD_comment": "grade",
            self.units.GRAD: (angle / AS5048B_RESOLUTION) * 400.0,
            "MILNATO_comment": "NATO MIL",
            self.units.MILNATO: (angle / AS5048B_RESOLUTION) * 6400.0,
            "MILSE_comment": "Swedish MIL",
            self.units.MILSE: (angle / AS5048B_RESOLUTION) * 6300.0,
            "MILRcomment": "Russian MIL",
            self.units.MILRU: (angle / AS5048B_RESOLUTION) * 6000.0
        }

        return conversions[unit]

    def __getExpAvgRawAngle(self) -> np.double:

        angle: np.double
        twopi: np.double = 2 * np.pi

        if (self.__movingAvgExpSin < 0.0):
            angle = twopi - np.arccos(self.__movingAvgExpCos)

        else:
            angle = np.arccos(self.__movingAvgExpCos)

        angle = (angle / twopi) * AS5048B_RESOLUTION

        return angle
