from machine import Pin, PWM
import time

speed = 50000

en4 = PWM(Pin(17))
in41 = Pin(18, Pin.OUT, value=0)
in42 = Pin(19, Pin.OUT, value=0)
en4.freq(1000)

en2 = PWM(Pin(22))
in21 = Pin(20, Pin.OUT, value=0)
in22 = Pin(21, Pin.OUT, value=0)
en2.freq(1000)

en3 = PWM(Pin(9))
in31 = Pin(10, Pin.OUT, value=0)
in32 = Pin(11, Pin.OUT, value=0)
en3.freq(1000)

en1 = PWM(Pin(14))
in11 = Pin(13, Pin.OUT, value=0)
in12 = Pin(12, Pin.OUT, value=0)
en1.freq(1000)

def fwd(en, in1, in2, spd=speed):
    in2.value(0)
    in1.value(1)
    en.duty_u16(spd)

def rev(en, in1, in2, spd=speed):
    in1.value(0)
    in2.value(1)
    en.duty_u16(spd)

def stp(en, in1, in2, spd=speed):
    en.duty_u16(0)
    in1.value(0)
    in2.value(0)

def test(en, in1, in2, m="_"):
    print("Test Mtr ", m)
    print(" FWD")
    fwd(en, in1, in2)
    time.sleep(1)
    stp(en, in1, in2)
    time.sleep(1)
    print(" REV")
    rev(en, in1, in2)
    time.sleep(1)
    stp(en, in1, in2)
    time.sleep(1)

if __name__ == "__main__":
    test(en1, in11, in12, m="M1")
    test(en2, in21, in22, m="M2")
    test(en3, in31, in32, m="M3")
    test(en4, in41, in42, m="M4")