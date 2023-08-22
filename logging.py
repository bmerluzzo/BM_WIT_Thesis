
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

URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E8')

position_estimate = [0, 0]
spX = [0, 0, 1, 1]
spY = [0, 1, 1, 0]
fl = 0.1


deck_attached_event = Event()


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

        logconf = LogConfig(name='Position', period_in_ms=1000)
        logconf.add_variable('stateEstimate.x', 'float')
        logconf.add_variable('stateEstimate.y', 'float')
        scf.cf.log.add_config(logconf)
        logconf.data_received_cb.add_callback(log_pos_callback)

        
        
        with MotionCommander(scf) as mc:
            
            logconf.start()
            for i in range(3):
                xp = spX[i]
                yp = spY[i]
                xn = spX[i+1]
                yn = spY[i+1]
                if xp == xn and yp < yn:
                    yd = yn - yp
                    ym = yd/fl
                    for j in range(ym):
                        mc.forward(fl)
                    time.sleep(2)
                elif xp == xn and yp > yn:
                    yd = yp - yn
                    ym = yd/fl
                    for k in range(ym):
                        mc.back(fl)
                    time.sleep(2)
                elif xp < xn and yp == yn:
                    xd = xn - xp
                    xm = xd/fl
                    for l in range(xm):
                        mc.right(fl)
                    time.sleep(2)
                elif xp > xn and yp == yn:
                    xd = xp - xn
                    xm = xd/fl
                    for m in range(xm):
                        mc.left(fl)
                    time.sleep(2)

            logconf.stop()