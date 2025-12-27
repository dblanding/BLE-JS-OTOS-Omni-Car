"""
This library is used for speed control of 4 motors
on 2 L299N motor driver boards attached to a Pico.

Usage:
from mtr import mtr1, mtr2, mtr3, mtr4

mtr1.drive(spd1)
mtr2.drive(spd2)
mtr3.drive(spd3)
mtr4.drive(spd4)

mtr1.stop()
mtr2.stop()
mtr3.stop()
mtr4.stop()

# spd values are within +/-100
# Max spd fwd = +100
# Max spd rev = -100
"""

from machine import Pin, PWM
import time

class DCMotor:
    def __init__(self, en, in1, in2, min_duty=30_000, max_duty=65_535):
        """
        en, in1, in2 are GPIO pin numbers on the Pico attached to
        enable, in1, in2 repectively on the L298N mtr driver board.
        """
        self.enable = PWM(Pin(en))
        self.enable.freq(1_000)
        self.in1 = Pin(in1, Pin.OUT, value=0)
        self.in2 = Pin(in2, Pin.OUT, value=0)
        self.min_duty = min_duty
        self.max_duty = max_duty
        self.max_spd_cmd = 127
        self.min_spd_cmd = 10
    
    def forward(self, speed):
        """Accepts only pos values of speed"""
        self.enable.duty_u16(self.duty_cycle(speed))
        self.in1.value(1)
        self.in2.value(0)
    
    def backward(self, speed):
        """Accepts only pos values of speed"""
        self.enable.duty_u16(self.duty_cycle(speed))
        self.in1.value(0)
        self.in2.value(1)
    
    def stop(self):
        self.enable.duty_u16(0)
        self.in1.value(0)
        self.in2.value(0)

    def drive(self, speed):
        """Accepts both pos & neg values of speed"""
        if abs(speed) < self.min_spd_cmd:
            self.stop()
        elif speed < 0:
            self.backward(-speed)
        else:
            self.forward(speed)

    def duty_cycle(self, speed):
        if speed > self.max_spd_cmd:
            duty_cycle = self.max_duty
        else:
            duty_cycle = int(self.min_duty + \
                             (self.max_duty - self.min_duty) \
                             * (speed / self.max_spd_cmd))
        return duty_cycle

mtr2 = DCMotor(1, 2, 3)
mtr4 = DCMotor(8, 4, 5)
mtr3 = DCMotor(9, 11, 10)
mtr1 = DCMotor(14, 12, 13)

#mtr2 = DCMotor(22, 20, 21)

mtrs = (mtr1, mtr2, mtr3, mtr4)

if __name__ == "__main__":
    print("Testing motors")
    for mtr in mtrs:
        mtr.drive(100)
    time.sleep(1)
    for mtr in mtrs:
        mtr.stop()
    time.sleep(1)
    for mtr in mtrs:
        mtr.drive(-100)
    time.sleep(1)
    for mtr in mtrs:
        mtr.stop()
