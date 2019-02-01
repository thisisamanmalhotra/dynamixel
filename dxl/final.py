import dxl
import time
import math


# coords
x = int(input("x:"))
y = int(input("y:"))

a = dxl.get_available_ports()
print(a)
d = dxl.dxl(a[0], 1000000)
print(d.scan(10))


# lengths
a2 = 10.5
a4 = 11.5

if x <= 0:
    x += 1
    y -= 1
    # value of r
    r = math.sqrt(pow(x, 2) + pow(y, 2))
    # equation 1
    pa = (pow(y, 2) + pow(r, 2) - pow(x, 2)) / (2 * y * r)
    p1 = math.acos(pa) * 57.2958
    # equation 2
    pb = (pow(a2, 2) + pow(r, 2) - pow(a4, 2)) / (2 * a2 * r)
    p2 = math.acos(pb) * 57.2958
    # equation 3
    pc = (pow(a4, 2) + pow(a2, 2) - pow(r, 2)) / (2 * a2 * a4)
    p3 = math.acos(pc) * 57.2958

    # angles
    m = p1 - p2
    n = 180 - p3

    # writing angles
    m3 = int(512 + (m * 3.413))
    m4 = int(512 + (n * 3.413))

else:
    # value of r
    r = math.sqrt(pow(x, 2) + pow(y, 2))
    # equation 1
    pa = (pow(a2, 2) + pow(r, 2) - pow(a4, 2)) / (2 * a2 * r)
    p1 = math.acos(pa) * 57.2958
    # equation 2
    pb = (pow(x, 2) + pow(r, 2) - pow(y, 2)) / (2 * x * r)
    p2 = math.acos(pb) * 57.2958
    # equation 3
    pc = (pow(a4, 2) + pow(a2, 2) - pow(r, 2)) / (2 * a2 * a4)
    p3 = math.acos(pc) * 57.2958

    # angles
    m = p2 - p1
    n = 180 - p3

    # writing angles
    m3 = int(211 + (m * 3.413))
    m4 = int(512 + (n * 3.413))


# dictionary writting values to motors corresponding to the motor ID
dictionary = {1: 2048, 2: 2122, 3: m3, 4: m4, 5: 202, 7: 700}
# zero for 1 is in 2122 and zero position for 2 is in 2068
# zero for 3-7 are in 512
d.speed(1, 40)
d.speed(2, 40)
d.speed(3, 40)
d.speed(4, 40)
d.speed(5, 40)
d.speed(6, 40)
d.speed(7, 40)

# sync-write command
d.set_goal_position(dictionary)
time.sleep(5)
d.move(2, 2870)
time.sleep(5)
d.move(7, 512)
# for a time interval between commands use: time.sleep(seconds)

# setting torque to zero(not very necessary)
# d.set_torque({k: 0 for k in range(1, 8)})

# prints done after all commands are executed
print("done")
