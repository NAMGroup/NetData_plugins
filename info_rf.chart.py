
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
        self.rf_sample_rate(res_json)
        self.rf_cpu_time(res_json)

        for i in range(0, self.num_lines):
            dimension_id = ''.join(['random', str(i)])

            if dimension_id not in self.charts['random']:
                self.charts['random'].add_dimension([dimension_id])

            data[dimension_id] = 10
        data=self.data
        return data

#########################################################################

    def rf_sample_rate(self, res_json):
        if "rf" in res_json:
            chart_name="rf_info_sample_rate"
            if chart_name not in  ORDER:
                ORDER.append(chart_name)
            if chart_name not in self.charts:
                CHARTS[chart_name]={\
                    'options': [None, "rf_info_sample_rate", "MHz", "Sample Rate", "STATS_GNODEB", 'line']}#,\
            #Now we add the newly created chart to the charts to be displayed.
            params = [chart_name] + CHARTS[chart_name]['options']
            self.charts.add_chart(params)
            #Once the chart has been created we populate it with dimensions (i.e. data to be displayed)
            dimension_id = "rx_sample_rate"
            if dimension_id not in self.charts[chart_name]:
                self.charts[chart_name].add_dimension([dimension_id,"Sample rate in RX",None,None,None])
                self.data[dimension_id] = res_json["rf"]["rx_sample_rate"]

            dimension_id ="tx_sample_rate"
            if dimension_id not in self.charts[chart_name]:
                self.charts[chart_name].add_dimension([dimension_id,"Sample rate in TX",None,None,None])
                self.data[dimension_id] = res_json["rf"]["tx_sample_rate"]
        else:
            self.debug("=> rf list is Empty !")


    def rf_cpu_time(self, res_json):
        if "rf" in res_json:
            chart_name="rf_info_cpu_time"
            if chart_name not in  ORDER:
                ORDER.append(chart_name)
            if chart_name not in self.charts:
                CHARTS[chart_name]={\
                    'options': [None, "rf_info_cpu_time", "MHz", "cpu_time_use", "STATS_GNODEB", 'line']}#,\
            #Now we add the newly created chart to the charts to be displayed.
            params = [chart_name] + CHARTS[chart_name]['options']
            self.charts.add_chart(params)
            #Once the chart has been created we populate it with dimensions (i.e. data to be displayed)
            dimension_id = "rx_cpu_time"
            if dimension_id not in self.charts[chart_name]:
                self.charts[chart_name].add_dimension([dimension_id,"CPU usage for RX",None,None,None])
                self.data[dimension_id] = res_json["rf"]["rx_cpu_time"]

            dimension_id ="tx_cpu_time"
            if dimension_id not in self.charts[chart_name]:
                self.charts[chart_name].add_dimension([dimension_id,"CPU usage for TX",None,None,None])
                self.data[dimension_id] = res_json["rf"]["rx_cpu_time"]
        else:
            self.debug("=> rf list is Empty !")

