# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2017 Bitcraze AB
#
#  Crazyflie Nano Quadcopter Client
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
This script shows the basic use of the MotionCommander class.

Simple example that connects to the crazyflie at `URI` and runs a
sequence. This script requires some kind of location system, it has been
tested with (and designed for) the flow deck.

The MotionCommander uses velocity setpoints.

Change the URI variable to your Crazyflie configuration.
"""
import logging
import sys
import time
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
deck_attached_event = Event()

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

def param_deck_flow(_, value_str):
    value = int(value_str)
    print(value)
    if value:
        deck_attached_event.set()
        print('Deck is attached!')
    else:
        print('Deck is NOT attached!')

def log_pos_callback(timestamp, data, logconf):
    print(data)
    global position_estimate
    position_estimate[0] = data['stateEstimate.x']
    position_estimate[1] = data['stateEstimate.y']

def is_close(range):
    MIN_DISTANCE = 0.3

    if range is None:
        return False
    else:
        return range < MIN_DISTANCE


if __name__ == '__main__':
    # Initialize the low-level drivers
    cflib.crtp.init_drivers()
    x = 60
    y = 0 
    fl = 0.05
    j = 0
    i = 0
    s = 0

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
                for i in range(x):
                    mc.forward(fl)
                    if is_close(mr.front):
                        j = 0
                        s = 0
                        mc.stop()
                        time.sleep(2)

                        if is_close(mr.right):
                            while j == 0:
                                if is_close(mr.front):
                                    mc.left(fl)
                                    y = y + 1
                                else:
                                    time.sleep(1)
                                    mc.forward(fl*6)
                                    i = i + 6
                                    while s == 0:
                                        if is_close(mr.right):
                                            mc.forward(fl)
                                            i = i + 1
                                        else:
                                            time.sleep(1)
                                            for k in range(y):
                                                mc.right(fl)
                                            time.sleep(2)
                                            y = 0
                                            k = 0
                                            s = 1
                                            j = 1

                        elif is_close(mr.left):
                            while j == 0:
                                if is_close(mr.front):
                                    mc.right(fl)
                                    y = y + 1
                                else:
                                    time.sleep(1)
                                    mc.forward(fl*7)
                                    i = i + 7
                                    while s == 0:
                                        if is_close(mr.left):
                                            mc.forward(fl)
                                            i = i + 1
                                        else:
                                            time.sleep(1)
                                            for k in range(y):
                                                mc.left(fl)
                                            time.sleep(1)
                                            y = 0
                                            k = 0
                                            s = 1
                                            j = 1

                        else:
                            while j == 0:
                                if is_close(mr.front):
                                    mc.left(fl*2)
                                    y = y + 2
                                else:
                                    time.sleep(1)
                                    mc.forward(fl*6)
                                    i = i + 6
                                    while s == 0:
                                        if is_close(mr.right):
                                            mc.forward(fl)
                                            i = i + 1
                                        else:
                                            time.sleep(1)
                                            for k in range(y):
                                                mc.right(fl)
                                            time.sleep(2)
                                            y = 0
                                            k = 0
                                            s = 1
                                            j = 1
                       

                        """elif is_close(mr.front) and is_close(mr.left) and is_close(mr.right):
                            while j == 0:
                                if is_close(mr.left) and is_close(mr.right):
                                    mc.back(fl)
                                    i = i - 1
                                else:
                                    time.sleep(2)
                                    if y == 0:
                                        mc.left(fl*4)
                                        y = y + 4
                                        while is_close(mr.front):
                                            mc.left(fl)
                                            y = y + 1
                                    else: 
                                        time.sleep(2)
                                        mc.forward(fl*4)
                                        i = i + 4
                                        while is_close(mr.right):
                                            mc.forward(fl)
                                            i = i + 1
                                        time.sleep(2)
                                        for k in range(y):
                                            mc.right(fl)
                                        y = 0
                                        k = 0
                                        j = 1"""
                logconf.stop()    
                time.sleep(2)
