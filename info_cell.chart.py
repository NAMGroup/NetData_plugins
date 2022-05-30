
from bases.FrameworkServices.SimpleService import SimpleService

priority = 90000

#those two imports are required to connect thous websockets
import websocket

#we tranform the result into json for easier manipulation
import json
#debug
from pprint import pprint
#update_every=2

ORDER = [
    'random',
]

CHARTS = {
    'random': {
        'options': [None, 'A random number', 'random number', 'random', 'random', 'line'],
        'lines': [
            ['random1']
        ]
    }
}


class Service(SimpleService):

    def __init__(self, configuration=None, name=None):
        SimpleService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS
        self.num_lines = self.configuration.get('num_lines', 1)
        self.lower = self.configuration.get('lower', 0)
        self.upper = self.configuration.get('upper', 100)
        self.wsapp_gNodeB = websocket.WebSocket()
        self.wsapp_mme = websocket.WebSocket()
        while True:
            self.wsapp_gNodeB.connect("ws://172.16.10.208:9001")       
            self.debug("check connection")
            if self.wsapp_gNodeB.connected:
                break
        self.data = dict() 

    @staticmethod
    def check():
        return True


    def gNodeB_WS(self):
        msg_to_send_mme="{\"message\":\"stats\",\"rf\":true}"
        self.wsapp_gNodeB.send(msg_to_send_mme)
        res=self.wsapp_gNodeB.recv()
        return res

    def get_data(self):
        data = dict()

        if(self.wsapp_gNodeB):
            gNodeB_res=self.gNodeB_WS()
            #self.debug("gNB res: ", gNodeB_res)

        res_json=json.loads(gNodeB_res)

###################################################################
# Create charts
        self.cell_bitrate(res_json)
        self.cell_transmissions(res_json)
        self.cell_retransmissions(res_json)

        for i in range(0, self.num_lines):
            dimension_id = ''.join(['random', str(i)])

            if dimension_id not in self.charts['random']:
                self.charts['random'].add_dimension([dimension_id])

            data[dimension_id] = 10
        data=self.data
        return data

#########################################################################

    def cell_bitrate(self, res_json):
        if "cells" in res_json:
            for i in range(1, len(res_json["cells"]) + 1):
                chart_name='_'.join(["cell", str(i), "bitrate"])
                if chart_name not in  ORDER:
                    ORDER.append(chart_name)
                if chart_name not in self.charts:
                    CHARTS[chart_name]={\
                        'options': [None, '_'.join(["cell", str(i), "bitrate"]), "bps", "bitrate", "STATS_GNODEB", 'line']}#,\
                #Now we add the newly created chart to the charts to be displayed.
                params = [chart_name] + CHARTS[chart_name]['options']
                self.charts.add_chart(params)
                #Once the chart has been created we populate it with dimensions (i.e. data to be displayed)
                dimension_id = '_'.join(["cell", str(i), "dl_bitrate"])
                if dimension_id not in self.charts[chart_name]:
                    self.charts[chart_name].add_dimension([dimension_id,"downlink bitrate",None,None,None])
                    self.data[dimension_id] = res_json["cells"][str(i)]["dl_bitrate"]

                dimension_id ='_'.join(["cell", str(i),"ul_bitrate"])
                if dimension_id not in self.charts[chart_name]:
                    self.charts[chart_name].add_dimension([dimension_id,"uplink bitrate",None,None,None])
                    self.data[dimension_id] = res_json["cells"][str(i)]["ul_bitrate"]
        else:
            self.debug("=> cell list is Empty !")

    def cell_transmissions(self, res_json):
        if "cells" in res_json:
            for i in range(1, len(res_json["cells"]) + 1):
                chart_name='_'.join(["cell", str(i),"tx"])
                if chart_name not in  ORDER:
                    ORDER.append(chart_name)
                if chart_name not in self.charts:
                    CHARTS[chart_name]={\
                        'options': [None, '_'.join(["cell", str(i),"tx"]), "# of Transport blocks", "Transmissions", "STATS_GNODEB", 'line']}#,\
                #Now we add the newly created chart to the charts to be displayed.
                params = [chart_name] + CHARTS[chart_name]['options']
                self.charts.add_chart(params)
                for i in range(1, len(res_json["cells"]) + 1):
                    #Once the chart has been created we populate it with dimensions (i.e. data to be displayed)
                    dimension_id = '_'.join(["cell", str(i),"dl_tx"])
                    if dimension_id not in self.charts[chart_name]:
                        self.charts[chart_name].add_dimension([dimension_id,"downlink tx",None,None,None])
                        self.data[dimension_id] = res_json["cells"][str(i)]["dl_tx"]

                    dimension_id ='_'.join(["cell", str(i),"ul_tx"])
                    if dimension_id not in self.charts[chart_name]:
                        self.charts[chart_name].add_dimension([dimension_id,"uplink tx",None,None,None])
                        self.data[dimension_id] = res_json["cells"][str(i)]["ul_tx"]
        else:
            self.debug("=> cell list is Empty !")

    def cell_retransmissions(self, res_json):
        if "cells" in res_json:
            for i in range(1, len(res_json["cells"]) + 1):
                chart_name='_'.join(["cell", str(i),"retx"])
                if chart_name not in  ORDER:
                    ORDER.append(chart_name)
                if chart_name not in self.charts:
                    CHARTS[chart_name]={\
                        'options': [None,'_'.join(["cell", str(i),"retx"]), "# of Transport blocks", "Retransmissions", "STATS_GNODEB", 'line']}#,\
                #Now we add the newly created chart to the charts to be displayed.
                params = [chart_name] + CHARTS[chart_name]['options']
                self.charts.add_chart(params)
                for i in range(1, len(res_json["cells"]) + 1):
                    #Once the chart has been created we populate it with dimensions (i.e. data to be displayed)
                    dimension_id = '_'.join(["cell", str(i),"dl_retx"])
                    if dimension_id not in self.charts[chart_name]:
                        self.charts[chart_name].add_dimension([dimension_id,"downlink retx",None,None,None])
                        self.data[dimension_id] = res_json["cells"][str(i)]["dl_retx"]

                    dimension_id ='_'.join(["cell", str(i),"ul_tx"])
                    if dimension_id not in self.charts[chart_name]:
                        self.charts[chart_name].add_dimension([dimension_id,"uplink retx",None,None,None])
                        self.data[dimension_id] = res_json["cells"][str(i)]["ul_retx"]
        else:
            self.debug("=> cell list is Empty !")

