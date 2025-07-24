import time
from machine import Pin, ADC
from servo import Servo
from picozero import Button
import random

# Switches and Mode Select
enable = Pin(6, Pin.IN, Pin.PULL_UP)
mode = Pin(1, Pin.IN, Pin.PULL_UP)
SDA = Pin(16, Pin.IN)
SCL = Pin(17, Pin.IN)

# Servo Setup
servos = {
    "LR": Servo(pin_id=8),
    "UD": Servo(pin_id=9),
    "TL": Servo(pin_id=13),
    "BL": Servo(pin_id=12),
    "TR": Servo(pin_id=11),
    "BR": Servo(pin_id=10),
}

# Servo Limits
servo_limits = {
    "LR": (40, 140),
    "UD": (60, 140),
    "TL": (90, 160),
    "BL": (90, 30),
    "TR": (90, 30),
    "BR": (90, 140),
}

# Calibration to neutral positions
def calibrate():
    for servo in servos.values():
        servo.write(90)

def neutral():
    for name, servo in servos.items():
        servo.write(90)
    lids = ["TL", "TR", "BL", "BR"]
    for lid in lids:
        servos[lid].write(servo_limits[lid][1])  # Max open

def blink():
    lids = ["TL", "TR", "BL", "BR"]
    for lid in lids:
        servos[lid].write(servo_limits[lid][0])  # Min closed

def move_servo_random(name):
    min_angle, max_angle = servo_limits[name]
    angle = random.randint(min_angle, max_angle)
    servos[name].write(angle)
    print(f"Moved {name} to {angle}°")

def move_servo_extremes(name, delay):
    min_angle, max_angle = servo_limits[name]
    servos[name].write(min_angle)
    time.sleep_ms(delay)
    servos[name].write(max_angle)
    time.sleep_ms(delay)

def control_ud_and_lids(ud_angle):
    ud_min, ud_max = servo_limits["UD"]
    tl_min, tl_max = servo_limits["TL"]
    tr_min, tr_max = servo_limits["TR"]
    bl_min, bl_max = servo_limits["BL"]
    br_min, br_max = servo_limits["BR"]

    progress = (ud_angle - ud_min) / (ud_max - ud_min)

    servos["UD"].write(ud_angle)
    servos["TL"].write(tl_max - (tl_max - tl_min) * (0.8 * (1 - progress)))
    servos["TR"].write(tr_max + (tr_min - tr_max) * (0.8 * (1 - progress)))
    servos["BL"].write(bl_max + (bl_min - bl_max) * (0.4 * progress))
    servos["BR"].write(br_max - (br_max - br_min) * (0.4 * progress))

def scale_potentiometer(value, servo_name, reverse=False):
    in_min, in_max = 300, 65300
    min_limit, max_limit = servo_limits[servo_name]

    scaled = min_limit + (value - in_min) * (max_limit - min_limit) / (in_max - in_min)
    return max_limit - (scaled - min_limit) if reverse else scaled

def update_eyelid_limits(trim_value):
    trim_min, trim_max = 7000, 14500
    progress = max(0, min(1, (trim_value - trim_min) / (trim_max - trim_min)))

    # Update servo limits based on progress
    servo_limits["TL"] = (90, 130 + (170 - 130) * progress)
    servo_limits["TR"] = (90, 50 + (10 - 50) * progress)
    servo_limits["BL"] = (90, 50 + (10 - 50) * progress)
    servo_limits["BR"] = (90, 130 + (170 - 130) * progress)

# Main Loop
while True:
    if mode.value() == 1:
        calibrate()
        time.sleep_ms(500)
    else:
        if SDA.value() == 0 and SCL.value() == 0:  # Eyes closed
            calibrate()
        elif SDA.value() == 1 and SCL.value() == 0:  # Eyes open
            neutral()
        elif SDA.value() == 1 and SCL.value() == 1:  # Auto
            command = random.randint(0, 2)
            if command == 0:
                blink()
                time.sleep_ms(50)
            elif command == 1:
                blink()
                time.sleep_ms(60)
                control_ud_and_lids(random.randint(*servo_limits["UD"]))
                servos["LR"].write(random.randint(*servo_limits["LR"]))
                time.sleep_ms(random.randint(600, 1000))
            elif command == 2:
                control_ud_and_lids(random.randint(*servo_limits["UD"]))
                servos["LR"].write(random.randint(*servo_limits["LR"]))
                time.sleep_ms(random.randint(400, 400))