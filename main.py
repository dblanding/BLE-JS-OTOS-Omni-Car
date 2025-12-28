# omni_car.py (aka main.py)
"""
Micropython code to drive omni-wheel car
using a 3 axis joystick communicating w/BLE
The depictions below are to clarify the relationship
between the joystick X-Y axis and
the Omni car's local X-Y axis.

They're not the same.
With a robot, its FORWARD direction defines
its X axis and its Y axis is to its left.
With a joystick, cartesian coordinates define
its X and Y axes. (Think: graph paper.)

 ***********************************************
 Joystick (3 DOF):
 
 X-axis (R/L sideways)
 Y-axis (Fwd/Rev)
 Theta-Z (spin)
 
         +Y
     Q2   |   Q1
          |
 -X ---- J/S ---- +X
          |
     Q3   |   Q4
         -Y

 Note designation of four 'quadrants'
 *************************************************
 Intuitively, we want the car to move in the same
 direction we move the joystick:
 FWD dir of car corresponds to +Y dir of joystick
 +X dir of joystick drives car to the right
 
            ^
           FWD
            |
          _____
         |_____|
   Q2    /  |  \   Q1
       /    M2   \
  _  /             \  _
 | |                 | |
 | |--M3   CAR   M4--| |
 |_|                 |_|
     \             /
       \    M1   /
   Q3    \__|__/    Q4
         |_____|
                      
 What are the motors doing?
 
 Moving joystick in +Y direction sends car FWD.
 M4 runs CW and M3 runs CCW at same speed.

 Moving joystick to the right sends car sideways.
 M1 runs CW and M2 runs CCW at same speed.
  
 Twisting joystick CW (theta-Z) spins car CW.
 All four motors run CCW at same speed.
 ************************************************
 It is easy to change car's FWD direction (by 45 deg):
 1. convert rect joystick coords to polar
 2. add 45 deg to angle
 3. convert back to rect coords
          _____
         |_____|
         /  |  \
       /    M3   \
  _  /             \  _
 | |                 | |
 | |--M1   CAR   M2--| |---> 'natural' FWD dir
 |_|                 |_|
     \             /
       \    M4   /\
         \__|__/   \
         |_____|   _\| 

                   'new' FWD dir
                  (rotated 45 deg)

"""

import aioble
import asyncio
import bluetooth
import qwiic_i2c
import qwiic_otos
import struct
import time
from machine import Pin
from math import pi
from pca9685 import PCA9685
from geom2d import r2p, p2r
from mtr import mtr1, mtr2, mtr3, mtr4

# Set teleop mode to either:
# 'FPV' for First-Person View or
# 'BEV' for Bird's-Eye View
TELEOP_MODE = 'BEV'

# Setup onboard LED
led = Pin("LED", Pin.OUT, value=0)

###################################
#
# Optical Tracking Odometry Sensor
#
###################################

# Initialize I2C1 using qwiic library
i2c0 = qwiic_i2c.get_i2c_driver(sda=16, scl=17, freq=100000)

# Set up OTOS on i2c0
myOtos = qwiic_otos.QwiicOTOS(23, i2c0)
print("\nSetting up OTOS\n")

# Perform the self test
result = myOtos.selfTest()
    
# Check if the self test passed
if(result == True):
    print("Self test passed!")
else:
    print("Self test failed!")

# Check if it's connected
if not myOtos.is_connected():
    print("The OTOS isn't connected", file=sys.stderr)

myOtos.begin()

print("Ensure the OTOS is flat and stationary during calibration!")
for i in range(5, 0, -1):
    print("Calibrating in %d seconds..." % i)
    time.sleep(1)

# Calibrate the IMU, which removes the accelerometer and gyroscope offsets
print("Calibrating IMU...")
myOtos.calibrateImu()

# Account for OTOS location w/r/t robot center
# offset = qwiic_otos.Pose2D(0, 0, 0)
# myOtos.setOffset(offset)

# Set units for linear and angular measurements.
# If not set, the default is inches and degrees.
# Note that this setting is not stored in the sensor.
# it's part of the library, so you need to set it.
myOtos.setLinearUnit(myOtos.kLinearUnitMeters)
myOtos.setAngularUnit(myOtos.kAngularUnitRadians)

# Reset the tracking algorithm - this resets the position to the origin,
# but can also be used to recover from some rare tracking errors
myOtos.resetTracking()

print("OTOS initialized")

def get_pose():
    pose = myOtos.getPosition()
    return (pose.x, pose.y, pose.h)

###################################
#
# Bluetooth
#
###################################

# BLE values
ble_name = "3axis_joystk"
ble_svc_uuid = bluetooth.UUID(0x1812)
ble_characteristic_uuid = bluetooth.UUID(0x2A4D)
ble_scan_length = 5000
ble_interval = 30000
ble_window = 30000

async def ble_scan():
    print("Scanning for BLE beacon named", ble_name, "...")
    async with aioble.scan(
    ble_scan_length,
    interval_us=ble_interval,
    window_us=ble_window,
    active=True) as scanner:
        async for result in scanner:
            if result.name() == ble_name and \
               ble_svc_uuid in result.services():
                return result.device
    return None

def decode(data):
    """Unpack X, Y, Z joystick values from BLE data"""
    return struct.unpack("3i", data)


async def main():
    while True:
        device = await ble_scan()
        if not device:
            print("BLE beacon not found.")
            continue

        try:
            print("Connecting to", device)
            connection = await device.connect()
        except asyncio.TimeoutError:
            print("Connection timed out.")
            continue

        async with connection:
            try:
                ble_service = await connection.service(ble_svc_uuid)
                ble_characteristic = await \
                  ble_service.characteristic(ble_characteristic_uuid)
            except (asyncio.TimeoutError, AttributeError):
                print("Timeout discovering services/characteristics.")
                continue

            while True:
                try:
                    pose_x, pose_y, pose_z = get_pose()
                    js_vals = decode(await ble_characteristic.read())
                    print(f"Joystick Values: {js_vals}")
                    x, y, z = js_vals
                    
                    # convert x,y coords to polar
                    r, t = r2p(x, y)
                    if TELEOP_MODE == 'BEV':
                        ROTATE_ANGLE = pi/4 + pose_z
                    else:
                        ROTATE_ANGLE = pi/4
                    # calculate new fwd dir and convert back to rect
                    x, y = p2r(r, t - ROTATE_ANGLE)
                    
                    # combine joystick thetaZ to get raw spd for motors
                    s1 = int(x + z/2)
                    s2 = int(x - z/2)
                    s3 = int(y - z/2)
                    s4 = int(y + z/2)
                    print(f"Speed Values: {s1}, {s2}, {s3}, {s4}")
                    '''
                    # check to see if any spd value is beyond +/-100
                    if any(s1, s2, s3, s4) > 100 or < -100:
                        # shrink all values to fit within circle (R=100)
                        s1, s2, s3, s4 = shrink(s1, s2, s3, s4)
                    '''
                    # Drive the motors
                    mtr4.drive(s4)
                    mtr3.drive(s3)
                    mtr2.drive(s2)
                    mtr1.drive(s1)
                    
                    led.toggle()
                    await asyncio.sleep(0.1)
                except Exception as e:
                    print(f"Error: {e}")
                    continue

asyncio.run(main())
