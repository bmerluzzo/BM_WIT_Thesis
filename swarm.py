#Swarm Code - Brandon Merluzzo
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
t1, t2 = 0
deck_attached_event = Event()

uri_list = {
    'radio://0/80/2M/E7E7E7E7E8',
    'radio://0/80/2M/E7E7E7E7E7',
    # Add more URIs if you want more copters in the swarm
}

uris = list(uri_list) 

drone1 = [
    (0, 0, 1), #X coordinate
    (0, 1, 1), #Y coordinate
    'drone1_pos.txt',
    'drone1',
]

drone2 = [
    (1, 2),
    (0, 0),
    'drone2_pos.txt',
    'drone2',
]

seq_args = {
    uris[0]: [drone1],
    uris[1]: [drone2],
}

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


def run_sequence(scf, path):
    spX = path[0]
    spY = path[1]
    file = path[2]

    if scf.cf.link_uri == 'radio://0/80/2M/E7E7E7E7E8':
        global pos_file1
        pos_file1 = open(file, "w")
        pos_file1.close()
        pos_file1 = open(file, "a")

        scf.cf.param.add_update_callback(name= path[3], cb=param_deck_flow)

        logconf = LogConfig(name='Position', period_in_ms=500) 
        logconf.add_variable('stateEstimate.x', 'float')
        logconf.add_variable('stateEstimate.y', 'float')
        logconf.add_variable('stateEstimate.z', 'float')
        scf.cf.log.add_config(logconf)
        logconf.data_received_cb.add_callback(log_pos_callback1)
    elif scf.cf.link_uri == 'radio://0/80/2M/E7E7E7E7E8':
        global pos_file2
        pos_file2 = open(file, "w")
        pos_file2.close()
        pos_file2 = open(file, "a")

        scf.cf.param.add_update_callback( name= path[3], cb=param_deck_flow)

        logconf = LogConfig(name='Position', period_in_ms=500) 
        logconf.add_variable('stateEstimate.x', 'float')
        logconf.add_variable('stateEstimate.y', 'float')
        logconf.add_variable('stateEstimate.z', 'float')
        scf.cf.log.add_config(logconf)
        logconf.data_received_cb.add_callback(log_pos_callback2)
        

    with MotionCommander(scf) as mc:
        with Multiranger(scf) as mr:
                time.sleep(2)
                        
                fl = 0.1
                size = len(spX) - 1            
                rotc = 1                   
                rotn = 0                   
                j = 0
                y = 0

                logconf.start()

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
    if scf.cf.link_uri == 'radio://0/80/2M/E7E7E7E7E8':
        pos_file1.close()
    elif scf.cf.link_uri == 'radio://0/80/2M/E7E7E7E7E7':
        pos_file2.close()

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

        time.sleep(5)

        #swarm.sequential(run_sequence, args_dict=seq_args)
        swarm.parallel_safe(run_sequence, args_dict=seq_args)