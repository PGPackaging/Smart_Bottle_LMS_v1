# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 14:55:50 2018

@author: kinney.ja & fields.n
"""

# MSCL Example: NodePing
#   This examples shows how to open a connection with a Base Station,
#   ping a Node, and get the result and its information
#
# Updated: 02/25/2015

# import the mscl library
import codecs
import sys
import mscl
import serial
from serial.tools import hexlify_codec
from serial.tools.list_ports import comports
import time
from time import sleep
import os
import csv


def ask_for_port():

    sys.stderr.write('\n--- Searching for ports:\n')
    ports = []
    for n, (port, desc, hwid) in enumerate(sorted(comports()), 1):
        sys.stderr.write('--- {:2}: {!r}\n'.format(n, desc))
        ports.append(port)
    while True:
        port = input('--- Enter port index or full name: ')
        try:
            index = int(port) - 1
            if not 0 <= index < len(ports):
                sys.stderr.write('--- Invalid index!\n')
                continue
        except ValueError:
            pass
        else:
            port = ports[index]
        return port

def nodecount():
    node_num=[]
    node_count = input ('--- Enter the number of nodes you have: ')
    if int(node_count)==1:
        node0 = input('--- Enter node address 1: ')
        return node_num.append(int(node0))
    elif int(node_count)==2:
        node0 = input('--- Enter node address 1: ')
        node1 = input('--- Enter node address 2: ')
        node_num.append(int(node0))
        node_num.append(int(node1))
        return node_num
    else:
        print('Invalid node count')
        
        
        
def open_comms(COM_PORT):
    try:
    # create a Serial Connection with the specified COM Port, default baud rate of 921600
        connection = mscl.Connection.Serial(COM_PORT)

    # create a BaseStation with the connection
        baseStation = mscl.BaseStation(connection)

        if not baseStation.ping():
            print("Failed to ping the Base Station")
        else:
            print("Base Station is active")
            print("Attempting to enable the beacon...")
    # enable the beacon on the Base Station using the PC time
            startTime = baseStation.enableBeacon()
            print("Successfully enabled the beacon on the Base Station")
            print("Beacon's initial Timestamp:", startTime)
            print("Beacon is active")
            print("Sleeping for 3 seconds...")
            sleep(3)
            baseStation.disableBeacon()
    # if we got here, no exception was thrown, so disableBeacon was successful
            print("Successfully disabled the beacon on the Base Station")
            return connection,baseStation
    
    except Exception as e:
        print("Error: ",e)
        print('Check that '+ COM_PORT + ' is not in use and nodes are not connect to Sensor Connect')
        close_comms(connection)
        
def close_comms(connection):
    try:
        connection.disconnect()
    except Exception:
        print("Error: Comm port was never open or other error has occured please check connections and restart")
    
    
def ping_test(node_num,connection,baseStation):
    node=[]
    node.append(mscl.WirelessNode(node_num[0], baseStation))
    node.append(mscl.WirelessNode(node_num[1], baseStation))
    response=[]
    node0=0
    node1=0
    while True:
        try:
            # create a WirelessNode with the BaseStation we created
        #node = mscl.WirelessNode(NODE_ADDRESS, baseStation)
            print ("Attempting to ping the Nodes...")
            
            
             # ping the Node
            response.append(node[0].ping())
            response.append(node[1].ping())

            if response[0].success():
                node0=1
            if response[1].success():
                node1=1
            
            if node0+node1==2:
                print ("Successfully pinged Node", node_num[0])
                print ("Base Station RSSI:", response[0].baseRssi())
                print ("Node RSSI:", response[0].nodeRssi())
                print ("Successfully pinged Node", node_num[1])
                print ("Base Station RSSI:", response[1].baseRssi())
                print ("Node RSSI:", response[1].nodeRssi())
                return node0,node1
            if node0==0:
                print ("Failed to ping Node 1 address...")
            if node1==0:
                print ("Failed to ping Node 2 address...")

            return node0,node1
        
        except Exception as e:
                print ("Error:", e )
                close_comms(connection)

def create_network(baseStation,node_num):
    try:
        network = mscl.SyncSamplingNetwork(baseStation)
        print ('Adding nodes to the network...')
        network.addNode(node_num[0])
        print ('Added node 1...')
        network.addNode(node_num[1])
        print ('Added node 2...')
        # can get information about the network
        print("Network info: ")
        print("Network OK: ", network.ok())
        print("Percent of Bandwidth: ", network.percentBandwidth())
        print("Lossless Enabled: ", network.lossless())
        # apply the network configuration to every node in the network
        print("Applying network configuration",
        network.applyConfiguration())
        print("Done.")
        print("Starting the network...", network.startSampling())
        return network
    
    except Exception as e:
        print('Error:', e)

def start_sampling(network,baseStation,node_num):
    
    print("Done.")
    data=[]
    out = csv.writer(open("LMS_SB.csv","w"), delimiter=',')
    try:
        # endless loop of reading in data
        record_time=30
        record_start = time.time()
        while time.time() < record_start + record_time:

            # get all of the data sweeps that have been collected by the BaseStation, with a timeout of 500 milliseconds
            sweeps = baseStation.getData(500)

            for sweep in sweeps:
                # print out information about the sweep
                print("Packet Received",)
                print("Node", sweep.nodeAddress(),)
                print("Timestamp", sweep.timestamp(),)
                print("Tick", sweep.tick(),)
                print("Sample Rate", sweep.sampleRate().prettyStr(),)
                print("Base RSSI: ", sweep.baseRssi(),)
                print("Node RSSI: ", sweep.nodeRssi(),)

                print("DATA: ",)
                # iterate over each point in the sweep
                for dataPoint in sweep.data():
                    # just printing this out as a string. Other methods (ie. as_float, as_uint16) are also available.
                    print(dataPoint.channelName(), ":", dataPoint.as_float(),)
                    #data.append(dataPoint.as_float(),)
                    
                    if node_num[0] == 63084:
                        d_p = dataPoint.as_float()
                        #cal for 63084 torque
                        cal_data = ((d_p*.0882)-183.99)
                        print(cal_data)
                        data.append(cal_data)
                    elif node_num[1] == 62960:
                        d_p = dataPoint.as_float()
                        cal_data = ((d_p*0.09)-185.82)
                        print(cal_data)
                        data.append(cal_data)
                    else:
                        print('node numbers are 63084 or 92960')
                    
                    
                    
                    
                print("")
            out.wrirterow(data)
            return data
                
    except Exception as e:
        print("Error:", e)  
    

def main():
    port = ask_for_port()
    node_num=nodecount()
    COM_PORT = port
    connection, baseStation = open_comms(COM_PORT)
    ping_test(node_num,connection,baseStation)
    network=create_network(baseStation,node_num)
    #data=start_sampling(network,baseStation,node_num)
    
main()
