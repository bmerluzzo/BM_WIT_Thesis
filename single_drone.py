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

URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E8')

x_pos = [0]
y_pos = [0]
z_pos = [0]
height_estimate = 0
temp = [0,0,0,0,0,0]
thres = 24
t = 0
spX = [0, 0]
spY = [0, 3]
fl = 0.1
df = 0.3
chh = 0


deck_attached_event = Event()

def my_plotter(ax, data1, data2, data3, param_dict):
    out = ax.plot3D(data1, data2, data3, **param_dict)
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
    mc.forward(fl)
    #if (temp[0] or temp[1] or temp[2] or temp[3] or temp[4] or temp[5]) > 24:t
        #print('Exceeded\n')
    if height_estimate < mc.default_height:
        mc.stop()
        chh = mc.default_height - height_estimate[3]
        time.sleep(2)
        mc.down(chh)
    elif is_close(mr.front):
        mc.stop()
        y = obs_avoid(mc, mr, fl)
        return y
    else:
        return 0

def move_front_ob(mc, mr, fl):
    mc.forward(fl)
    if is_close(mr.front):
        mc.stop()
        return 1
    else:
        return
    
def move_right_ob(mc, mr, fl):
    mc.right(fl)
    if is_close(mr.right):
        mc.stop()
        return 1
    else:
        return
    
    
def move_left_ob(mc, mr, fl):
    mc.left(fl)
    if is_close(mr.left):
        mc.stop()
        return 1
    else:
        return
    
def move_back_ob(mc, mr, fl):
    mc.back(fl)
    return

def rotate(mc, rotc, rotn):
    
    rot = 0
    deg = 90
    d_rate = 30
    k = 0 
    k = k + 0

    if rotc == rotn:
        return rotc
    
    elif rotc < rotn:
        rot = rotn - rotc
        for k in range(rot):
            mc.turn_right(deg, d_rate)
        k = 0
        rotc = rotn
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
    temp[0] = data['MLX1.To1']
    temp[1] = data['MLX1.To2']
    temp[2] = data['MLX1.To3']
    temp[3] = data['MLX1.To4']
    temp[4] = data['MLX1.To5']
    temp[5] = data['MLX1.To6']

    


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

        """ogconf1 = LogConfig(name='Temp1', period_in_ms=500) 
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
        logconf6.data_received_cb.add_callback(log_temp_callback)"""

        
        with MotionCommander(scf) as mc:    
            with Multiranger(scf) as mr:

                time.sleep(2)
                logconf.start()  
                """logconf1.start()
                logconf2.start()
                logconf3.start()
                logconf4.start()
                logconf5.start()
                logconf6.start()"""        
              
                size = len(spX) - 1
                point = 0

                rotc = 1                   
                rotn = 0                   
                j = 0
                y = 0

                while point != size:
                    
                    xp = spX[point]       
                    yp = spY[point]
                    xn = spX[point+1]
                    yn = spY[point+1]

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

                    point = point + 1

                logconf.stop()
                """logconf1.stop()
                logconf2.stop()
                logconf3.stop()
                logconf5.stop()
                logconf5.stop()
                logconf6.stop()"""
                pos_file.close()
                temp_file.close()
                my_plotter(ax, x_pos, y_pos, z_pos,  {'marker': 'x'})
                plt.show()
