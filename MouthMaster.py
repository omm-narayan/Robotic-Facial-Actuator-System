import time
import sys
from machine import Pin
from servo import Servo

# GPIO Setup
led = Pin(25, Pin.OUT)
mode = Pin(28, Pin.IN, Pin.PULL_UP)
SDA = Pin(16, Pin.OUT)
SCL = Pin(17, Pin.OUT)
BSDA = Pin(18, Pin.OUT)
BSCL = Pin(19, Pin.OUT)

# ServoConfig Class
class SCFG:
    def __init__(self, pin_id, limits):
        self.servo = Servo(pin_id=pin_id)
        self.start, self.end = limits
        self.angle = self.start
        self.direction = 1

    def move(self, angle):
        self.servo.write(angle)

    def step(self, step_size=1):
        step = step_size if self.start < self.end else -step_size
        self.angle += self.direction * step
        if self.direction == 1 and self.angle >= self.end:
            self.angle = self.end
            self.direction = -1
        elif self.direction == -1 and self.angle <= self.start:
            self.angle = self.start
            self.direction = 1
        self.move(self.angle)

# Servo Map
servos = {
    "JL": SCFG(4, (90, 50)),
    "JR": SCFG(5, (90, 130)),
    "LUL": SCFG(6, (80, 100)),
    "LUR": SCFG(7, (80, 100)),
    "LLL": SCFG(8, (10, 170)),
    "LLR": SCFG(9, (80, 100)),
    "CUL": SCFG(10, (80, 100)),
    "CUR": SCFG(11, (80, 100)),
    "CLL": SCFG(12, (80, 100)),
    "CLR": SCFG(13, (80, 100)),
    "TON": SCFG(14, (80, 100)),
    "EXA": SCFG(15, (80, 100)),
}

# Facial Pose Map
poses = {
    "mouth_closed": {"JL": 90, "JR": 90},
    "mouth_open": {"JL": 50, "JR": 130},
    "lips_down": {"LUL": 110, "LUR": 70, "LLL": 55, "LLR": 110},
    "lips_up": {"LUL": 40, "LUR": 140, "LLL": 110, "LLR": 60},
    "tongue_down": {"TON": 130},
    "tongue_up": {"TON": 55},
    "smile": {"CUL": 60, "CUR": 105, "CLL": 90, "CLR": 90},
    "frown": {"CUL": 100, "CUR": 75, "CLL": 90, "CLR": 90},
    "wide": {"CUL": 65, "CUR": 105, "CLL": 120, "CLR": 65},
    "narrow": {"CUL": 90, "CUR": 80, "CLL": 90, "CLR": 90},
}

# Apply a named facial pose
def apply_pose(pose_name):
    if pose_name in poses:
        for name, angle in poses[pose_name].items():
            servos[name].move(angle)
    else:
        print(f"Pose '{pose_name}' not found.")

# Initialization
print("Mouth Master Ready")
SDA.value(0)
SCL.value(0)
BSDA.value(0)
BSCL.value(0)
apply_pose("mouth_closed")
apply_pose("tongue_down")
apply_pose("narrow")

# Main command loop
while True:
    try:
        line = sys.stdin.readline()
        if not line:
            continue
        command = line.strip()
        print(f"Received: {command}")

        if command == "on":
            led.value(1)
        elif command == "off":
            led.value(0)
        elif command == "eyes_move":
            SDA.value(1)
            SCL.value(1)
        elif command == "eyes_open":
            SDA.value(1)
            SCL.value(0)
        elif command == "eyes_close":
            SDA.value(0)
            SCL.value(0)
        elif command == "brows_up":
            BSDA.value(1)
            BSCL.value(1)
        elif command == "brows_down":
            BSDA.value(0)
            BSCL.value(0)
        elif command == "brows_happy":
            BSDA.value(0)
            BSCL.value(1)
        elif command == "brows_angry":
            BSDA.value(1)
            BSCL.value(0)
        elif command in poses:
            apply_pose(command)
        else:
            print("Unknown command")

    except Exception as e:
        print("Error:", e)