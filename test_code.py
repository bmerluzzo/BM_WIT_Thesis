#Test code for Crazyflie control with Multi-ranger deck and Flow deck - Github

import logging
import sys
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper
from cflib.utils.multiranger import Multiranger

URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E8')

if len(sys.argv) > 1:
    URI = sys.argv[1]

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)


def is_close(range):
    MIN_DISTANCE = 0.2  # m

    if range is None:
        return False
    else:
        return range < MIN_DISTANCE


if __name__ == '__main__':
    x = 20
    y = 0 
    fl = 0.2
    j = 0
    # Initialize the low-level drivers
    cflib.crtp.init_drivers()

    cf = Crazyflie(rw_cache='./cache')
    with SyncCrazyflie(URI, cf=cf) as scf:
        with MotionCommander(scf) as mc:
            with Multiranger(scf) as mr:
                time.sleep(2)
                for i in range(x):
                    mc.forward(fl)
                    if is_close(mr.front):
                        mc.stop()
                        while j == 0:
                            if is_close(mr.front):
                                mc.left(fl)
                                y = y + 1
                            else:
                                mc.forward(fl)
                                i = i + 1
                                if is_close(mr.right):
                                    mc.forward(fl)
                                    i = i + 1
                                else:
                                    for k in range(y):
                                        mc.right(fl)
                                        j = 1
                

                    

    
