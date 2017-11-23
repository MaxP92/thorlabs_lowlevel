# -*- coding: utf-8 -*-
"""
Created on Aug 15 16:35:13 2017

@author: Maxime PINSARD
"""
'''
control_thorlabs_lowlevel

for thorlabs instruments to get more functions than APT.dll
'''

## parameters

import array, os, time
import thorlabs_lowlvl_list
os.chdir('~your working dir')
    
port = 'COM4' # check what is your COM port

use_serial_not_ftdi = 1 # ftdi

## open connection

if use_serial_not_ftdi: # use Serial
    
    from serial.tools.list_ports import comports
    import serial
    
    # serial_ports = [(x[0], x[1], dict(y.split('=', 1) for y in x[2].split(' ') if '=' in y)) for x in comports()] # long version
    serial_ports = [x[0] for x in comports()]
    
    port_motor=''.join(str(x) for x in serial_ports if x == port)
    
    motor_stageXY = serial.Serial(port_motor,baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE, timeout=2, rtscts=True)

else: # use ftdi

    '''
    WARNING : this option of connection allows you to purge the buffers and reset your device,
    but it lacks a time out in reading
    You have to make your own time out like :
    bb = ''
    start_time = time.time()
    while (not bool(bb) and (time.time() - start_time) < timeout_sec):
        bb = motor_stageXY.read(90) 
    
    You also have to use "write_data" and "read_data" instead of 'write' and 'read'
    
    It's better also to use time.sleep(0.1) between commands
    '''

    timeout_sec = 2
    from pyftdi.ftdi import Ftdi

    # PID seems to be FAF0 in device manager
    Ftdi.add_custom_product(0x403, 0xfaf0)
    try:
        motor_stageXY = Ftdi.create_from_url('ftdi://0x403:0xfaf0/1')
        motor_stageXY.open_from_url(url = 'ftdi://0x403:0xfaf0/1')
        
        motor_stageXY.set_baudrate(115200)
        motor_stageXY.set_line_property(8, 1, 'N', break_=0) # 'N' = parity_none
        time.sleep(50e-3) # pre-purge
        motor_stageXY.purge_buffers() # purge RX and TX buffers
        time.sleep(50e-3) # post-purge
        motor_stageXY._reset_device() # private module, unlock it to public if no access
        motor_stageXY.set_flowctrl('hw') # 'hw' means RTS/CTS UART lines
    
        # f1.set_rts(state) # not sure for this one, the doc does not specify the 'state'
    
    except Exception as e:
        if str(e) == "No USB device matches URL":
            print("\n Motor XY not recognized ! \n")
        else:
            raise # do error
    
## init

# no flash programming is maybe only for USB interface, because it makes the motor to be silent in virtual COM
# motor_stageXY.write_data(thorlabs_lowlvl_list.msg_ID_noflashprog1)
# time.sleep(0.1)
# motor_stageXY.write_data(thorlabs_lowlvl_list.msg_ID_noflashprog2) # can be simultaneous
# time.sleep(0.1)

motor_stageXY.write(thorlabs_lowlvl_list.command_req_info)
# bb = ''
# while (not bool(bb) and (time.time() - start_time) < timeout_sec):
bb = motor_stageXY.read(90) 
print(bb[10:16], bb[24:67]) 
motor_stageXY.write(thorlabs_lowlvl_list.command_req_info1)
# bb = ''
# while (not bool(bb) and (time.time() - start_time) < timeout_sec):
bb = motor_stageXY.read(90) 
print(bb[10:16], bb[24:52]) 
# motor_stageXY.write(thorlabs_lowlvl_list.command_req_info2)
# bb = ''
# while (not bool(bb) and (time.time() - start_time) < timeout_sec):
bb = motor_stageXY.read(90) 
print(bb[10:16], bb[24:52])    


# MSG update msg # I don't want a continuous set of message received !
# MGMSG_MOT_REQ_PMDSTAGEAXISPARAMS
# MGMSG_MOT_REQ_VELPARAMS
# MGMSG_MOT_REQ_JOGPARAMS
# MGMSG_MOT_REQ_LIMSWITCHPARAMS
# MGMSG_MOT_REQ_GENMOVEPARAMS
# MGMSG_MOT_REQ_HOMEPARAMS
# MGMSG_MOT_REQ_MOVERELPARAMS
# MGMSG_MOT_REQ_MOVEABSPARAMS
# MGMSG_MOT_REQ_PMDCURRENTLOOPPARAMS
# move piezo ??
# MGMSG_MOT_REQ_PMDMOTOROUTPUTPARAMS 0x04DB
# MGMSG_MOT_REQ_PMDTRACKSETTLEPARAMS
# MGMSG_MOT_REQ_PMDPROFILEMODEPARAMS
# MGMSG_MOT_REQ_PMDJOYSTICKPARAMS
# MGMSG_MOT_REQ_PMDSETTLEDCURRENTLOOPPARAMS
# MGMSG_MOT_REQ_TRIGGER
# for both channels
# read parameters

blocking = True

## Turn on channels

# enable CHs
# motor_stageXY.write(command_ch2)
# command_ch2=b"\x10\x02\x01\x01\xA2\x01"
if thorlabs_lowlvl_list.get_chstate_bycommand_meth(0, motor_stageXY) != 1: # can be 2
    motor_stageXY.write(thorlabs_lowlvl_list.command_En0)
if thorlabs_lowlvl_list.get_chstate_bycommand_meth(1, motor_stageXY) != 1: # can be 2
    motor_stageXY.write(thorlabs_lowlvl_list.command_EnCH1)
if thorlabs_lowlvl_list.get_chstate_bycommand_meth(2, motor_stageXY) != 1: # can be 2
    motor_stageXY.write(thorlabs_lowlvl_list.command_EnCH2)

# control CHs

motor_stageXY.write(thorlabs_lowlvl_list.command_req_ch1)
print(motor_stageXY.read(6))
motor_stageXY.write(thorlabs_lowlvl_list.command_req_ch2)
print(motor_stageXY.read(6))

## get POS

posX0 = thorlabs_lowlvl_list.get_posXY_bycommand_meth(1, motor_stageXY)
print(posX0)
# when not homed : 0.00925 mm, or 214748.3605 or -1.032
posY0 = thorlabs_lowlvl_list.get_posXY_bycommand_meth(2, motor_stageXY)
print(posY0)
# when not homed : 0.00925 mm, or 214748.3605

## home

motor_stageXY.write(thorlabs_lowlvl_list.command_home1)

blocking = True
if blocking: # wait for MGMSG_MOT_MOVE_COMPLETED
    bb = ''
    while not bool(bb):
        bb = motor_stageXY.read(6)  # blocks 10sec except if receive a msg of completion
        
motor_stageXY.write(thorlabs_lowlvl_list.command_home2)
if blocking: # wait for MGMSG_MOT_MOVE_COMPLETED
    bb = ''
    while not bool(bb):
        bb = motor_stageXY.read(6) 
    
# thorlabs_lowlvl_list.command_hasBeenHomed2

## move motor X

# short
abs_dist = 27 # mm
commandGen_moveAbsparamXY2 = thorlabs_lowlvl_list.commandGen_moveAbsparamXY_meth(2, abs_dist)
motor_stageXY.write(commandGen_moveAbsparamXY2) # write the displacement to do in advance

commandGen_moveAbsshort2 = thorlabs_lowlvl_list.commandGen_moveAbsshort_meth(2)
motor_stageXY.write(commandGen_moveAbsshort2) # move effectively, according to the value previously entered

# long
abs_dist = 50.5 # mm
command_moveAbs1 = thorlabs_lowlvl_list.commandGen_moveAbsXY_meth(1, abs_dist)
motor_stageXY.write(command_moveAbs1)
if blocking: # wait for MGMSG_MOT_MOVE_COMPLETED
    # bb = ''
    # while not bool(bb):
    print(motor_stageXY.read(20) )
    
    # bb = motor_stageXY.readline()

pos , stat = thorlabs_lowlvl_list.msg_decoder_movecompleted_XY_meth(bb)     

# rel move long

rel_dist = 0.01 # mm
command_moveRel2 = thorlabs_lowlvl_list.commandGen_moveRelXY_meth(2, rel_dist)
motor_stageXY.write(command_moveRel2)
if blocking: # wait for MGMSG_MOT_MOVE_COMPLETED
    bb = ''
    while not bool(bb):
        bb = motor_stageXY.read(20) 

## stop the move profiled

motor_stageXY.write(thorlabs_lowlvl_list.command_stop1) # x
motor_stageXY.write(thorlabs_lowlvl_list.command_stop2) # x


## set acceleration, velocity

max_vel = 18 # m/s
acc_max = 500 # m/s/s
command_setvelparam1 = thorlabs_lowlvl_list.commandGen_setvelparamXY_meth(1, max_vel, acc_max)
motor_stageXY.write(command_setvelparam1)

min_vel, max_acc, max_vel = thorlabs_lowlvl_list.get_velparam_bycommand_meth(1, motor_stageXY)
print('For CH1 : min_vel = %.1f, max_acc = %.1f, max_vel = %.1f' % (min_vel, max_acc, max_vel))
min_vel, max_acc, max_vel = thorlabs_lowlvl_list.get_velparam_bycommand_meth(2, motor_stageXY)
print('For CH2 : min_vel = %.1f, max_acc = %.1f, max_vel = %.1f' % (min_vel, max_acc, max_vel))


## set/get move profile 

# set profile

motor_stageXY.write(thorlabs_lowlvl_list.command_set_profile_old_trapez1)
# motor_stageXY.readline()

motor_stageXY.write(thorlabs_lowlvl_list.command_set_profile_old_trapez2)
# motor_stageXY.readline()

# can also be thorlabs_lowlvl_list.command_set_profile_old_scurve1

# read profile

# motor_stageXY.write(thorlabs_lowlvl_list.command_req_profile1)
# bb = motor_stageXY.read(10)
# bb = motor_stageXY.readline()
# print(bb)
# motor_stageXY.write(thorlabs_lowlvl_list.command_req_profile2)
# bb = motor_stageXY.read(10)
# print(bb)

motor_stageXY.write(thorlabs_lowlvl_list.command_req_profile_old_1)
bb = motor_stageXY.read(18)
print(bb)

print(thorlabs_lowlvl_list2.get_profile_bycommand_meth(1, motor_stageXY))

motor_stageXY.write(thorlabs_lowlvl_list.command_req_profile_old_2)
bb = motor_stageXY.read(18)
print(bb)

print(thorlabs_lowlvl_list2.get_profile_bycommand_meth(2, motor_stageXY))

## set/get Trigger IN/OUT

# read trigger

motor_stageXY.write(thorlabs_lowlvl_list.command_req_trigger1)
bb = motor_stageXY.read(6)
print(bb)

state1 = thorlabs_lowlvl_list.get_trig_bycommand_meth(1, motor_stageXY)
print(state1)
state2 = thorlabs_lowlvl_list.get_trig_bycommand_meth(2, motor_stageXY)
print(state2)

# motor_stageXY.write(thorlabs_lowlvl_list.command_req_trigger2)
# bb = motor_stageXY.read(6) # indeed 6
# print(bb)

# set trigger

# set TRIGGER OUT to Max Vel. Reached for both channels
#- none – none – none- none - TRIGOUT HIGH – none – none - Max Vel. 
# 0-0-0-0-1-0-0-1 in reverse way so 10010000 
# OR - none – none – none- none - TRIGOUT HIGH – IN-MOTION – none - none
# 0-0-0-0-1-1-0-0 in reverse way so 00110000 

thorlabs_lowlvl_list.set_trig_meth(1, motor_stageXY, '10010000')
thorlabs_lowlvl_list.set_trig_meth(2, motor_stageXY, '10010000')

# resume end_of_move messages # MGMSG_ MOT_RESUME_ENDOFMOVEMSGS

msg_ID_resume_end_of_move_ind1 = b'\x6C\x04\x00\x00\x21\x01' 

motor_stageXY.write(msg_ID_resume_end_of_move_ind1)

msg_ID_resume_end_of_move_ind2 = b'\x6C\x04\x00\x00\x22\x01' 

motor_stageXY.write(msg_ID_resume_end_of_move_ind2)

## say that server is alive
# you have to fire this every 50 commands

motor_stageXY.write(thorlabs_lowlvl_list.command_serv_alive1) # say that server is alive
motor_stageXY.write(thorlabs_lowlvl_list.command_serv_alive2) # say that server is alive

## close

motor_stageXY.close() # close instrument
