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

URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E8')

position_estimate = [0, 0]
spX = [0]
spY = [0]
fl = 0.1


deck_attached_event = Event()

def obs_avoid(mc, mr, fl):
    return

def move_forward(mc, mr, fl):
    mc.forward(fl)
    if is_close(mr.front):
        obs_avoid(mc, mr, fl)
    elif is_close(mr.top):
        mc.stop()
    else:
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
            mc.turn_right(deg, d_rate)
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
    print(data)
    global position_estimate
    position_estimate[0] = data['stateEstimate.x']
    position_estimate[1] = data['stateEstimate.y']


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

        scf.cf.param.add_update_callback(group='deck', name='bcFlow2', cb=param_deck_flow)

        logconf = LogConfig(name='Position', period_in_ms=500)
        logconf.add_variable('stateEstimate.x', 'float')
        logconf.add_variable('stateEstimate.y', 'float')
        scf.cf.log.add_config(logconf)
        logconf.data_received_cb.add_callback(log_pos_callback)

        
        with MotionCommander(scf) as mc:
            with Multiranger(scf) as mr:
                time.sleep(2)
                logconf.start()
                size = len(spX)
                rotc = 1
                rotn = 0
                j = 0
                for i in range(size):
                    
                    xp = spX[i]
                    yp = spY[i]
                    xn = spX[i+1]
                    yn = spY[i+1]

                    yd, xd = 0, 0
                    ym, xm = 0, 0

                    if xp == xn and yp < yn:
                        
                        rotn = 1

                        yd = yn - yp
                        ym = yd/fl
                        ym = int(ym)

                        rotc = rotate(mc, rotc, rotn)

                        for j in range(ym):
                            move_forward(mc, fl)
                        time.sleep(2)
                        j = 0

                    elif xp == xn and yp > yn:

                        rotn = 3

                        yd = yp - yn
                        ym = yd/fl
                        ym = int(ym)

                        rotc = rotate(mc, rotc, rotn)

                        for j in range(ym):
                            move_forward(mc, fl)
                        time.sleep(2)
                        j = 0

                    elif xp < xn and yp == yn:

                        rotn = 2

                        xd = xn - xp
                        xm = xd/fl
                        xm = int(xm)

                        rotc = rotate(mc, rotc, rotn)
                        
                        for j in range(xm):
                            move_forward(mc, fl)
                        time.sleep(2)
                        j = 0

                    elif xp > xn and yp == yn:

                        rotn = 4

                        xd = xp - xn
                        xm = xd/fl
                        xm = int(xm)

                        rotc = rotate(mc, rotc, rotn)

                        for m in range(xm):
                            move_forward(mc, fl)
                        time.sleep(2)
                        j = 0

                    elif xp < xn and yp < yn:

                        rotn = 1

                        yd = yn - yp
                        ym = yd/fl
                        ym = int(ym)

                        rotc = rotate(mc, rotc, rotn)

                        for j in range(ym):
                            move_forward(mc, fl)
                        time.sleep(2)
                        j = 0

                        rotn = 2

                        xd = xn - xp
                        xm = xd/fl
                        xm = int(xm)

                        rotc = rotate(mc, rotc, rotn)

                        for j in range(xm):
                            move_forward(mc, fl)
                        time.sleep(2)
                        j = 0

                    elif xp > xn and yp > yn:

                        rotn = 3

                        yd = yp - yn
                        ym = yd/fl
                        ym = int(ym)

                        rotc = rotate(mc, rotc, rotn)

                        for j in range(ym):
                            move_forward(mc, fl)
                        time.sleep(2)
                        j = 0

                        rotn = 4

                        xd = xp - xn
                        xm = xd/fl
                        xm = int(xm)

                        rotc = rotate(mc, rotc, rotn)

                        for j in range(xm):
                            move_forward(mc, fl)
                        time.sleep(2)
                        j = 0

                    elif xp > xn and yp < yn:

                        rotn = 1

                        yd = yn - yp
                        ym = yd/fl
                        ym = int(ym)

                        rotc = rotate(mc, rotc, rotn)

                        for j in range(ym):
                            move_forward(mc,fl)
                        time.sleep(2)
                        j = 0

                        rotn = 4

                        xd = xp - xn
                        xm = xd/fl
                        xm = int(xm)

                        rotc = rotate(mc, rotc, rotn)

                        for j in range(xm):
                            move_forward(mc,fl)
                        time.sleep(2)
                        j = 0

                    elif xp < xn and yp > yn:

                        rotn = 3

                        yd = yp - yn
                        ym = yd/fl
                        ym = int(ym)

                        rotc = rotate(mc, rotc, rotn)

                        for j in range(ym):
                            move_forward(mc,fl)
                        time.sleep(2)
                        j = 0

                        rotn = 2

                        xd = xn - xp
                        xm = xd/fl
                        xm = int(xm)

                        rotc = rotate(mc, rotc, rotn)

                        for j in range(xm):
                            move_forward(mc,fl)
                        time.sleep(2)
                        j = 0

                logconf.stop()
