# Tele-Operated Omni Wheel Car Revisited
This project builds on the use of a 3-axis joystick to control a mobile robot capable of holonomic motion. Two dimensional *holonomic motion* is the abilty to move freely in 3 degrees of freedom (DOF) on a *typically flat* surface. The 3 degrees of freedom are defined as **X**, **Y**, and **θz**.

> Holonomic Motion is comprised of any combination of its 3 DOF all superimposed simultaneously. For example, the robot can move diagonally along a line (either straight or curved) while spinning about its axis. 


## Earlier Projects:
1. The [Arduino controlled TeleOp "Omni wheel" type car](https://github.com/dblanding/teleOpOmniCar) was an initial project which demonstrated holonomic motion by using 4 omni-wheels in an **X** pattern. In this project, a driver station communicated with the car via a pair of HC05/06 Bluetooth modules. The driver station processed input from a 3-axis joystick and then sent 4 comma separated substrings "str1,str2,str3,str4" to the robot, each substring representing the speed of one of the 4 wheel motors in the range from -255 to +255. (-255 is full speed reverse and +255 is full speed forward.)

2. A more recent project is the [Adeept Mecanum wheel project](https://github.com/dblanding/BLE-Joystick-Controlled-Mecanum-Car), in which Mecanum wheels are used (instead of Omni wheels) to achieve holonomic motion. This project was undertaken to explore and demonstrate the functional equivalence of the Mecanum wheels and the Omni wheels.

Some other differences between the Mecanum wheel project and the onmi-wheel project were:
* Used Pico-W modules communicating via built-in BLE capability, instead of Arduinos.
* Driver station sends raw joystick data as 3 comma separated joystick values in range from -127 to +127. Wheel speeds are computed on the robot.
* The Mecanum wheel project was a modification of a purchased kit, so I made only minimal changes. For example, I used the motor driver h/w and s/w that came with the kit. 

## Coordinate frames: Local vs. Global
Regardless of whether Mecanum wheels or Omni wheels are used to enable Holonomic Motion, the driver who operates the joystick is likely to be in a fixed location while the robot will be moving about within a *field* or arena. The robot's *Local* frame of reference will be constantly moving with respect to the *Global* frame of reference of the arena or field.

In both of the above projects, the joystick control has operated as if the driver is seated on the robot. Whatever direction the joysick moves, the robot will move in the corresponding direction. This is called by various names, such as *First-Person View* or *Robot-Centric Control*.

However, the driver is **not** actually seated on the robot, but is stationary w/r/t the field. So to make the driving task much easier, a *Field-Centric Control* can be used, in which moving the stick forward causes the robot to move away from the wall where the driver is located, irrespective of the robot's angular orientation. A robot, aware of its instantaneous pose angle (**θz**), can easily convert from its local coordinate frame to its global coordinate frame.

**The main goal of this project is to implement driver control in a *Field-Centric* (Bird's-Eye View) mode** using the pose angle from an Optical Tracking Odometry Sensor (as used in the [PicoBot-OTO](https://github.com/dblanding/PicoBot-oto) project).

* The Sparkfun Optical Tracking Odometry Sensor is hooked up using the 4-wire qwiic system
    * Here's the color code used by the Qwiic system:
        * Black: GND (Ground)
        * Red: 3.3V (Power)
        * Blue: SDA (Serial Data)
        * Yellow: SCL (Serial Clock) 
    * For this project, hook up OTOS on I2C0 bus:
        * SDA to GPIO 16
        * SCL to GPIO 17

## Other project choices:
* Use a pair of Pico-W modules onboard the driver station and robot, communicating via built-in BLE (as done in the [Adeept Mecanum wheel project](https://github.com/dblanding/BLE-Joystick-Controlled-Mecanum-Car) project).
* Although I dabbled with using a [Waveshare DC Motor Driver Module for Raspberry Pi Pico](https://www.amazon.com/dp/B09D7MDL2C?ref=ppx_yo2ov_dt_b_fed_asin_title) to drive the robot's 4 motors, I ended up using two L298N modules instead.

![L298N Image](https://github.com/dblanding/Pico-MicroPython-smart-car/raw/main/imgs/L298N-pinout.jpg)

* Use a LiPo (~12V) battery onboard the robot as was done toward the end of the [Pico MicroPython Smart Car](https://github.com/dblanding/Pico-MicroPython-smart-car) project.
    * Battery supplies 12V to both L298N boards
    * 5V from one of the boards supplies power to the Pico VSYS pin (39)
    * 3.3V (for the OTOS board) comes from the Pico 3V3 pin (37)




https://github.com/user-attachments/assets/ad237c95-bbda-4d98-8ddb-20915f91a6c0


