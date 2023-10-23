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

URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E9')

def log_temp_callback(timestamp, data, logconf):
    print(data)
    
    

if __name__ == '__main__':
    cflib.crtp.init_drivers()

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:

        logconf = LogConfig(name='Temp1', period_in_ms=500) 
        logconf.add_variable('MLX1.To1', 'float')
        logconf.add_variable('MLX1.To2', 'float')
        logconf.add_variable('MLX1.To3', 'float')
        logconf.add_variable('MLX1.To4', 'float')
        logconf.add_variable('MLX1.To5', 'float')
        logconf.add_variable('MLX1.To6', 'float')
        scf.cf.log.add_config(logconf)
        logconf.data_received_cb.add_callback(log_temp_callback)

        logconf2 = LogConfig(name='Temp2', period_in_ms=500) 
        logconf2.add_variable('MLX2.To1', 'float')
        logconf2.add_variable('MLX2.To2', 'float')
        logconf2.add_variable('MLX2.To3', 'float')
        logconf2.add_variable('MLX2.To4', 'float')
        logconf2.add_variable('MLX2.To5', 'float')
        logconf2.add_variable('MLX2.To6', 'float')
        scf.cf.log.add_config(logconf2)
        logconf2.data_received_cb.add_callback(log_temp_callback)

        logconf.start()
        logconf2.start()
        time.sleep(20)
        logconf.stop()
        logconf2.stop()