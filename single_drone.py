import sys
import logging
import time
from threading import Event
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils.multiranger import Multiranger
from cflib.crazyflie.syncLogger import SyncLogger

import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

#Logging variables
x_pos = [0]
y_pos = [0]
z_pos = [0]
yaw = 0
position_estimate = [0,0]
pos_error = 0.075
error_flag = 0
temp1 = [0,0,0,0,0,0]
temp2 = [0,0,0,0,0,0]
temp3 = [0,0,0,0,0,0]
temp4 = [0,0,0,0,0,0]
temp5 = [0,0,0,0,0,0]
temp6 = [0,0,0,0,0,0]
t = 0
temp_det = 0
count_temp = 0
hold = 0
cal = 0
temp_map = [0]
pos_map_x = [0]
pos_map_y = [0]
flag = 0

rx = [0]
ry = [0]
ox = [0]
oy = [0]
bx = [0]
by = [0]

#Setpoint variables (for gridded map)
grid_size = 1 
partition1 = 2
partition2 = 4
map_length_y = 1
map_length_x = 1
grid_num = 0

#Flight varibles - velocity and distance increment 
fl = 0.2
velocityx = 0.2
velocityy = 0.125

deck_attached_event = Event()

def calibrate(mc):
    global cal
    print("Recalibrating\n")
    mc.stop()
    while(1):
        if cal == 1:
            time.sleep(1)
        elif cal == 0:
            print("Calibrated")
            return

def color_coding(x, y, temp):
    global rx
    global ry

    global ox
    global oy

    it = 0.05
    for i in range(len(grid_order)):
        if gn == grid_order[i]:
            templbx = spX[i]
            tempubx = spX[i] + it
            lby = spY[i]
            uby = spY[i] + it
            ubm = spX[i] + 1

    for i in range(20):
        lbx = templbx
        ubx = tempubx
        for j in range(20):
            if lbx < x < ubx  and lby < y < uby:
                if temp >=25 and temp < 30:
                    ox.append(lbx + (it/2))
                    oy.append(lby + (it/2))
                    return

                elif temp >= 30:
                    rx.append(lbx + (it/2))
                    ry.append(lby + (it/2))
                    return
                
            elif x > ubm and lby < y < uby:
                if ubm < x < (ubm+it):
                    if temp >=25 and temp < 30:
                        ox.append(ubm + (it/2))
                        oy.append(lby + (it/2))
                        return

                    elif temp >= 30:
                        rx.append(ubm + (it/2))
                        ry.append(lby + (it/2))
                        return
                elif (ubm+it) < x < (ubm + (it*2)):
                    if temp >=25 and temp < 30:
                        ox.append((ubm+it) + (it/2))
                        oy.append(lby + (it/2))
                        return

                    elif temp >= 30:
                        rx.append((ubm+it) + (it/2))
                        ry.append(lby + (it/2))
                        return                    
                elif (ubm+(it*2)) < x < (ubm + (it*3)):
                    if temp >=25 and temp < 30:
                        ox.append((ubm + (it*2)) + (it/2))
                        oy.append(lby + (it/2))
                        return

                    elif temp >= 30:
                        rx.append((ubm + (it*2)) + (it/2))
                        ry.append(lby + (it/2))
                        return                    

            else:
                lbx = lbx + it
                ubx = ubx + it       
        lby = lby + it
        uby = uby + it        

def temp_mapping():
    
    global temp_map
    global pos_map_x
    global pos_map_y
    
    pos_map_x.append((position_estimate[1])*-1)
    pos_map_y.append(position_estimate[0])

    temp_map.append(temp2[2])
    temp_map.append(temp2[1])
    temp_map.append(temp2[0])
    temp_map.append(temp2[3])
    temp_map.append(temp2[4])
    temp_map.append(temp2[5])

    temp_map.append(temp3[2])
    temp_map.append(temp3[1])
    temp_map.append(temp3[0])
    temp_map.append(temp3[3])
    temp_map.append(temp3[4])
    temp_map.append(temp3[5])

    temp_map.append(temp4[2])
    temp_map.append(temp4[1])
    temp_map.append(temp4[0])
    temp_map.append(temp4[3])
    temp_map.append(temp4[4])
    temp_map.append(temp4[5])

    temp_map.append(temp5[2])
    temp_map.append(temp5[1])
    temp_map.append(temp5[0])
    temp_map.append(temp5[3])
    temp_map.append(temp5[4])
    temp_map.append(temp5[5])


def error_correction_level1(mc, xe, ye, rotc):
    if rotc == 1:
        y = position_estimate[0]
        
        time.sleep(1)
        error = abs(ye - y)
        
        if error > pos_error:
            error_flag = 1
            while error_flag == 1:
                if error > pos_error:
                    if y < ye:
                        mc.forward(pos_error/4)
                        y = position_estimate[0]
                    elif y > ye:
                        mc.back(pos_error/4)
                        y = position_estimate[0]
                    error = abs(ye - y)
                else:
                    error_flag = 0

        x = position_estimate[1]
        time.sleep(1)
        error = abs(xe - x)
        
        if error > pos_error:
            error_flag = 1
            while error_flag == 1:
                if error > pos_error:
                    if x > xe:
                        mc.right(pos_error/4)
                        x = position_estimate[1]
                    elif x < xe:
                        mc.left(pos_error/4)
                        x = position_estimate[1]
                    error = abs(xe - x)
                else:
                    error_flag = 0

    elif rotc == 2:
        y = position_estimate[0]
        
        time.sleep(1)
        error = abs(ye - y)
        
        if error > pos_error:
            error_flag = 1
            while error_flag == 1:
                if error > pos_error:
                    if y < ye:
                        mc.left(pos_error/4)
                        y = position_estimate[0]
                    elif y > ye:
                        mc.right(pos_error/4)
                        y = position_estimate[0]
                    error = abs(ye - y)
                else:
                    error_flag = 0

        x = position_estimate[1]
        time.sleep(1)
        error = abs(xe - x)
        
        if error > pos_error:
            error_flag = 1
            while error_flag == 1:
                if error > pos_error:
                    if x > xe:
                        mc.forward(pos_error/4)
                        x = position_estimate[1]
                    elif x < xe:
                        mc.back(pos_error/4)
                        x = position_estimate[1]
                    error = abs(xe - x)
                else:
                    error_flag = 0
    
    elif rotc == 3:
        y = position_estimate[0]
        
        time.sleep(1)
        error = abs(ye - y)
        
        if error > pos_error:
            error_flag = 1
            while error_flag == 1:
                if error > pos_error:
                    if y < ye:
                        mc.back(pos_error/4)
                        y = position_estimate[0]
                    elif y > ye:
                        mc.forward(pos_error/4)
                        y = position_estimate[0]
                    error = abs(ye - y)
                else:
                    error_flag = 0

        x = position_estimate[1]
        time.sleep(1)
        error = abs(xe - x)
        
        if error > pos_error:
            error_flag = 1
            while error_flag == 1:
                if error > pos_error:
                    if x > xe:
                        mc.left(pos_error/4)
                        x = position_estimate[1]
                    elif x < xe:
                        mc.right(pos_error/4)
                        x = position_estimate[1]
                    error = abs(xe - x)
                else:
                    error_flag = 0

    elif rotc == 4:
        y = position_estimate[0]
        
        time.sleep(1)
        error = abs(ye - y)
        
        if error > pos_error:
            error_flag = 1
            while error_flag == 1:
                if error > pos_error:
                    if y < ye:
                        mc.right(pos_error/4)
                        y = position_estimate[0]
                    elif y > ye:
                        mc.left(pos_error/4)
                        y = position_estimate[0]
                    error = abs(ye - y)
                else:
                    error_flag = 0

        x = position_estimate[1]
        time.sleep(1)
        error = abs(xe - x)
        
        if error > pos_error:
            error_flag = 1
            while error_flag == 1:
                if error > pos_error:
                    if x > xe:
                        mc.back(pos_error/4)
                        x = position_estimate[1]
                    elif x < xe:
                        mc.forward(pos_error/4)
                        x = position_estimate[1]
                    error = abs(xe - x)
                else:
                    error_flag = 0

    return


def temp_flag():
    print("Hotspot Detected in Grid ", gn)
    global temp_det
    global flag
    flag = flag + 1
    temp_det = 1
    
    

def sweep(mc, mr, fl, rotc, grid_size, partition, xc, yc):
    swX = [0+xc]
    swY = [0+yc]
    swY.append(1+yc)
    swX.append(0+xc)
    i = 0
    i = i + 1
    point = 0
    p_size = grid_size/partition
    pn_size = p_size
    global gn

    if temp_det == 0:
        print("Surveilling Grid ", gn, "\n")
    elif temp_det == 1:
        print("Mapping Grid ", gn, "\n")
    
    for i in range(partition):
        
        if i % 2 == 0:
            swY.append(grid_size+yc)
            swY.append(0+yc)
        else:
            swY.append(0+yc)
            swY.append(grid_size+yc)

        swX.append(pn_size+xc)
        swX.append(pn_size+xc)

        pn_size = pn_size + p_size

    swX.append(0+xc)
    swY.append(0+yc)

    size = len(swX) - 1

    time.sleep(2)


    if temp_det == 0:
        while point != size:
                    
                        xp = swX[point]       
                        yp = swY[point]
                        xn = swX[point+1]
                        yn = swY[point+1]

                        pathing_level2(mc, fl, xn, xp, yn, yp)

                        if temp_det == 1:
                            time.sleep(1)
                            pathing_level2(mc, fl, xc, xn, yc, yn)
                            time.sleep(1)
                            mc.down(0.1)
                            return
                        point = point + 1

    elif temp_det == 1:
        while point != size:
                    
                        xp = swX[point]       
                        yp = swY[point]
                        xn = swX[point+1]
                        yn = swY[point+1]

                        rotc = pathing_level1(mc, mr, fl, xn, xp, yn, yp, rotc)

                        point = point + 1

    return

def pathing_level1(mc, mr, fl, xn, xp, yn, yp, rotc):
                
    j = 0
    y = 0
    x = 0
    yd, xd = 0, 0
    ym, xm = 0, 0

    ye = yn
    xe = xn*-1

    if xp == xn and yp < yn:       
                        
        rotn = 1

        yd = yn - yp
        ym = yd/fl
        ym = int(ym)

        rotc = rotate(mc, rotc, rotn)
        error_correction_level1(mc, xe, yp, rotc)

        for j in range(ym):
            y = move_forward(mc, mr, fl, velocityy)
            temp_mapping()
        y = 0
        j = 0

    elif xp == xn and yp > yn:

        rotn = 3

        yd = yp - yn
        ym = yd/fl
        ym = int(ym)

        rotc = rotate(mc, rotc, rotn)
        error_correction_level1(mc, xe, yp, rotc)

        for j in range(ym):
            y = move_forward(mc, mr, fl, velocityy)
            temp_mapping()
            
        y = 0
        j = 0

    elif xp < xn and yp == yn:

        rotn = 2

        xd = abs(xn - xp)

        rotc = rotate(mc, rotc, rotn)
        error_correction_level1(mc, -abs(xp), ye, rotc)
                        

        y = move_forward(mc, mr, xd, velocityx)
        y = 0
        j = 0

    elif xp > xn and yp == yn:

        rotn = 4

        xd = abs(xp - xn)

        rotc = rotate(mc, rotc, rotn)
        error_correction_level1(mc, -abs(xp), ye, rotc)
            
        y = move_forward(mc, mr, xd, velocityx)
        y = 0
        j = 0

    elif xp < xn and yp < yn:

        rotn = 1

        yd = yn - yp
        ym = yd/fl
        ym = int(ym)

        rotc = rotate(mc, rotc, rotn)

        for j in range(ym):
        
            y = move_forward(mc, mr, fl, velocityx)
        time.sleep(2)
        j = 0
        y = 0
        rotn = 2

        xd = xn - xp
        xm = xd/fl
        xm = int(xm)

        rotc = rotate(mc, rotc, rotn)

        for j in range(xm):
        
            y = move_forward(mc, mr, fl, velocityx)
            
        time.sleep(2)
        y = 0
        j = 0

    elif xp > xn and yp > yn:

        rotn = 3

        yd = yp - yn
        ym = yd/fl
        ym = int(ym)

        rotc = rotate(mc, rotc, rotn)

        for j in range(ym):
        
            y = move_forward(mc, mr, fl, velocityx)
            
        time.sleep(2)
        y = 0
        j = 0

        rotn = 4

        xd = xp - xn
        xm = xd/fl
        xm = int(xm)

        rotc = rotate(mc, rotc, rotn)

        for j in range(xm):
            
            y = move_forward(mc, mr, fl, velocityx)
            
        time.sleep(2)
        y = 0
        j = 0

    elif xp > xn and yp < yn:

        rotn = 1

        yd = yn - yp
        ym = yd/fl
        ym = int(ym)

        rotc = rotate(mc, rotc, rotn)

        for j in range(ym):
            
            y = move_forward(mc, mr, fl, velocityx)
            
        time.sleep(2)
        y = 0
        j = 0

        rotn = 4

        xd = xp - xn
        xm = xd/fl
        xm = int(xm)

        rotc = rotate(mc, rotc, rotn)

        for j in range(xm):
            
            y = move_forward(mc, mr, fl, velocityx)
            
        time.sleep(2)
        y = 0
        j = 0

    elif xp < xn and yp > yn:

        rotn = 3

        yd = yp - yn
        ym = yd/fl
        ym = int(ym)

        rotc = rotate(mc, rotc, rotn)

        for j in range(ym):
        
            y = move_forward(mc, mr, fl, velocityx)
            
        time.sleep(2)
        j = 0

        rotn = 2

        xd = xn - xp
        xm = xd/fl
        xm = int(xm)

        rotc = rotate(mc, rotc, rotn)

        for j in range(xm):
            
            y = move_forward(mc, mr, fl, velocityx)
            
        time.sleep(2)
        y = 0
        j = 0

    error_correction_level1(mc, xe, ye, rotc)

    return rotc
          

def pathing_level2(mc, fl, xn, xp, yn, yp):

    j = 0
    y = 0
    x = 0
    error = 0
    yd, xd = 0, 0
    ym, xm = 0, 0
   
    ye = yn
    xe = xn

    if xp == xn and yp < yn:       
                        
        yd = yn - yp
        ym = yd/fl
        ym = int(ym)

        for j in range(ym):
            if cal == 1:
                calibrate(mc)
            mc.forward(fl, velocity=0.2)     
        j = 0

    elif xp == xn and yp > yn:

        yd = yp - yn
        ym = yd/fl
        ym = int(ym)

        for j in range(ym):
            if cal == 1:
                calibrate(mc)
            mc.back(fl, velocity=0.2)
            
        j = 0

    elif xp < xn and yp == yn:

        xd = xn - xp
        xm = xd/fl
        xm = int(xm)
                        
        for j in range(xm):
            if cal == 1:
                calibrate(mc)
            mc.right(fl, velocity=0.2)
            
        j = 0

    elif xp > xn and yp == yn:

        xd = xp - xn
        xm = xd/fl
        xm = int(xm)

        for j in range(xm):
            if cal == 1:
                calibrate(mc)
            mc.left(fl, velocity=0.2)
        
        j = 0

    elif xp < xn and yp < yn:

        yd = yn - yp
        ym = yd/fl
        ym = int(ym)

        for j in range(ym):
            if cal == 1:
                calibrate(mc)
            mc.forward(fl)
        time.sleep(2)
        j = 0

        xd = xn - xp
        xm = xd/fl
        xm = int(xm)

        for j in range(xm):
            if cal == 1:
                calibrate(mc)
            mc.right(fl)
        time.sleep(2)
        j = 0

    elif xp > xn and yp > yn:

        yd = yp - yn
        ym = yd/fl
        ym = int(ym)

        for j in range(ym):
            if cal == 1:
                calibrate(mc)
            mc.back(fl)
        time.sleep(2)
        j = 0

        xd = xp - xn
        xm = xd/fl
        xm = int(xm)

        for j in range(xm):
            if cal == 1:
                calibrate(mc)
            mc.left(fl)
        time.sleep(2)
        j = 0

    elif xp > xn and yp < yn:

        yd = yn - yp
        ym = yd/fl
        ym = int(ym)

        for j in range(ym):
           if cal == 1:
                calibrate(mc)
           mc.forward(fl)
        time.sleep(2)
        j = 0

        xd = xp - xn
        xm = xd/fl
        xm = int(xm)

        for j in range(xm):
            if cal == 1:
                calibrate(mc)
            mc.left(fl)
        time.sleep(2)
        j = 0

    elif xp < xn and yp > yn:

        yd = yp - yn
        ym = yd/fl
        ym = int(ym)

        for j in range(ym):
            if cal == 1:
                calibrate(mc)
            mc.back(fl)
        time.sleep(2)
        j = 0

        xd = xn - xp
        xm = xd/fl
        xm = int(xm)

        for j in range(xm):
            if cal == 1:
                calibrate(mc)
            mc.right(fl)
        time.sleep(2)
        j = 0

    time.sleep(1)

    x = abs(position_estimate[1])
    y = position_estimate[0]  
    error = abs(ye - y)
        
    if error > pos_error:
        error_flag = 1
        while error_flag == 1:
            if error > pos_error:
                if y < ye:
                    mc.forward(pos_error/4)
                    y = position_estimate[0]
                elif y > ye:
                    mc.back(pos_error/4)
                    y = position_estimate[0]
                error = abs(ye - y)
            else:
                error_flag = 0

    x = abs(position_estimate[1])
    error = abs(xe - x)
        
    if error > pos_error:
        error_flag = 1
        while error_flag == 1:
            if error > pos_error:
                if x < xe:
                    mc.right(pos_error/4)
                    x = abs(position_estimate[1])
                elif x > xe:
                    mc.left(pos_error/4)
                    x = abs(position_estimate[1])
                error = abs(xe - x)
            else:
                error_flag = 0


def my_plotter(ax, ax2, ax3, ax4, x_pos, y_pos, z_pos, pos_map_x, pos_map_y, temp_map): 
    x_pos_l1 = [0]
    y_pos_l1 = [0]
    z_pos_l1 = [0]

    x_pos_l2 = [0]
    y_pos_l2 = [0]
    z_pos_l2 = [0]

    for i in range(len(z_pos)):
        if z_pos[i] > 0.35:
            x_pos_l1.append(x_pos[i])
            y_pos_l1.append(y_pos[i])
            z_pos_l1.append(z_pos[i])
        elif 0.275 < z_pos[i] < 0.35:
            x_pos_l2.append(x_pos[i])
            y_pos_l2.append(y_pos[i])
            z_pos_l2.append(z_pos[i])

    x_pos_l1.pop(0)
    y_pos_l1.pop(0)
    z_pos_l1.pop(0)

    x_pos_l2.pop(0)
    y_pos_l2.pop(0)
    z_pos_l2.pop(0)

    ax.plot3D(x_pos_l1, y_pos_l1, z_pos_l1, 'blue')
    ax.plot3D(x_pos_l2, y_pos_l2, z_pos_l2, 'red')

    ax3.plot(x_pos_l1, y_pos_l1, 'blue')
    ax4.plot(x_pos_l2, y_pos_l2, 'red')

    x = 0
    y = 0
    temp = 0
    #x_change = 0.0315/2
    #y_change = 0.039/2
    x_change = 0.07/2
    y_change = 0.1071/2
    pos_map_x.pop(0)
    pos_map_y.pop(0)
    temp_map.pop(0)
    it1 = 1
    it2 = 1
    count = 0
    t_len = len(temp_map)
    print(t_len, "\n")
    print(len(pos_map_x), "\n")
    
    for i in range(partition2*flag+1):
        if i % 2 == 0:

            for j in range(5):
                for k in range(4):
                    if k == 0:
                        it1 = 1
                        it2 = 1
                        for l in range(6):
                            if l >= 0 and l < 3:
                                x = pos_map_x[j+i*5] - x_change*it1
                                y = pos_map_y[j+i*5] + y_change*3
                                temp = temp_map[l+k*6+j*24+i*120]
                                color_coding(x,y,temp)
                                count = count + 1
                                it1 = it1 + 2
                            elif l >= 3:
                                x = pos_map_x[j+i*5] + x_change*it2
                                y = pos_map_y[j+i*5] + y_change*3
                                temp = temp_map[l+k*6+j*24+i*120]
                                color_coding(x,y,temp)
                                count = count + 1
                                it2 = it2 + 2
                    
                    if k == 1:
                        it1 = 1
                        it2 = 1
                        for l in range(6):
                            if l >= 0 and l < 3:
                                x = pos_map_x[j+i*5] - x_change*it1
                                y = pos_map_y[j+i*5] + y_change
                                temp = temp_map[l+k*6+j*24+i*120]
                                color_coding(x,y,temp)
                                count = count + 1
                                it1 = it1 + 2
                            elif l >= 3:
                                x = pos_map_x[j+i*5] + x_change*it2
                                y = pos_map_y[j+i*5] + y_change
                                temp = temp_map[l+k*6+j*24+i*120]
                                color_coding(x,y,temp)
                                count = count + 1
                                it2 = it2 + 2

                    if k == 2:
                        it1 = 1
                        it2 = 1
                        for l in range(6):
                            if l >= 0 and l < 3:
                                x = pos_map_x[j+i*5] - x_change*it1
                                y = pos_map_y[j+i*5] - y_change
                                temp = temp_map[l+k*6+j*24+i*120]
                                color_coding(x,y,temp)
                                count = count + 1
                                it1 = it1 + 2
                            elif l >= 3:
                                x = pos_map_x[j+i*5] + x_change*it2
                                y = pos_map_y[j+i*5] - y_change
                                temp = temp_map[l+k*6+j*24+i*120]
                                color_coding(x,y,temp)
                                count = count + 1
                                it2 = it2 + 2

                    if k == 3:
                        it1 = 1
                        it2 = 1
                        for l in range(6):
                            if l >= 0 and l < 3:
                                x = pos_map_x[j+i*5] - x_change*it1
                                y = pos_map_y[j+i*5] - y_change*3
                                temp = temp_map[l+k*6+j*24+i*120]
                                color_coding(x,y,temp)
                                count = count + 1
                                it1 = it1 + 2
                            elif l >= 3:
                                x = pos_map_x[j+i*5] + x_change*it2
                                y = pos_map_y[j+i*5] - y_change*3
                                temp = temp_map[l+k*6+j*24+i*120]
                                color_coding(x,y,temp)
                                count = count + 1
                                it2 = it2 + 2

        
                                
        else:
            for j in range(5):
                for k in range(4):
                    if k == 0:
                        it1 = 1
                        it2 = 1
                        for l in range(6):
                            if l >= 0 and l < 3:
                                x = pos_map_x[j+i*5] + x_change*it1
                                y = pos_map_y[j+i*5] - y_change*3
                                temp = temp_map[l+k*6+j*24+i*120]
                                color_coding(x,y,temp)
                                count = count + 1
                                it1 = it1 + 2
                            elif l >= 3:
                                x = pos_map_x[j+i*5] - x_change*it2
                                y = pos_map_y[j+i*5] - y_change*3
                                temp = temp_map[l+k*6+j*24+i*120]
                                color_coding(x,y,temp)
                                count = count + 1
                                it2 = it2 + 2
                    
                    if k == 1:
                        it1 = 1
                        it2 = 1
                        for l in range(6):
                            if l >= 0 and l < 3:
                                x = pos_map_x[j+i*5] + x_change*it1
                                y = pos_map_y[j+i*5] - y_change
                                temp = temp_map[l+k*6+j*24+i*120]
                                color_coding(x,y,temp)
                                count = count + 1
                                it1 = it1 + 2
                            elif l >= 3:
                                x = pos_map_x[j+i*5] - x_change*it2
                                y = pos_map_y[j+i*5] - y_change
                                temp = temp_map[l+k*6+j*24+i*120]
                                color_coding(x,y,temp)
                                count = count + 1
                                it2 = it2 + 2

                    if k == 2:
                        it1 = 1
                        it2 = 1
                        for l in range(6):
                            if l >= 0 and l < 3:
                                x = pos_map_x[j+i*5] + x_change*it1
                                y = pos_map_y[j+i*5] + y_change
                                temp = temp_map[l+k*6+j*24+i*120]
                                color_coding(x,y,temp)
                                count = count + 1
                                it1 = it1 + 2
                            elif l >= 3:
                                x = pos_map_x[j+i*5] - x_change*it2
                                y = pos_map_y[j+i*5] + y_change
                                temp = temp_map[l+k*6+j*24+i*120]
                                color_coding(x,y,temp)
                                count = count + 1
                                it2 = it2 + 2

                    if k == 3:
                        it1 = 1
                        it2 = 1
                        for l in range(6):
                            if l >= 0 and l < 3:
                                x = pos_map_x[j+i*5] + x_change*it1
                                y = pos_map_y[j+i*5] + y_change*3
                                temp = temp_map[l+k*6+j*24+i*120]
                                color_coding(x,y,temp)
                                count = count + 1
                                it1 = it1 + 2
                            elif l >= 3:
                                x = pos_map_x[j+i*5] - x_change*it2
                                y = pos_map_y[j+i*5] + y_change*3
                                temp = temp_map[l+k*6+j*24+i*120]
                                color_coding(x,y,temp)
                                count = count + 1
                                it2 = it2 + 2

    rx.pop(0)
    ry.pop(0)
    bx.pop(0)
    by.pop(0)
    ox.pop(0)
    oy.pop(0)

    ax2.scatter(ox, oy, c = 'tab:orange', s=50)
    ax2.scatter(rx, ry, c = 'tab:red', s=50)

    return

def obs_avoid(mc, mr, fl):

    time.sleep(3)
    ob = 0
    i = 0
    i = i + 0
    x = 0
    y = 0

    while ob != 2:
        
        ob = 0
        flag = 0 

        if is_close(mr.right) and is_close(mr.front) or is_close(mr.front):

            move_left_ob(mc, mr, fl*2)
            x = x + 2

            while flag != 1:
                if is_close(mr.front):
                    while is_close(mr.front):
                        ob = move_left_ob(mc, mr, fl)
                        x = x + 1
                        if ob == 1:
                            flag = 1
                    time.sleep(2)

                else:
                    ob = move_front_ob(mc, mr, fl*5)
                    y = y + 5
                    if ob == 1:
                        flag = 1
                    elif is_close(mr.right):
                        time.sleep(2)
                        while is_close(mr.right):
                            ob = move_front_ob(mc, mr, fl)
                            y =  y + 1
                            if ob == 1:
                                flag = 1
                        time.sleep(2)
                    else: 
                        for i in range(x):
                            move_right_ob(mc, mr, fl)
                        flag = 1
                        ob = 2

        if is_close(mr.left) and is_close(mr.front):

            move_right_ob(mc,mr, fl*2)
            x = x + 2

            while flag != 1:
                if is_close(mr.front):
                    while is_close(mr.front):
                        ob = move_right_ob(mc, mr, fl)
                        x = x + 1
                        if ob == 1:
                            flag = 1
                    time.sleep(2)

                else:
                    ob = move_front_ob(mc, mr, fl*5)
                    y = y + 5
                    if ob == 1:
                        flag = 1
                    elif is_close(mr.left):
                        time.sleep(2)
                        while is_close(mr.left):
                            ob = move_front_ob(mc, mr, fl)
                            y =  y + 1
                            if ob == 1:
                                flag = 1
                        time.sleep(2)
                    else: 
                        for i in range(x):
                            move_left_ob(mc, mr, fl)
                        flag = 1
                        ob = 2   

        if is_close(mr.left) and is_close(mr.right):

            move_back_ob(mc,mr, fl*2)
            y = y - 2

            while flag != 1:
                if is_close(mr.left) and is_close(mr.right):
                    while is_close(mr.left) and is_close(mr.right):
                        ob = move_back_ob(mc, mr, fl)
                        y = y - 1
                    time.sleep(2)

                elif is_close(mr.left) and not is_close(mr.right):
                    ob = move_right_ob(mc, mr, fl*2)
                    x = x + 2
                    if ob == 1:
                        flag = 1
                    if is_close(mr.front):
                        time.sleep(2)
                        while is_close(mr.front):
                            ob = move_right_ob(mc, mr, fl)
                            x =  x + 1
                            if ob == 1:
                                flag = 1
                        time.sleep(2)
                    else: 
                        ob = move_front_ob(mc, mr, fl*5)
                        y = y + 5
                        if is_close(mr.left):
                            while is_close(mr.left):
                                ob = move_front_ob(mc, mr, fl)
                                y = y + 1
                                if ob == 1:
                                    flag = 1
                            
                            for i in range(x):
                                move_left_ob(mc, mr, fl)
                            flag = 1
                            ob = 2   
                        
                elif not is_close(mr.left) and is_close(mr.right):
                    ob = move_left_ob(mc, mr, fl*2)
                    x = x + 2
                    if ob == 1:
                        flag = 1
                    if is_close(mr.front):
                        time.sleep(2)
                        while is_close(mr.front):
                            ob = move_left_ob(mc, mr, fl)
                            x =  x + 1
                            if ob == 1:
                                flag = 1
                        time.sleep(2)
                    else: 
                        ob = move_front_ob(mc, mr, fl*5)
                        y = y + 5
                        if is_close(mr.right):
                            while is_close(mr.right):
                                ob = move_front_ob(mc, mr, fl)
                                y = y + 1
                                if ob == 1:
                                    flag = 1
                            
                            for i in range(x):
                                move_right_ob(mc, mr, fl)
                            flag = 1
                            ob = 2
    return y


def move_forward(mc, mr, fl, velocity):
    mc.forward(fl, velocity)

    """if is_close(mr.front):
        mc.stop()
        y = obs_avoid(mc, mr, fl)
        return y
    else:
        return 0"""

def move_front_ob(mc, mr, fl):
    mc.forward(fl, velocityy)
    if is_close(mr.front):
        mc.stop()
        return 1
    else:
        return
    
def move_right_ob(mc, mr, fl):
    mc.right(fl, velocityy)
    if is_close(mr.right):
        mc.stop()
        return 1
    else:
        return
    
    
def move_left_ob(mc, mr, fl):
    mc.left(fl, velocityy)
    if is_close(mr.left):
        mc.stop()
        return 1
    else:
        return
    
def move_back_ob(mc, mr, fl):
    mc.back(fl, velocityy)
    return

def rotate(mc, rotc, rotn):
    
    rot = 0
    deg = 90
    d_rate = 30
    k = 0 
    k = k + 0
    d = 3
    c = rotc
    n = rotn

    if c == n:
        return rotc
    
    elif c < n:
        rot = n - c
        
        if rot == d:
            mc.turn_left(deg, d_rate)
        
        else:
            for k in range(rot):
                mc.turn_right(deg, d_rate)
            k = 0
    
    elif c > n:
        rot = c - n
        if rot == d:
            mc.turn_right(deg, d_rate)
        else: 
            for k in range(rot):
                mc.turn_left(deg, d_rate)
            k = 0
    
    rotc = rotn
    return rotc
        


def is_close(range):
    MIN_DISTANCE = 0.3

    if range is None:
        return False
    else:
        return range < MIN_DISTANCE

def log_pos_callback(timestamp, data, logconf):
    pos_file.write("Y:{},X:{},Z:{}\n".format(data['stateEstimate.x'], -1*data['stateEstimate.y'], data['stateEstimate.z']))
    global x_pos
    global y_pos
    global z_pos
    global yaw
    global position_estimate
    global t

    position_estimate[0] = data['stateEstimate.x']
    position_estimate[1] = data['stateEstimate.y']
    yaw = data['stateEstimate.yaw']
    y_pos.append(data['stateEstimate.x'])
    x_pos.append(data['stateEstimate.y']*-1)
    z_pos.append(data['stateEstimate.z'])
    t = timestamp
    

def log_temp_callback(timestamp, data, logconf):
    global count_temp
    global cal
    global hold
    thres2 = 24

    if count_temp == 6:
        temp_file.write("\n")
        count_temp = 0

    temp_file.write("{},{}\n".format(data, position_estimate))
    count_temp = count_temp + 1

    if logconf.name == 'Temp1':
        temp1[0] = data['MLX1.To6']
        temp1[1] = data['MLX1.To5']
        temp1[2] = data['MLX1.To4']
        temp1[3] = data['MLX1.To3']
        temp1[4] = data['MLX1.To2']
        temp1[5] = data['MLX1.To1']

        if (temp1[0] or temp1[1] or temp1[2] or temp1[3] or temp1[4] or temp1[5]) > thres2 and hold == 0:
            temp_flag()
            hold = 1

    elif logconf.name == 'Temp2':
        temp2[0] = data['MLX2.To6']
        temp2[1] = data['MLX2.To5']
        temp2[2] = data['MLX2.To4']
        temp2[3] = data['MLX2.To3']
        temp2[4] = data['MLX2.To2']
        temp2[5] = data['MLX2.To1']
               
        if (temp2[0] or temp2[1] or temp2[2] or temp2[3] or temp2[4] or temp2[5]) > thres2 and hold == 0:
            temp_flag()
            hold = 1

    
    elif logconf.name == 'Temp3':
        temp3[0] = data['MLX3.To6']
        temp3[1] = data['MLX3.To5']
        temp3[2] = data['MLX3.To4']
        temp3[3] = data['MLX3.To3']
        temp3[4] = data['MLX3.To2']
        temp3[5] = data['MLX3.To1']

        if (temp3[0] or temp3[1] or temp3[2] or temp3[3] or temp3[4] or temp3[5]) > thres2 and hold == 0:
            temp_flag()
            hold = 1

    elif logconf.name == 'Temp4':
        temp4[0] = data['MLX4.To6']
        temp4[1] = data['MLX4.To5']
        temp4[2] = data['MLX4.To4']
        temp4[3] = data['MLX4.To3']
        temp4[4] = data['MLX4.To2']
        temp4[5] = data['MLX4.To1']
            
        if (temp4[0] or temp4[1] or temp4[2] or temp4[3] or temp4[4] or temp4[5]) > thres2 and hold == 0:
            temp_flag()
            hold = 1

    elif logconf.name == 'Temp5':
        temp5[0] = data['MLX5.To6']
        temp5[1] = data['MLX5.To5']
        temp5[2] = data['MLX5.To4']
        temp5[3] = data['MLX5.To3']
        temp5[4] = data['MLX5.To2']
        temp5[5] = data['MLX5.To1']

        if (temp5[0] or temp5[1] or temp5[2] or temp5[3] or temp5[4] or temp5[5]) > thres2 and hold == 0:
            temp_flag()
            hold = 1

    elif logconf.name == 'Temp6':
        temp6[0] = data['MLX6.To6']
        temp6[1] = data['MLX6.To5']
        temp6[2] = data['MLX6.To4']
        temp6[3] = data['MLX6.To3']
        temp6[4] = data['MLX6.To2']
        temp6[5] = data['MLX6.To1']

        if (temp6[0] or temp6[1] or temp6[2] or temp6[3] or temp6[4] or temp6[5]) > thres2 and hold == 0:
            temp_flag()
            hold = 1


def param_deck_flow(_, value_str):
    value = int(value_str)
    print(value)
    if value:
        deck_attached_event.set()
        print('Deck is attached!')
    else:
        print('Deck is NOT attached!')

def reset_estimator(scf):
    cf = scf.cf
    cf.param.set_value('kalman.resetEstimation', '1')
    time.sleep(0.1)
    cf.param.set_value('kalman.resetEstimation', '0')
    print("Estimator Reset\n")

def wait_for_position_estimator(scf):
        print("Waiting for Estimator to Stabilize\n")
        log_config = LogConfig(name='Kalman Variance', period_in_ms=500)
        log_config.add_variable('kalman.varPX', 'float')
        log_config.add_variable('kalman.varPY', 'float')
        log_config.add_variable('kalman.varPZ', 'float')

        var_y_history = [1000] * 10
        var_x_history = [1000] * 10
        var_z_history = [1000] * 10

        threshold = 0.001

        with SyncLogger(scf, log_config) as logger:
            for log_entry in logger:
                data = log_entry[1]

                var_x_history.append(data['kalman.varPX'])
                var_x_history.pop(0)
                var_y_history.append(data['kalman.varPY'])
                var_y_history.pop(0)
                var_z_history.append(data['kalman.varPZ'])
                var_z_history.pop(0)

                min_x = min(var_x_history)
                max_x = max(var_x_history)
                min_y = min(var_y_history)
                max_y = max(var_y_history)
                min_z = min(var_z_history)
                max_z = max(var_z_history)

                if (max_x - min_x) < threshold and (
                        max_y - min_y) < threshold and (
                        max_z - min_z) < threshold:
                    break
        print("Estimator Stabilized\n")

if __name__ == '__main__':
    cflib.crtp.init_drivers()

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:

        #reset_estimator(scf)

        fig = plt.figure(figsize=plt.figaspect(4.))
        ax = fig.add_subplot(4, 1, 1, projection='3d')
        ax2 = fig.add_subplot(4, 1, 4)
        ax3 = fig.add_subplot(4, 1, 2)
        ax4 = fig.add_subplot(4, 1, 3)

        pos_file = open('pos_data.txt', "w")
        pos_file.close()
        pos_file = open('pos_data.txt', "a")

        temp_file = open('temp_data.txt', "w")
        temp_file.close()
        temp_file = open('temp_data.txt', "a")

        scf.cf.param.add_update_callback(group='deck', name='bcFlow2', cb=param_deck_flow)

        logconf = LogConfig(name='Position', period_in_ms=250) 
        logconf.add_variable('stateEstimate.x', 'float')
        logconf.add_variable('stateEstimate.y', 'float')
        logconf.add_variable('stateEstimate.z', 'float')
        logconf.add_variable('stateEstimate.yaw', 'float')
        scf.cf.log.add_config(logconf)
        logconf.data_received_cb.add_callback(log_pos_callback)

        logconf1 = LogConfig(name='Temp1', period_in_ms=1000) 
        logconf1.add_variable('MLX1.To1', 'float')
        logconf1.add_variable('MLX1.To2', 'float')
        logconf1.add_variable('MLX1.To3', 'float')
        logconf1.add_variable('MLX1.To4', 'float')
        logconf1.add_variable('MLX1.To5', 'float')
        logconf1.add_variable('MLX1.To6', 'float')
        scf.cf.log.add_config(logconf1)
        logconf1.data_received_cb.add_callback(log_temp_callback)

        logconf2 = LogConfig(name='Temp2', period_in_ms=1000) 
        logconf2.add_variable('MLX2.To1', 'float')
        logconf2.add_variable('MLX2.To2', 'float')
        logconf2.add_variable('MLX2.To3', 'float')
        logconf2.add_variable('MLX2.To4', 'float')
        logconf2.add_variable('MLX2.To5', 'float')
        logconf2.add_variable('MLX2.To6', 'float')
        scf.cf.log.add_config(logconf2)
        logconf2.data_received_cb.add_callback(log_temp_callback)

        logconf3 = LogConfig(name='Temp3', period_in_ms=1000) 
        logconf3.add_variable('MLX3.To1', 'float')
        logconf3.add_variable('MLX3.To2', 'float')
        logconf3.add_variable('MLX3.To3', 'float')
        logconf3.add_variable('MLX3.To4', 'float')
        logconf3.add_variable('MLX3.To5', 'float')
        logconf3.add_variable('MLX3.To6', 'float')
        scf.cf.log.add_config(logconf3)
        logconf3.data_received_cb.add_callback(log_temp_callback)

        logconf4 = LogConfig(name='Temp4', period_in_ms=1000) 
        logconf4.add_variable('MLX4.To1', 'float')
        logconf4.add_variable('MLX4.To2', 'float')
        logconf4.add_variable('MLX4.To3', 'float')
        logconf4.add_variable('MLX4.To4', 'float')
        logconf4.add_variable('MLX4.To5', 'float')
        logconf4.add_variable('MLX4.To6', 'float')
        scf.cf.log.add_config(logconf4)
        logconf4.data_received_cb.add_callback(log_temp_callback)

        logconf5 = LogConfig(name='Temp5', period_in_ms=1000) 
        logconf5.add_variable('MLX5.To1', 'float')
        logconf5.add_variable('MLX5.To2', 'float')
        logconf5.add_variable('MLX5.To3', 'float')
        logconf5.add_variable('MLX5.To4', 'float')
        logconf5.add_variable('MLX5.To5', 'float')
        logconf5.add_variable('MLX5.To6', 'float')
        scf.cf.log.add_config(logconf5)
        logconf5.data_received_cb.add_callback(log_temp_callback)

        logconf6 = LogConfig(name='Temp6', period_in_ms=1000) 
        logconf6.add_variable('MLX6.To1', 'float')
        logconf6.add_variable('MLX6.To2', 'float')
        logconf6.add_variable('MLX6.To3', 'float')
        logconf6.add_variable('MLX6.To4', 'float')
        logconf6.add_variable('MLX6.To5', 'float')
        logconf6.add_variable('MLX6.To6', 'float')
        scf.cf.log.add_config(logconf6)
        logconf6.data_received_cb.add_callback(log_temp_callback)

        i = 0
        j = 0
                
        pointX = 0
        pointY = 0
        grid_num_y = map_length_y/grid_size
        grid_num_x = map_length_x/grid_size
        grid_num_y = int(grid_num_y)
        grid_num_x = int(grid_num_x)
        global spY
        global spX
        spY = [0] 
        spX = [0] 


        for i in range(grid_num_x):
                    
            for j in range(grid_num_y):
                spY.append(pointY)
                spX.append(pointX)
                pointY = pointY + grid_size
            pointX = pointX + grid_size
            pointY = 0
        
        grid_num = map_length_x * map_length_y

        spX.pop(0)
        spY.pop(0)
        global grid_order
        grid_order = [0]

        i = 1
        for i in range(grid_num):
                    grid_order.append(i + 1)

        grid_order.pop(0)

        point = 0
        rotc = 1
        rotc = int(rotc)     
        global gn  
        gn = grid_order[0] 

        logconf.start() 

        with MotionCommander(scf, default_height = 0.4) as mc:    
            #with Multiranger(scf) as mr:
                mr = 0
                time.sleep(1)
                
                logconf1.start()
                logconf2.start()
                logconf3.start()
                logconf4.start()
                logconf5.start()
                logconf6.start()    

                time.sleep(2)   

                while point != grid_num:

                    xp = spX[point]       
                    yp = spY[point]
                    
                    if point < grid_num - 1:
                        xn = spX[point+1]
                        yn = spY[point+1] 

                    sweep(mc, mr, fl, rotc, grid_size, partition1, xp, yp)

                    if temp_det == 1:
                        sweep(mc, mr, fl, rotc, grid_size, partition2, xp, yp)
                        time.sleep(1)
                        mc.up(0.1)
                        time.sleep(2)
                        mc.turn_right(90, 30)

                    if point < grid_num - 1:
                        
                        pathing_level2(mc, fl, xn, xp, yn, yp)

                        gn = grid_order[point + 1]
                    
                    if temp_det == 1:
                        temp_det = 0
                        hold = 0

                    point = point + 1

                logconf.stop()
                logconf1.stop()
                logconf2.stop()
                logconf3.stop()
                logconf5.stop()
                logconf5.stop()
                logconf6.stop()
                pos_file.close()
                temp_file.close()
                
                my_plotter(ax, ax2, ax3, ax4, x_pos, y_pos, z_pos, pos_map_x, pos_map_y, temp_map)

                ax.set_title('3D Drone Trajectory')
                ax.view_init(elev = 20, azim = -120, roll = 0)

                ax2.set_title('Temperature Map')
                ax2.set_xlim(left=-0.2, right=map_length_x+0.2)
                ax2.set_ylim(bottom=-0.2, top=map_length_y+0.2)

                ax3.set_title('Level 1 Drone Trajectory')
                ax3.set_xlim(left=-0.2, right=map_length_x+0.2)
                ax3.set_ylim(bottom=-0.2, top=map_length_y+0.2)
    

                ax4.set_title('Level 2 Drone Trajectory')
                ax4.set_xlim(left=-0.2, right=map_length_x+0.2)
                ax4.set_ylim(bottom=-0.2, top=map_length_y+0.2)

                plt.show()
