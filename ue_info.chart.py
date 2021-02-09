# -*- coding: utf-8 -*-
# Description: example netdata python.d module
# Author: Panagiotis Papaioannou (papajohn-uop) 
# SPDX-License-Identifier: GPL-3.0-or-later

from bases.FrameworkServices.SimpleService import SimpleService

#those two imports are required to connect thous websockets
import websocket
from websocket import create_connection

#we tranform the result into json for easier manipulation
import json
#debug
from pprint import pprint

NETDATA_UPDATE_EVERY=1
priority = 90000

'''
Since we plan to create our charts on run time
we just declare these variables.
Chart order, names option etc will be added on the fly
'''
#CHARTS = {}
#ORDER=[]

ORDER = [
    'random1',
]

CHARTS = {
    'random1': {
        'options': [None, 'A randomm number', 'random number', 'random', 'random', 'line'],
        'lines': [
            ['random1']
        ]
    }
}



'''
+------------------+                              +----------------------+                                              
|                  |                              |              NETDATA |                                              
|                  |                              |                      |                                              
|       gNodeB     |                              |                      |                                              
|                  |                              |+----------+          |                                              
|                  |<---------------------------->||  custom  |          |                                              
|                  |         websocket            ||  plugin  |          |                                              
|                  |<---------------------------->|+----------+          |                                                  v
+------------------+                              +----------------------+
'''


'''
In order to talk with the amarifost gNodeB we set the following parameters:
prot: is ws (should not be changed)
ip: should be the IP of the gNodeB we wish to talk to (This could be moved into a conf file)
gnb_port: Default value (9001) should be OK. Change as required if the GnodeB conf has changed
'''
#gNodeB
prot="ws://"
ip="AMARISOFT_IP_HERE"
gnb_port=":9001"

'''
In this plugin we send try to visualize data from the result of ue_get command.
'''
msg_to_send="{\"message\":\"ue_get\",\"stats\":true}"


'''
Every command returns a lot of information.
Each entry in this dictionary is in the form of: {chart_key:[metric1. metric2, ...metricN]}
This means that the chart keyed chart_key will have n metrics (lines/dimensions in it)
Each chartkey/chart metrics values are selected depending on the data that are returned through the web socket and the infor we want to visualize.
By addinf more rows or by commenting existing rows in this dictionary we can modify the displayed charts.
In this plugin we have decided to display the following charts.

'''
charts_to_create= {
       "bitrate":["dl_bitrate", "ul_bitrate" ] ,
       "tx": ["dl_tx", "ul_tx"],
       "retx":["dl_retx", "ul_retx"],
       "snr":["pucch1_snr","pusch_snr"]
}



'''
In order to define a chart the following info is required for the visualization part:
TITLE:  The chart title (to differentiate between other charts of the same plugin)
units:  The units of the chart. In our plugin we also use the units as the label in the y-axis
legend: The various lines shown in this chart.

CHART


                                  TITLE

      |
      |                                                                                units
      |                                                                                legend
units |
      |
      |
      |____________________________________________________________________________
                      (time)
'''

'''
For each chart we wish to display we have the following dictionary.
Each entry in this dictionary is in the form of: {chart_key:[Title]}
Each entry in the charts dictionary should have an entry in here as well with the same key
The value of each entry is the title to be shown for the chart
'''
titles_for_charts={
       "bitrate":"bitrate" ,
       "tx": "Success  transmissions" ,
       "retx": "Success  retransmissions" ,
       "snr" : "Signal to Noise Ratio"
       }

'''
For each chart we wish to display we have the following dictionary.
Each entry in this dictionary is in the form of: {chart_key:[units]}
Each entry in the charts dictionary should have an entry in here as well with the same key
The value of each entry is the units to be shown on the chart
'''

units_for_charts={
       "bitrate":"bits/second" ,
       "tx": "# of Transport blocks" ,
       "retx":"# of Transport blocks",
       "snr":"Signal/Noise ratio"
        }



'''
For each metric  we wish to display we have the following dictionary.
Each entry in this dictionary is in the form of: {metric_key:[legend]}
Each metric in the charts dictionary values should have an entry in here
The value of each entry is the legend to be shown on the chart descibing the metric
'''
legends_for_charts={
       "dl_bitrate":"downlink bitrate" ,
       "ul_bitrate":"uplink bitrate" ,
       "dl_tx": "downlink tx" ,
       "ul_tx": "uplink tx" ,
       "dl_retx":"downlink retx ",
       "ul_retx":"uplink retx ",
       "pucch1_snr" : "physical uplink control channel (format 1)",
       "pusch_snr" : "physical uplink shared channel"
       }





class Service(SimpleService):
    def __init__(self, configuration=None, name=None):
        SimpleService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS
        #values to show at graphs
        self.values=dict()


    @staticmethod
    def check():
        return True


    def logMe(self,msg):
        self.debug(msg)

    def check_status(self,res):
        self.logMe("Check Status")
        #go json format
        res_json=json.loads(res)
        msg_in_json =  "message" in res_json
        if not msg_in_json:
            return None
        return(res_json["message"])



    def check_connection(self,uri):
        self.logMe("Check Connection")
        ws = websocket.WebSocket()
        try:
            ws = websocket.create_connection(uri)
        except Exception:
        # Although a number of exceptions can occur here
        # we handle them all the same way, return None.
        # As such, enough to just "except Exception."
            self.logMe("websocket create connection failed")
        if ws is None or not ws.connected:
            self.logMe("websocket create connection unsuccessful")
        return ws





    def create_charts(self,name,key,vals,data):
        chart_name=name
        #We add the chart name in the ORDER list
        if chart_name not in  ORDER:
            ORDER.append(chart_name)
        #We create the chart. For titles and units we get the info from the titles_for_charts and units_for_charts dictionaries
        if chart_name not in  self.charts:
            CHARTS[chart_name]={\
            'options': [None, name, units_for_charts[key], titles_for_charts[key], 'CONTEXT_gNodeB_ue', 'line']}#,\
        #Now we add the newly created chart to the charts to be displayed.
        params = [chart_name] + CHARTS[chart_name]['options']
        self.charts.add_chart(params)
        #Once the chart has been created we populate it with dimensions (i.e. data to be displayed)
        for i in range(len(vals)):
            #We create the dimensions name depending in the chart name and the metric name
            dimension_id = '_'.join([name, list(vals.keys())[i]])
            self.debug(dimension_id)
            #We add this dimsnsion to the chart that has been created
            #For the legend part we used the info form the legends_for_charts dictionary
            #The last 100 is divisor: This means that when the value is represented it will be divided by 100
            if dimension_id not in self.charts[chart_name]:
                self.charts[chart_name].add_dimension([dimension_id,legends_for_charts[list(vals.keys())[i]],None,None,100])
            #We populate the data dictionary
            #We add an entry into the data dictionary.
            #The entry will be the value for the metric to be displayed. Since this value might be fractional
            #and only integer values are collected we multiply this by 100.
            #That is why we had the 100 divisor on the dimension creation
            data[dimension_id] = vals[list(vals.keys())[i]]*100

    '''
This is the main function in which we gather the data
    '''
    def collect_gNodeB_ue_get_metrics(self,data):
        mme_connection=prot+ip+gnb_port
        self.logMe(mme_connection)
            #check that we can connect to the amarisoft device
        ws=self.check_connection(mme_connection)
        if ws is None:
            self.logMe("NO CONNECTION")
            return
        if not  ws.connected:
            self.logMe("NOT CONNECTED")
            return
        status=None
        #once connection has been estblished we send the message
        ws.send(msg_to_send)
        #the response comes into two parts: status and actual respone
        res=ws.recv()
        #check that the devices status is ready
        status=None
        status=self.check_status(res)
        if status!="ready":
            self.logMe("NOT READY")
            return
        res=ws.recv()
        #go json format
        res_json=json.loads(res)
        self.logMe(json.dumps( res_json, indent=4))
        #For this message all the interesting info is contained in the ue_list list contained in the response
        #check if ue_list exists
        ue_list_in_json =  "ue_list" in res_json
        if not ue_list_in_json:
            return None
        ue_list_json=res_json["ue_list"]
        #Now we parse each item in the ue list.
        #Each item repsrents a UE
        for ue_index in range(len(ue_list_json)):
            ue=ue_list_json[ue_index]
            #For our plugin we only need part of the info: The id of the UE and the cells object which has the info we require
            # So we keep that nad stripp the rest
            ue_stripped= {k: v for k, v in ue.items() if k  in {"enb_ue_id", "ran_ue_id", "cells"}}
            #The data we wish to visualize are in cell_list list contained in the response
            #check if cell_list exists
            cells_list_in_ue="cells" in ue_stripped
            if cells_list_in_ue:
                cells_in_ue=ue_stripped["cells"]
                #Now we parse each item in the cell list.
                #Each item represents a cell . UEs might be in two cells in case of NSA
                for cell_index in range(len(cells_in_ue)):
                    #For each of this cells we want to have a number of charts (As defined at charts_to_disply dict)
                    #To create each chart we iterate trhough the charts_to_display dict
                    #Each item is a dict entry in the form of: {chart_key:[metric1. metric2, ...metricN]}
                    for index, (key, value) in enumerate(charts_to_create.items()):
                        cell=cells_in_ue[cell_index]
                        #cell_id=cell["cell_id"]
                        #Every cell entry of every ue entry has a lot of info.
                        #For each chart we create we want to keep just the metrics for this chart
                        #So we remove everything  from the cell
                        cell_stripped= {k: v for k, v in cell.items() if k  in value }
                        unit=units_for_charts[key]
                        if "enb_ue_id" in ue:  #4g cell
                            id='_'.join(["ue",str(ue_index),'LTE','cell'])
                        elif  "ran_ue_id" in ue: #5g cell
                            id='_'.join(["ue",str(ue_index),'NR','cell'])
                        else:
                            id="OOOPS"
                        self.logMe(id)
                       # name = '_'.join([id,"cell",str(cell_id), key ])
                        name = '_'.join([id, key ])
                        self.logMe(name)
                        self.logMe(unit)
                        #Once all the required info is gathered we start creating charts
                        self.create_charts(name,key,cell_stripped,data)
        return




    def get_data(self):
        #The data dict is basically all the values to be represented
        # The entries are in the format: { "dimension": value}
        #And each "dimension" shoudl belong to a chart.
        data = dict()
        self.collect_gNodeB_ue_get_metrics(data)


        return data



