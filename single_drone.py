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

import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

x_pos = [0]
y_pos = [0]
z_pos = [0]
height_estimate = 0
temp1 = [0,0,0,0,0,0]
temp2 = [0,0,0,0,0,0]
temp3 = [0,0,0,0,0,0]
temp4 = [0,0,0,0,0,0]
temp5 = [0,0,0,0,0,0]
temp6 = [0,0,0,0,0,0]
thres = 24
t = 0
grid_size = 1 
partition = 2
temp_flag = 0
map_length_y = 2
map_length_x = 1
grid_num = 0
grid_order = [1]
fl = 0.1
velocity = 0.1

deck_attached_event = Event()

def temp_flag():
    print("Hotspot Detected in Grid ", gn)
    return 

def sweep(mc, mr, fl, rotc, grid_size, partition):
    swX = [0]
    swY = [0]
    swY.append(0)
    i = 0
    i = i + 1
    point = 0
    p_size = grid_size/partition
    pn_size = p_size

    print("Surveilling Grid ", gn, "\n")
    
    for i in range(partition):
        
        if i % 2 == 0:
            swY.append(grid_size)
            swY.append(grid_size)
        else:
            swY.append(0)
            swY.append(0)

        swX.append(pn_size)
        swX.append(pn_size)

        pn_size = pn_size + p_size

    swX.append(0)

    size = len(swX) - 1

    time.sleep(2)

    while point != size:
                    
                    xp = swX[point]       
                    yp = swY[point]
                    xn = swX[point+1]
                    yn = swY[point+1]

                    rotc = pathing(mc, mr, fl, xn, xp, yn, yp, rotc)
                    point = point + 1

    return rotc
          

def pathing(mc, mr, fl, xn, xp, yn, yp, rotc):

    j = 0
    y = 0
    yd, xd = 0, 0
    ym, xm = 0, 0
    if xp == xn and yp < yn:       
                        
        rotn = 1
        yd = yn - yp
        ym = yd/fl
        ym = int(ym)

        rotc = rotate(mc, rotc, rotn)

        for j in range(ym):
            y = move_forward(mc, mr, fl)
            if y > 0:
                j = j + y
        time.sleep(2)
        y = 0
        j = 0

    elif xp == xn and yp > yn:

        rotn = 3
        yd = yp - yn
        ym = yd/fl
        ym = int(ym)

        rotc = rotate(mc, rotc, rotn)

        for j in range(ym):
            y = move_forward(mc, mr, fl)
            if y > 0:
                j = j + y
        time.sleep(2)
        y = 0
        j = 0

    elif xp < xn and yp == yn:

        rotn = 2
        xd = xn - xp
        xm = xd/fl
        xm = int(xm)

        rotc = rotate(mc, rotc, rotn)
                        
        for j in range(xm):
            y = move_forward(mc, mr, fl)
            if y > 0:
                j = j + y
        time.sleep(2)
        y = 0
        j = 0

    elif xp > xn and yp == yn:

        rotn = 4
        xd = xp - xn
        xm = xd/fl
        xm = int(xm)

        rotc = rotate(mc, rotc, rotn)

        for m in range(xm):
            y = move_forward(mc, mr, fl)
            if y > 0:
                j = j + y
        time.sleep(2)
        y = 0
        j = 0

    elif xp < xn and yp < yn:

        rotn = 1
        yd = yn - yp
        ym = yd/fl
        ym = int(ym)

        rotc = rotate(mc, rotc, rotn)

        for j in range(ym):
            y = move_forward(mc, mr, fl)
            if y > 0:
                j = j + y
        time.sleep(2)
        j = 0
        y = 0
        rotn = 2

        xd = xn - xp
        xm = xd/fl
        xm = int(xm)

        rotc = rotate(mc, rotc, rotn)

        for j in range(xm):
            y = move_forward(mc, mr, fl)
            if y > 0:
                j = j + y
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
            y = move_forward(mc, mr, fl)
            if y > 0:
                j = j + y
        time.sleep(2)
        y = 0
        j = 0

        rotn = 4

        xd = xp - xn
        xm = xd/fl
        xm = int(xm)

        rotc = rotate(mc, rotc, rotn)

        for j in range(xm):
            y = move_forward(mc, mr, fl)
            if y > 0:
                j = j + y
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
            y = move_forward(mc, mr, fl)
            if y > 0:
                j = j + y
        time.sleep(2)
        y = 0
        j = 0

        rotn = 4

        xd = xp - xn
        xm = xd/fl
        xm = int(xm)

        rotc = rotate(mc, rotc, rotn)

        for j in range(xm):
            y = move_forward(mc, mr, fl)
            if y > 0:
                j = j + y
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
            y = move_forward(mc, mr, fl)
            if y > 0:
                j = j + y
        time.sleep(2)
        j = 0

        rotn = 2

        xd = xn - xp
        xm = xd/fl
        xm = int(xm)

        rotc = rotate(mc, rotc, rotn)

        for j in range(xm):
            y = move_forward(mc, mr, fl)
            if y > 0:
                j = j + y
        time.sleep(2)
        y = 0
        j = 0

    return rotc


def my_plotter(ax, data1, data2, data3):
    out = ax.plot3D(data1, data2, data3, 'blue')
    return out

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


def move_forward(mc, mr, fl):
    mc.forward(fl, velocity)

    if is_close(mr.front):
        mc.stop()
        y = obs_avoid(mc, mr, fl)
        return y
    else:
        return 0

def move_front_ob(mc, mr, fl):
    mc.forward(fl, velocity)
    if is_close(mr.front):
        mc.stop()
        return 1
    else:
        return
    
def move_right_ob(mc, mr, fl):
    mc.right(fl, velocity)
    if is_close(mr.right):
        mc.stop()
        return 1
    else:
        return
    
    
def move_left_ob(mc, mr, fl):
    mc.left(fl, velocity)
    if is_close(mr.left):
        mc.stop()
        return 1
    else:
        return
    
def move_back_ob(mc, mr, fl):
    mc.back(fl, velocity)
    return

def rotate(mc, rotc, rotn):
    
    rot = 0
    deg = 90
    d_rate = 45
    k = 0 
    k = k + 0

    if rotc == rotn:
        return rotc
    
    elif rotc == 4 and rotn == 1:
        mc.turn_right(deg, d_rate)

    elif rotc < rotn:
        rot = rotn - rotc
        if rot < 3:
            for k in range(rot):
                mc.turn_right(deg, d_rate)
            k = 0
            rotc = rotn
        elif rot == 3:
            mc.turn_left(deg, d_rate)
        return rotc
    
    elif rotc > rotn:
        rot = rotc - rotn
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
    pos_file.write("Y:{},X:{},Z:{}\n".format(data['stateEstimate.x'], data['stateEstimate.y'], data['stateEstimate.z']))
    global x_pos
    global y_pos
    global z_pos
    global t
    global height_estimate
    height_estimate = data['stateEstimate.z']
    x_pos.append(data['stateEstimate.x'])
    y_pos.append(data['stateEstimate.y'])
    z_pos.append(data['stateEstimate.z'])
    t = timestamp
    

def log_temp_callback(timestamp, data, logconf):
    temp_file.write("{}\n".format(data))

    global temp

    if logconf.name == 'Temp1':
        temp1[0] = data['MLX1.To1']
        temp1[1] = data['MLX1.To2']
        temp1[2] = data['MLX1.To3']
        temp1[3] = data['MLX1.To4']
        temp1[4] = data['MLX1.To5']
        temp1[5] = data['MLX1.To6']
        print(temp1[0], ' | ',temp1[1], ' | ',temp1[2], ' | ',temp1[3], ' | ',temp1[4], ' | ',temp1[5], '\n')
        if (temp1[0] or temp1[1] or temp1[2] or temp1[3] or temp1[4] or temp1[5]) > 24:
            temp_flag()

    elif logconf.name == 'Temp2':
        temp2[0] = data['MLX2.To1']
        temp2[1] = data['MLX2.To2']
        temp2[2] = data['MLX2.To3']
        temp2[3] = data['MLX2.To4']
        temp2[4] = data['MLX2.To5']
        temp2[5] = data['MLX2.To6']
        print(temp2[0], ' | ',temp2[1], ' | ',temp2[2], ' | ',temp2[3], ' | ',temp2[4], ' | ',temp2[5], '\n')
        if (temp2[0] or temp2[1] or temp2[2] or temp2[3] or temp2[4] or temp2[5]) > 24:
            temp_flag()

    
    elif logconf.name == 'Temp3':
        temp3[0] = data['MLX3.To1']
        temp3[1] = data['MLX3.To2']
        temp3[2] = data['MLX3.To3']
        temp3[3] = data['MLX3.To4']
        temp3[4] = data['MLX3.To5']
        temp3[5] = data['MLX3.To6']
        print(temp3[0], ' | ',temp3[1], ' | ',temp3[2], ' | ',temp3[3], ' | ',temp3[4], ' | ',temp3[5], '\n')
        if (temp3[0] or temp3[1] or temp3[2] or temp3[3] or temp3[4] or temp3[5]) > 24:
            temp_flag()

    elif logconf.name == 'Temp4':
        temp4[0] = data['MLX4.To1']
        temp4[1] = data['MLX4.To2']
        temp4[2] = data['MLX4.To3']
        temp4[3] = data['MLX4.To4']
        temp4[4] = data['MLX4.To5']
        temp4[5] = data['MLX4.To6']
        print(temp4[0], ' | ',temp4[1], ' | ',temp4[2], ' | ',temp4[3], ' | ',temp4[4], ' | ',temp4[5], '\n')
        if (temp4[0] or temp4[1] or temp4[2] or temp4[3] or temp4[4] or temp4[5]) > 24:
            temp_flag()

    elif logconf.name == 'Temp5':
        temp5[0] = data['MLX5.To1']
        temp5[1] = data['MLX5.To2']
        temp5[2] = data['MLX5.To3']
        temp5[3] = data['MLX5.To4']
        temp5[4] = data['MLX5.To5']
        temp5[5] = data['MLX5.To6']
        print(temp5[0], ' | ',temp5[1], ' | ',temp5[2], ' | ',temp5[3], ' | ',temp5[4], ' | ',temp5[5], '\n')
        if (temp5[0] or temp5[1] or temp5[2] or temp5[3] or temp5[4] or temp5[5]) > 24:
            temp_flag()

    elif logconf.name == 'Temp6':
        temp6[0] = data['MLX6.To1']
        temp6[1] = data['MLX6.To2']
        temp6[2] = data['MLX6.To3']
        temp6[3] = data['MLX6.To4']
        temp6[4] = data['MLX6.To5']
        temp6[5] = data['MLX6.To6']
        print(temp5[0], ' | ',temp5[1], ' | ',temp5[2], ' | ',temp5[3], ' | ',temp5[4], ' | ',temp5[5], '\n')
        if (temp6[0] or temp6[1] or temp6[2] or temp6[3] or temp6[4] or temp6[5]) > 24:
            temp_flag ()


def param_deck_flow(_, value_str):
    value = int(value_str)
    print(value)
    if value:
        deck_attached_event.set()
        print('Deck is attached!')
    else:
        print('Deck is NOT attached!')

if __name__ == '__main__':
    cflib.crtp.init_drivers()

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:

        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')

        pos_file = open('pos_data.txt', "w")
        pos_file.close()
        pos_file = open('pos_data.txt', "a")

        temp_file = open('temp_data.txt', "w")
        temp_file.close()
        temp_file = open('temp_data.txt', "a")

        scf.cf.param.add_update_callback(group='deck', name='bcFlow2', cb=param_deck_flow)

        logconf = LogConfig(name='Position', period_in_ms=500) 
        logconf.add_variable('stateEstimate.x', 'float')
        logconf.add_variable('stateEstimate.y', 'float')
        logconf.add_variable('stateEstimate.z', 'float')
        scf.cf.log.add_config(logconf)
        logconf.data_received_cb.add_callback(log_pos_callback)

        logconf1 = LogConfig(name='Temp1', period_in_ms=500) 
        logconf1.add_variable('MLX1.To1', 'float')
        logconf1.add_variable('MLX1.To2', 'float')
        logconf1.add_variable('MLX1.To3', 'float')
        logconf1.add_variable('MLX1.To4', 'float')
        logconf1.add_variable('MLX1.To5', 'float')
        logconf1.add_variable('MLX1.To6', 'float')
        scf.cf.log.add_config(logconf1)
        logconf1.data_received_cb.add_callback(log_temp_callback)

        logconf2 = LogConfig(name='Temp2', period_in_ms=500) 
        logconf2.add_variable('MLX2.To1', 'float')
        logconf2.add_variable('MLX2.To2', 'float')
        logconf2.add_variable('MLX2.To3', 'float')
        logconf2.add_variable('MLX2.To4', 'float')
        logconf2.add_variable('MLX2.To5', 'float')
        logconf2.add_variable('MLX2.To6', 'float')
        scf.cf.log.add_config(logconf2)
        logconf2.data_received_cb.add_callback(log_temp_callback)

        logconf3 = LogConfig(name='Temp3', period_in_ms=500) 
        logconf3.add_variable('MLX3.To1', 'float')
        logconf3.add_variable('MLX3.To2', 'float')
        logconf3.add_variable('MLX3.To3', 'float')
        logconf3.add_variable('MLX3.To4', 'float')
        logconf3.add_variable('MLX3.To5', 'float')
        logconf3.add_variable('MLX3.To6', 'float')
        scf.cf.log.add_config(logconf3)
        logconf3.data_received_cb.add_callback(log_temp_callback)

        logconf4 = LogConfig(name='Temp4', period_in_ms=500) 
        logconf4.add_variable('MLX4.To1', 'float')
        logconf4.add_variable('MLX4.To2', 'float')
        logconf4.add_variable('MLX4.To3', 'float')
        logconf4.add_variable('MLX4.To4', 'float')
        logconf4.add_variable('MLX4.To5', 'float')
        logconf4.add_variable('MLX4.To6', 'float')
        scf.cf.log.add_config(logconf4)
        logconf4.data_received_cb.add_callback(log_temp_callback)

        logconf5 = LogConfig(name='Temp5', period_in_ms=500) 
        logconf5.add_variable('MLX5.To1', 'float')
        logconf5.add_variable('MLX5.To2', 'float')
        logconf5.add_variable('MLX5.To3', 'float')
        logconf5.add_variable('MLX5.To4', 'float')
        logconf5.add_variable('MLX5.To5', 'float')
        logconf5.add_variable('MLX5.To6', 'float')
        scf.cf.log.add_config(logconf5)
        logconf5.data_received_cb.add_callback(log_temp_callback)

        logconf6 = LogConfig(name='Temp6', period_in_ms=500) 
        logconf6.add_variable('MLX6.To1', 'float')
        logconf6.add_variable('MLX6.To2', 'float')
        logconf6.add_variable('MLX6.To3', 'float')
        logconf6.add_variable('MLX6.To4', 'float')
        logconf6.add_variable('MLX6.To5', 'float')
        logconf6.add_variable('MLX6.To6', 'float')
        scf.cf.log.add_config(logconf6)
        logconf6.data_received_cb.add_callback(log_temp_callback)

        
        with MotionCommander(scf) as mc:    
            with Multiranger(scf) as mr:

                time.sleep(2)
                logconf.start()  
                logconf1.start()
                logconf2.start()
                logconf3.start()
                logconf4.start()
                logconf5.start()
                logconf6.start()    

                i = 0
                j = 0
                
                pointX = 0
                pointY = grid_size
                grid_num_y = map_length_y/grid_size
                grid_num_x = map_length_x/grid_size
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

                i = 1
                for i in range(grid_num):
                    grid_order.append(i + 1)

                size = len(spX) - 1
                point = 0
                rotc = 1     
                global gn   

                print(spX, "\n")
                print(spY, "\n")    

                time.sleep(20)                         

                while point != size:
                    
                    xp = spX[point]       
                    yp = spY[point]
                    xn = spX[point+1]
                    yn = spY[point+1] 
                    gn = grid_num[point + 1]

                    rotc = sweep(mc, mr, fl, rotc, grid_size, partition)

                    rotc = pathing(mc, mr, fl, xn, xp, yn, yp, rotc)

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
                print("Temperature Flag: ", temp_flag, "\n")
                my_plotter(ax, x_pos, y_pos, z_pos)
                ax.set_title('Drone Trajectory')
                plt.show()
