#!/usr/bin/env python2
import time
import os
import subprocess
import sys

#PARAMETERS
count = 0
path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
devicename = "'IPTS Touch'"
penname = "'IPTS Stylus Pen (0)'"
freq = 1.0

#FUNCTIONS
def readFile(path): #self.filename
    myDatei = open(path, "r")
    myList = []
    #Liste aus Datei erstellen
    for Line in myDatei:
        Line = Line.rstrip()
        #Line = Line.decode('utf8')
        myList.append(Line)
    myDatei.close()
    return(myList)

def writeFile(path, myList): #self.filename
    myDatei = open(path, "w")
    #Liste aus Datei erstelle
    myDatei.writelines(myList)
    myDatei.close()

def refreshtouch():
    os.system('xinput disable ' + devicename)
    os.system('xinput enable ' + devicename)

def checkdisplays():
    check_displays = "xrandr | grep -w 'connected'"
    str_displays = str(subprocess.check_output(check_displays, shell=True).lower().rstrip())
    list_displays = str_displays.splitlines()
    int_displays = len(list_displays)
    return int_displays

# Look for accelerometer
while count <= 9:
    if os.path.exists('/sys/bus/iio/devices/iio:device' + str(count) + '/in_accel_scale') == True:
        dpath = '/sys/bus/iio/devices/iio:device' + str(count) + '/' # directory of accelerometer device (iio)
        break
    count = count + 1
#print(dpath)

#Commands for correct rotation
normal = 'xrandr -o normal; '+'xinput set-prop ' + devicename +" 'Coordinate Transformation Matrix' 1 0 0 0 1 0 0 0 1;"+'xinput set-prop ' + penname +" 'Coordinate Transformation Matrix' 1 0 0 0 1 0 0 0 1;"
inverted = 'xrandr -o inverted; '+'xinput set-prop ' + devicename +" 'Coordinate Transformation Matrix' -1 0 1 0 -1 1 0 0 1;"+'xinput set-prop ' + penname +" 'Coordinate Transformation Matrix' -1 0 1 0 -1 1 0 0 1;"
right = 'xrandr -o left; '+'xinput set-prop ' + devicename +" 'Coordinate Transformation Matrix' 0 -1 1 1 0 0 0 0 1;"+'xinput set-prop ' + penname +" 'Coordinate Transformation Matrix' 0 -1 1 1 0 0 0 0 1;"
left = 'xrandr -o right; '+'xinput set-prop ' + devicename +" 'Coordinate Transformation Matrix' 0 1 0 -1 0 1 0 0 1;"+'xinput set-prop ' + penname +" 'Coordinate Transformation Matrix' 0 1 0 -1 0 1 0 0 1;"
state_dict = {0: "normal", 1: "inverted", 2: "right", 3: "left"}
current_state = 0
previous_tstate = "on"
previousStylusProximityStatus = "out"
firstrun = True
#ACCELEROMETER
with open(dpath + 'in_accel_scale') as f:
    scale = float(f.readline())
while True:
    multimonitor = False
    int_displays = checkdisplays()
    if int_displays > 1:
        multimonitor = True
    time.sleep(1.0/freq)
    previous_state = current_state
    status = readFile(os.path.join(path, 'status.txt'))
    if str(status[0]) == "on" and multimonitor == False:
        with open(dpath + 'in_accel_x_raw', 'r') as fx:
            with open(dpath + 'in_accel_y_raw', 'r') as fy:
                with open(dpath + 'in_accel_z_raw', 'r') as fz:
                    thex = float(fx.readline())
                    they = float(fy.readline())
                    thez = float(fz.readline())
                    if checkdisplays() == 1:
                        if (thex >= -650 and thex <=650 and thez > -350):
                            if (they <= -1 and they >= -1100):
                                os.system(normal)
                                current_state = 0
                            #elif (they >= 0 and they <= 1100):
                            #    os.system(inverted)
                            #    current_state = 1
                        else:
                            if (thex >= 700 and thex <= 1100):
                                os.system(right)
                                current_state = 2
                            elif (thex <= -700 and thex >= -1100):
                                os.system(left)
                                current_state = 3

        os.system('clear')
        print("ExtDi: " + str(multimonitor))
        print("A-ROT: " + status[0])
        print("    x: " + str(thex))
        print("    y: " + str(they))
        print("    z: " + str(thez))
        print("  POS: " + state_dict[current_state])
    if status[0] == "off" or multimonitor == True:
        os.system('clear')
        print("ExtDi: " + str(multimonitor))
        print("A-ROT: " + status[0])
        print("    x: " + status[0])
        print("    y: " + status[0])
        print("    z: " + status[0])
        print("  POS: " + state_dict[previous_state])
    if current_state != previous_state:
        refreshtouch()
        print "Touchscreen refreshed"

    print("##########################")
#SCREEN
    stylusProximityCommand = 'xinput query-state ' + penname + ' | grep Proximity | cut -d " " -f3 | cut -d "=" -f2'
    stylusProximityStatus = str(subprocess.check_output(stylusProximityCommand, shell=True).lower().rstrip())
    tstatus = readFile(os.path.join(path, 'touch.txt'))
#TOUCHSCREEN
    if str(tstatus[0]) == "on" and stylusProximityStatus == "out":
        os.system('xinput enable ' + devicename + '')
        print("TOUCH: " + tstatus[0])
        if str(tstatus[0]) != previous_tstate:
            Notify.init ("Touchscreen-ON")
            RotationON=Notify.Notification.new ("Touchscreen","Touchscreen is now turned ON","dialog-information")
            RotationON.show()
    elif str(tstatus[0]) == "off" and stylusProximityStatus == "out":
        os.system('xinput disable ' + devicename + '')
        print("TOUCH: " + tstatus[0])
        if str(tstatus[0]) != previous_tstate:
            Notify.init ("Touchscreen-OFF")
            RotationOFF=Notify.Notification.new ("Touchscreen","Touchscreen is now turned OFF","dialog-information")
            RotationOFF.show()
    previous_tstate = str(tstatus[0])
#PEN
    if str(tstatus[0]) == "off" and stylusProximityStatus == "in":
        print("TOUCH: " + tstatus[0])
        print("  PEN: " + stylusProximityStatus)
    elif str(tstatus[0]) == "on" and stylusProximityStatus == "in" and firstrun == False:
        os.system('xinput disable "NTRG0001:01 1B96:1B05"')
        print("TOUCH: " + "off")
        print("  PEN: " + stylusProximityStatus)
    elif stylusProximityStatus == "out":
        print("  PEN: " + stylusProximityStatus)
        firstrun == False
