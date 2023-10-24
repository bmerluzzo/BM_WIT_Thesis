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

URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

position_estimate = [0, 0, 0]
t = 0
spX = [0, 0, 1, 1, 2, 2, 3, 3]
spY = [0, 3, 3, 1, 1, 3, 3, 0]
fl = 0.1


deck_attached_event = Event()

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
                            ob = 2
    return y


def move_forward(mc, mr, fl):
    mc.forward(fl)
    if is_close(mr.front):
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
    global position_estimate
    global t
    position_estimate[0] = data['stateEstimate.x']
    position_estimate[1] = data['stateEstimate.y']
    position_estimate[2] = data['stateEstimate.z']
    t = timestamp



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

        pos_file = open('pos_data.txt', "w")
        pos_file.close()
        pos_file = open('pos_data.txt', "a")

        scf.cf.param.add_update_callback(group='deck', name='bcFlow2', cb=param_deck_flow)

        logconf = LogConfig(name='Position', period_in_ms=500) 
        logconf.add_variable('stateEstimate.x', 'float')
        logconf.add_variable('stateEstimate.y', 'float')
        logconf.add_variable('stateEstimate.z', 'float')
        scf.cf.log.add_config(logconf)
        logconf.data_received_cb.add_callback(log_pos_callback)

        
        with MotionCommander(scf) as mc:    
            with Multiranger(scf) as mr:

                time.sleep(2)
                logconf.start()          
              
                size = len(spX) - 1            
                rotc = 1                   
                rotn = 0                   
                j = 0
                y = 0

                for p in range(size):
                    
                    xp = spX[p]       
                    yp = spY[p]
                    xn = spX[p+1]
                    yn = spY[p+1]

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

                logconf.stop()
                pos_file.close()
