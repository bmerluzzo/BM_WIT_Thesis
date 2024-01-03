#Swarm Code - Brandon Merluzzo
#***Changes needed*** - Modify callbacks and flight functions to differentiate between the data of each drone (temp and position)
import sys
import logging
import time
from threading import Event
import cflib.crtp

import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.log import LogConfig
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils.multiranger import Multiranger

position_estimate1 = [0, 0, 0]
position_estimate2 = [0, 0, 0]
t1 = 0
t2 = 0
deck_attached_event = Event()
pos_error = 0.075

temp11 = [0,0,0,0,0,0]
temp12 = [0,0,0,0,0,0]
temp13 = [0,0,0,0,0,0]
temp14 = [0,0,0,0,0,0]
temp15 = [0,0,0,0,0,0]
temp16 = [0,0,0,0,0,0]
temp_det1 = 0

temp21 = [0,0,0,0,0,0]
temp22 = [0,0,0,0,0,0]
temp23 = [0,0,0,0,0,0]
temp24 = [0,0,0,0,0,0]
temp25 = [0,0,0,0,0,0]
temp26 = [0,0,0,0,0,0]
temp_det2 = 0

grid_size = 1 
partition1 = 2
partition2 = 4
map_length_y = 2
map_length_x = 1
grid_num = 0
grid_order = [0]

fl = 0.1
velocity = 0.15

uri_list = {
    'radio://0/80/2M/E7E7E7E7E8',
    'radio://0/80/2M/E7E7E7E7E7',
    # Add more URIs if you want more copters in the swarm
}

uris = list(uri_list) 

seq_args = {
    uris[0]: [drone1],
    uris[1]: [drone2],
}

def temp_flag1():
    print("Hotspot Detected in Grid ", gn1)
    global temp_det1
    temp_det1 = 1

def temp_flag2():
    print("Hotspot Detected in Grid ", gn2)
    global temp_det2
    temp_det2 = 1

def sweep(mc, mr, fl, rotc, grid_size, partition):
    swX = [0]
    swY = [0]
    swY.append(1)
    swX.append(0)
    i = 0
    i = i + 1
    point = 0
    p_size = grid_size/partition
    pn_size = p_size

    print("Surveilling Grid ", gn, "\n")
    
    for i in range(partition):
        
        if i % 2 == 0:
            swY.append(grid_size)
            swY.append(0)
        else:
            swY.append(0)
            swY.append(grid_size)

        swX.append(pn_size)
        swX.append(pn_size)

        pn_size = pn_size + p_size

    swX.append(0)
    swY.append(0)

    size = len(swX) - 1

    time.sleep(3)


    if temp_det == 0:
        print("Level 2\n")
        while point != size:
                    
                        xp = swX[point]       
                        yp = swY[point]
                        xn = swX[point+1]
                        yn = swY[point+1]

                        pathing_level2(mc, fl, xn, xp, yn, yp, 1)

                        if temp_det == 1:
                            time.sleep(2)
                            pathing_level2(mc, fl, 0, xn, 0, yn, 0)
                            time.sleep(2)
                            mc.down(0.1)
                            return
                        point = point + 1

    elif temp_det == 1:
        print("Level 1\n")
        while point != size:
                    
                        xp = swX[point]       
                        yp = swY[point]
                        xn = swX[point+1]
                        yn = swY[point+1]

                        rotc = pathing_level1(mc, mr, fl, xn, xp, yn, yp, rotc, 1)

                        point = point + 1

    return

def pathing_level1(mc, mr, fl, xn, xp, yn, yp, rotc, mode):
                
    j = 0
    y = 0
    x = 0
    yd, xd = 0, 0
    ym, xm = 0, 0

    if mode == 1:
        yl = gn - 1
        ye = yn + yl
        xe = -abs(xn)
        if xn == 0:
            xe = 0
    elif mode == 0:
        ye = yn
        xe = xn

    if xp == xn and yp < yn:       
                        
        rotn = 1

        yd = yn - yp
        ym = yd/fl
        ym = int(ym)

        rotc = rotate(mc, rotc, rotn)
        error_correction_level1(mc, xe, yp, rotc)

        for j in range(ym):
            y = move_forward(mc, mr, fl)
            temp_mapping()
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
        error_correction_level1(mc, xe, yp, rotc)

        for j in range(ym):
            y = move_forward(mc, mr, fl)
            temp_mapping()
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
        error_correction_level1(mc, -abs(xp), ye, rotc)
                        
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
        error_correction_level1(mc, -abs(xp), ye, rotc)

        for j in range(xm):
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

    error_correction_level1(mc, xe, ye, rotc)

    return rotc

def pathing_level2(mc, fl, xn, xp, yn, yp, mode):

    j = 0
    y = 0
    x = 0
    error = 0
    yd, xd = 0, 0
    ym, xm = 0, 0
   
    if mode == 1:
        yl = gn - 1
        ye = yn + yl
        xe = -abs(xn)
        if xn == 0:
            xe = 0
    elif mode == 0:
        ye = yn
        xe = xn

    if xp == xn and yp < yn:       
                        
        yd = yn - yp
        ym = yd/fl
        ym = int(ym)

        for j in range(ym):
            mc.forward(fl)
            
        j = 0

    elif xp == xn and yp > yn:

        yd = yp - yn
        ym = yd/fl
        ym = int(ym)

        for j in range(ym):
            mc.back(fl)
            
        j = 0

    elif xp < xn and yp == yn:

        xd = xn - xp
        xm = xd/fl
        xm = int(xm)
                        
        for j in range(xm):
            mc.right(fl)
            
        j = 0

    elif xp > xn and yp == yn:

        xd = xp - xn
        xm = xd/fl
        xm = int(xm)

        for j in range(xm):
            mc.left(fl)
        
        j = 0

    elif xp < xn and yp < yn:

        yd = yn - yp
        ym = yd/fl
        ym = int(ym)

        for j in range(ym):
            mc.forward(fl)
        time.sleep(2)
        j = 0

        xd = xn - xp
        xm = xd/fl
        xm = int(xm)

        for j in range(xm):
            mc.right(fl)
        time.sleep(2)
        j = 0

    elif xp > xn and yp > yn:

        yd = yp - yn
        ym = yd/fl
        ym = int(ym)

        for j in range(ym):
            mc.back(fl)
        time.sleep(2)
        j = 0

        xd = xp - xn
        xm = xd/fl
        xm = int(xm)

        for j in range(xm):
            mc.left(fl)
        time.sleep(2)
        j = 0

    elif xp > xn and yp < yn:

        yd = yn - yp
        ym = yd/fl
        ym = int(ym)

        for j in range(ym):
           mc.forward(fl)
        time.sleep(2)
        j = 0

        xd = xp - xn
        xm = xd/fl
        xm = int(xm)

        for j in range(xm):
            mc.left(fl)
        time.sleep(2)
        j = 0

    elif xp < xn and yp > yn:

        yd = yp - yn
        ym = yd/fl
        ym = int(ym)

        for j in range(ym):
            mc.back(fl)
        time.sleep(2)
        j = 0

        xd = xn - xp
        xm = xd/fl
        xm = int(xm)

        for j in range(xm):
            mc.right(fl)
        time.sleep(2)
        j = 0

    x = position_estimate[1]
    y = position_estimate[0] 
    print(x, "\n") 
    print(y, "\n") 
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

        if is_close(mr.right) or is_close(mr.front):

            move_left_ob(mc,mr, fl*2)
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

    return y

def move_forward(mc, mr, fl):
    mc.forward(fl)
    if is_close(mr.front):
        mc.stop()
        y = obs_avoid(mc, mr, fl)
        return y
    #elif is_close(mr.top):
       # mc.stop()
       # time.sleep(20)
    else:
        return 0
    
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
            mc.turn_right(deg, d_rate)
        k = 0
        rotc = rotn
        return rotc
    
def move_front_ob(mc, mr, fl):
    mc.forward(fl)
    if is_close(mr.front):
        mc.stop()
        return 1
    #elif is_close(mr.top):
      #  mc.stop()
        #time.sleep(20)
    else:
        return
    
def move_right_ob(mc, mr, fl):
    mc.right(fl)
    if is_close(mr.right):
        mc.stop()
        return 1
    # is_close(mr.top):
     #   mc.stop()
      #  time.sleep(20)
    else:
        return
    
    
def move_left_ob(mc, mr, fl):
    mc.left(fl)
    if is_close(mr.left):
        mc.stop()
        return 1
    #elif is_close(mr.top):
      #  mc.stop()
        #time.sleep(20)
    else:
        return
    
def move_back_ob(mc, mr, fl):
    mc.back(fl)
    if is_close(mr.top):
        mc.stop()
        return 2
    else:
        return

def is_close(range):
    MIN_DISTANCE = 0.3

    if range is None:
        return False
    else:
        return range < MIN_DISTANCE
    
def light_check(scf):
    activate_led_bit_mask(scf)
    time.sleep(2)
    deactivate_led_bit_mask(scf)

def activate_led_bit_mask(scf):
    scf.cf.param.set_value('led.bitmask', 255)

def deactivate_led_bit_mask(scf):
    scf.cf.param.set_value('led.bitmask', 0)

def map_generation(grid_size, map_length_y, map_length_x):
    i = 0
    j = 0
                
    pointX = 0
    pointY = grid_size
    grid_num_y = map_length_y/grid_size
    grid_num_x = map_length_x/grid_size
    grid_num_y = int(grid_num_y)
    grid_num_x = int(grid_num_x)
    spY = [0] 
    spX = [0] 


    for i in range(grid_num_x):
                    
        for j in range(grid_num_y):
            spY.append(pointY)
            spX.append(pointX)
            pointY = pointY + grid_size
        pointX = pointX + grid_size
        pointY = 0    

    return spX, spY 

def run_sequence(scf, path):

    if scf.cf.link_uri == 'radio://0/80/2M/E7E7E7E7E8':

        spX, spY = map_generation(grid_size, map_length_y, map_length_x)

        grid_num = map_length_x * map_length_y

        i = 0
        for i in range(grid_num):
                    grid_order.append(i + 1)

        global pos_file1
        pos_file1 = open(file, "w")
        pos_file1.close()
        pos_file1 = open(file, "a")

        scf.cf.param.add_update_callback(name= path[3], cb=param_deck_flow)

        logconf1 = LogConfig(name='Position', period_in_ms=500) 
        logconf1.add_variable('stateEstimate.x', 'float')
        logconf1.add_variable('stateEstimate.y', 'float')
        logconf1.add_variable('stateEstimate.z', 'float')
        scf.cf.log.add_config(logconf1)
        logconf1.data_received_cb.add_callback(log_pos_callback1)
        logconf1.start()

        size = len(spX) - 1
        point = 0
        rotc = 1
        rotc = int(rotc)     
        global gn1  
        global hold1

        with MotionCommander(scf, default_height = 0.4) as mc:    
            with Multiranger(scf) as mr:

                time.sleep(2)  
                    
                while point != size:
                    
                    xp = spX[point]       
                    yp = spY[point]
                    xn = spX[point+1]
                    yn = spY[point+1] 
                    gn1 = grid_order[point + 1]

                    sweep(mc, mr, fl, rotc, grid_size, partition1)

                    if temp_det1 == 1:
                        sweep(mc, mr, fl, rotc, grid_size, partition2)
                        time.sleep(2)
                        mc.up(0.1)
                        time.sleep(2)
                        mc.turn_right(90, 30)

                    pathing_level2(mc, fl, xn, xp, yn, yp, 0)
                    
                    if temp_det1 == 1:
                        temp_det1 = 0
                        hold1 = 0

                    point = point + 1

    elif scf.cf.link_uri == 'radio://0/80/2M/E7E7E7E7E7':

        spX, spY = map_generation(grid_size, map_length_y, map_length_x)
        for i in range(len(spX)):
            spX[i] = spX[i] + 2

        grid_num = map_length_x * map_length_y

        i = 0
        for i in range(grid_num):
                    grid_order.append(i + grid_size + 1)

        global pos_file2
        pos_file2 = open(file, "w")
        pos_file2.close()
        pos_file2 = open(file, "a")

        scf.cf.param.add_update_callback(name= path[3], cb=param_deck_flow)

        logconf2 = LogConfig(name='Position', period_in_ms=500) 
        logconf2.add_variable('stateEstimate.x', 'float')
        logconf2.add_variable('stateEstimate.y', 'float')
        logconf2.add_variable('stateEstimate.z', 'float')
        scf.cf.log.add_config(logconf2)
        logconf2.data_received_cb.add_callback(log_pos_callback2)
        logconf2.start()

        size = len(spX) - 1
        point = 0
        rotc = 1
        rotc = int(rotc)     
        global gn2  
        global hold2

        with MotionCommander(scf, default_height = 0.4) as mc:    
            with Multiranger(scf) as mr:

                time.sleep(2)  
                    
                while point != size:
                    
                    xp = spX[point]       
                    yp = spY[point]
                    xn = spX[point+1]
                    yn = spY[point+1] 
                    gn2 = grid_order[point + 1]

                    sweep(mc, mr, fl, rotc, grid_size, partition1)

                    if temp_det2 == 1:
                        sweep(mc, mr, fl, rotc, grid_size, partition2)
                        time.sleep(2)
                        mc.up(0.1)
                        time.sleep(2)
                        mc.turn_right(90, 30)

                    pathing_level2(mc, fl, xn, xp, yn, yp, 0)
                    
                    if temp_det2 == 1:
                        temp_det2 = 0
                        hold2 = 0

                    point = point + 1
        

def log_pos_callback1(timestamp, data, logconf):
    pos_file1.write("Y:{},X:{},Z:{}\n".format(data['stateEstimate.x'], data['stateEstimate.y'], data['stateEstimate.z']))
    global position_estimate
    global t
    position_estimate1[0] = data['stateEstimate.x']
    position_estimate1[1] = data['stateEstimate.y']
    position_estimate1[2] = data['stateEstimate.z']
    t1 = timestamp

def log_pos_callback2(timestamp, data, logconf):
    pos_file2.write("Y:{},X:{},Z:{}\n".format(data['stateEstimate.x'], data['stateEstimate.y'], data['stateEstimate.z']))
    global position_estimate
    global t
    position_estimate2[0] = data['stateEstimate.x']
    position_estimate2[1] = data['stateEstimate.y']
    position_estimate2[2] = data['stateEstimate.z']
    t2 = timestamp

def log_temp1_callback(timestamp, data, logconf):
    temp_file.write("{}\n".format(data))
    thres = 100
    global hold1

    if logconf.name == 'Temp1':
        temp11[0] = data['MLX1.To1']
        temp11[1] = data['MLX1.To2']
        temp11[2] = data['MLX1.To3']
        temp11[3] = data['MLX1.To4']
        temp11[4] = data['MLX1.To5']
        temp11[5] = data['MLX1.To6']
        if (temp11[0] or temp11[1] or temp11[2] or temp11[3] or temp11[4] or temp11[5]) > thres and hold1 == 0:
            hold1 = 1
            temp_flag1()

    elif logconf.name == 'Temp2':
        temp12[0] = data['MLX2.To1']
        temp12[1] = data['MLX2.To2']
        temp12[2] = data['MLX2.To3']
        temp12[3] = data['MLX2.To4']
        temp12[4] = data['MLX2.To5']
        temp12[5] = data['MLX2.To6']
        if (temp12[0] or temp12[1] or temp12[2] or temp12[3] or temp12[4] or temp12[5]) > thres and hold1 == 0:
            hold1 = 1
            temp_flag1()

    
    elif logconf.name == 'Temp3':
        temp13[0] = data['MLX3.To1']
        temp13[1] = data['MLX3.To2']
        temp13[2] = data['MLX3.To3']
        temp13[3] = data['MLX3.To4']
        temp13[4] = data['MLX3.To5']
        temp13[5] = data['MLX3.To6']
        if (temp13[0] or temp13[1] or temp13[2] or temp13[3] or temp13[4] or temp13[5]) > thres and hold1 == 0:
            hold1 = 1
            temp_flag1()

    elif logconf.name == 'Temp4':
        temp14[0] = data['MLX4.To1']
        temp14[1] = data['MLX4.To2']
        temp14[2] = data['MLX4.To3']
        temp14[3] = data['MLX4.To4']
        temp14[4] = data['MLX4.To5']
        temp14[5] = data['MLX4.To6']
        if (temp14[0] or temp14[1] or temp14[2] or temp14[3] or temp14[4] or temp14[5]) > thres and hold1 == 0:
            hold1 = 1
            temp_flag1()

    elif logconf.name == 'Temp5':
        temp15[0] = data['MLX5.To1']
        temp15[1] = data['MLX5.To2']
        temp15[2] = data['MLX5.To3']
        temp15[3] = data['MLX5.To4']
        temp15[4] = data['MLX5.To5']
        temp15[5] = data['MLX5.To6']
        if (temp15[0] or temp15[1] or temp15[2] or temp15[3] or temp15[4] or temp15[5]) > thres and hold1 == 0:
            hold1 = 1
            temp_flag1()

    elif logconf.name == 'Temp6':
        temp16[0] = data['MLX6.To1']
        temp16[1] = data['MLX6.To2']
        temp16[2] = data['MLX6.To3']
        temp16[3] = data['MLX6.To4']
        temp16[4] = data['MLX6.To5']
        temp16[5] = data['MLX6.To6']
        if (temp16[0] or temp16[1] or temp16[2] or temp16[3] or temp16[4] or temp16[5]) > thres and hold1 == 0:
            hold1 = 1
            temp_flag1()

def log_temp2_callback(timestamp, data, logconf):
    temp_file.write("{}\n".format(data))
    thres = 100
    global hold2

    if logconf.name == 'Temp1':
        temp21[0] = data['MLX1.To1']
        temp21[1] = data['MLX1.To2']
        temp21[2] = data['MLX1.To3']
        temp21[3] = data['MLX1.To4']
        temp21[4] = data['MLX1.To5']
        temp21[5] = data['MLX1.To6']
        if (temp21[0] or temp21[1] or temp21[2] or temp21[3] or temp21[4] or temp21[5]) > thres and hold2 == 0:
            hold2 = 1
            temp_flag2()

    elif logconf.name == 'Temp2':
        temp22[0] = data['MLX2.To1']
        temp22[1] = data['MLX2.To2']
        temp22[2] = data['MLX2.To3']
        temp22[3] = data['MLX2.To4']
        temp22[4] = data['MLX2.To5']
        temp22[5] = data['MLX2.To6']
        if (temp22[0] or temp22[1] or temp22[2] or temp22[3] or temp22[4] or temp22[5]) > thres and hold2 == 0:
            hold2 = 1
            temp_flag2()

    
    elif logconf.name == 'Temp3':
        temp23[0] = data['MLX3.To1']
        temp23[1] = data['MLX3.To2']
        temp23[2] = data['MLX3.To3']
        temp23[3] = data['MLX3.To4']
        temp23[4] = data['MLX3.To5']
        temp23[5] = data['MLX3.To6']
        if (temp23[0] or temp23[1] or temp23[2] or temp23[3] or temp23[4] or temp23[5]) > thres and hold2 == 0:
            hold2 = 1
            temp_flag2()

    elif logconf.name == 'Temp4':
        temp24[0] = data['MLX4.To1']
        temp24[1] = data['MLX4.To2']
        temp24[2] = data['MLX4.To3']
        temp24[3] = data['MLX4.To4']
        temp24[4] = data['MLX4.To5']
        temp24[5] = data['MLX4.To6']
        if (temp24[0] or temp24[1] or temp24[2] or temp24[3] or temp24[4] or temp24[5]) > thres and hold2 == 0:
            hold2 = 1
            temp_flag2()

    elif logconf.name == 'Temp5':
        temp25[0] = data['MLX5.To1']
        temp25[1] = data['MLX5.To2']
        temp25[2] = data['MLX5.To3']
        temp25[3] = data['MLX5.To4']
        temp25[4] = data['MLX5.To5']
        temp25[5] = data['MLX5.To6']
        if (temp25[0] or temp25[1] or temp25[2] or temp25[3] or temp25[4] or temp25[5]) > thres and hold2 == 0:
            hold2 = 1
            temp_flag2()

    elif logconf.name == 'Temp6':
        temp26[0] = data['MLX6.To1']
        temp26[1] = data['MLX6.To2']
        temp26[2] = data['MLX6.To3']
        temp26[3] = data['MLX6.To4']
        temp26[4] = data['MLX6.To5']
        temp26[5] = data['MLX6.To6']
        if (temp26[0] or temp26[1] or temp26[2] or temp26[3] or temp26[4] or temp26[5]) > thres and hold2 == 0:
            hold2 = 1
            temp_flag2()


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
    factory = CachedCfFactory(rw_cache='./cache')
    with Swarm(uris, factory=factory) as swarm:
        swarm.parallel_safe(light_check)
        swarm.reset_estimators()

        time.sleep(2)

        #swarm.sequential(run_sequence, args_dict=seq_args)
        swarm.parallel(run_sequence)