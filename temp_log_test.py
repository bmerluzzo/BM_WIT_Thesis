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

temp1 = [0,0,0,0,0,0]
temp2 = [0,0,0,0,0,0]
temp3 = [0,0,0,0,0,0]
temp4 = [0,0,0,0,0,0]
temp5 = [0,0,0,0,0,0]
temp6 = [0,0,0,0,0,0]
count = 0

def log_temp_callback(timestamp, data, logconf):
    temp_file.write("{}\n".format(data))
    global count

    if logconf.name == 'Temp1':
        temp1[0] = data['MLX1.To1']
        temp1[1] = data['MLX1.To2']
        temp1[2] = data['MLX1.To3']
        temp1[3] = data['MLX1.To4']
        temp1[4] = data['MLX1.To5']
        temp1[5] = data['MLX1.To6']
        print(temp1[0], '|',temp1[1], '|',temp1[2], '|',temp1[3], '|',temp1[4], '|',temp1[5], '\n')
        count = count + 1

    elif logconf.name == 'Temp2':
        temp2[0] = data['MLX2.To1']
        temp2[1] = data['MLX2.To2']
        temp2[2] = data['MLX2.To3']
        temp2[3] = data['MLX2.To4']
        temp2[4] = data['MLX2.To5']
        temp2[5] = data['MLX2.To6']
        print(temp2[0], '|',temp2[1], '|',temp2[2], '|',temp2[3], '|',temp2[4], '|',temp2[5], '\n')
        count = count + 1

    
    elif logconf.name == 'Temp3':
        temp3[0] = data['MLX3.To1']
        temp3[1] = data['MLX3.To2']
        temp3[2] = data['MLX3.To3']
        temp3[3] = data['MLX3.To4']
        temp3[4] = data['MLX3.To5']
        temp3[5] = data['MLX3.To6']
        print(temp3[0], '|',temp3[1], '|',temp3[2], '|',temp3[3], '|',temp3[4], '|',temp3[5], '\n')
        count = count + 1


    elif logconf.name == 'Temp4':
        temp4[0] = data['MLX4.To1']
        temp4[1] = data['MLX4.To2']
        temp4[2] = data['MLX4.To3']
        temp4[3] = data['MLX4.To4']
        temp4[4] = data['MLX4.To5']
        temp4[5] = data['MLX4.To6']
        print(temp4[0], '|',temp4[1], '|',temp4[2], '|',temp4[3], '|',temp4[4], '|',temp4[5], '\n')
        count = count + 1
    

    elif logconf.name == 'Temp5':
        temp5[0] = data['MLX5.To1']
        temp5[1] = data['MLX5.To2']
        temp5[2] = data['MLX5.To3']
        temp5[3] = data['MLX5.To4']
        temp5[4] = data['MLX5.To5']
        temp5[5] = data['MLX5.To6']
        print(temp5[0], '|',temp5[1], '|',temp5[2], '|',temp5[3], '|',temp5[4], '|',temp5[5], '\n')
        count = count + 1
       

    elif logconf.name == 'Temp6':
        temp6[0] = data['MLX6.To1']
        temp6[1] = data['MLX6.To2']
        temp6[2] = data['MLX6.To3']
        temp6[3] = data['MLX6.To4']
        temp6[4] = data['MLX6.To5']
        temp6[5] = data['MLX6.To6']
        print(temp6[0], '|',temp6[1], '|',temp6[2], '|',temp6[3], '|',temp6[4], '|',temp6[5], '\n')
        count = count + 1
    
    if count == 6:
        print("\n")
        count = 0
    

if __name__ == '__main__':
    cflib.crtp.init_drivers()

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:

        temp_file = open('temp_data.txt', "w")
        temp_file.close()
        temp_file = open('temp_data.txt', "a")

        logconf = LogConfig(name='Temp1', period_in_ms=1000) 
        logconf.add_variable('MLX1.To1', 'float')
        logconf.add_variable('MLX1.To2', 'float')
        logconf.add_variable('MLX1.To3', 'float')
        logconf.add_variable('MLX1.To4', 'float')
        logconf.add_variable('MLX1.To5', 'float')
        logconf.add_variable('MLX1.To6', 'float')
        scf.cf.log.add_config(logconf)
        logconf.data_received_cb.add_callback(log_temp_callback)

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

        #with MotionCommander(scf, default_height = 0.4) as mc: 

        time.sleep(10)
            
        logconf.start()
        logconf2.start()
        logconf3.start()
        logconf4.start()
        logconf5.start()
        logconf6.start()

        time.sleep(30)
        #mc.forward(1)
        time.sleep(2)

        logconf.stop()
        logconf2.stop()
        logconf3.stop()
        logconf5.stop()
        logconf5.stop()
        logconf6.stop()

        temp_file.close()