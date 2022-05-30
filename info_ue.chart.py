
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
        while True:
            self.wsapp_mme.connect("ws://172.16.10.208:9000")       
            self.debug("check connection")
            if self.wsapp_mme.connected:
                break
        self.data = dict() 

    @staticmethod
    def check():
        return True


    def gNodeB_WS(self):
        msg_to_send_mme="{\"message\":\"ue_get\",\"stats\":true}"
        self.wsapp_gNodeB.send(msg_to_send_mme)
        res=self.wsapp_gNodeB.recv()
        return res


    def mme_WS(self):
        msg_to_send_mme="{\"message\":\"ue_get\",\"stats\":true}"
        self.wsapp_mme.send(msg_to_send_mme)
        res=self.wsapp_mme.recv()
        return res


    def get_data(self):
        data = dict()

        if(self.wsapp_gNodeB):
            gNodeB_res=self.gNodeB_WS()
            self.debug("gNB res: ", gNodeB_res)

        if(self.wsapp_mme):
            mme_res=self.mme_WS()
            self.debug("mme_res: ", mme_res)

        #Lets work on gNodeB
        gNodeB_res_json=json.loads(gNodeB_res)

        #Lets work on mme
        mme_res_json=json.loads(mme_res)

###################################################################
# Create charts

        self.UE_total_bytes(gNodeB_res_json, mme_res_json)
        self.UE_Bitrate(gNodeB_res_json, mme_res_json)
        self.UE_transmissions(gNodeB_res_json, mme_res_json)
        self.UE_retransmissions(gNodeB_res_json, mme_res_json)
        self.UE_pucch_SNR(gNodeB_res_json, mme_res_json)
        self.UE_pusch_SNR(gNodeB_res_json, mme_res_json)
        self.UE_ul_path_loss(gNodeB_res_json, mme_res_json)

        for i in range(0, self.num_lines):
            dimension_id = ''.join(['random', str(i)])

            if dimension_id not in self.charts['random']:
                self.charts['random'].add_dimension([dimension_id])

            data[dimension_id] = 10
        data=self.data
        return data

#########################################################################

    def UE_total_bytes(self, gNodeB_res_json, mme_res_json):
        if "ue_list" in mme_res_json and len(mme_res_json["ue_list"]) > 0:
            ue_list_in_mme=mme_res_json["ue_list"]
            for ue_in_mme in ue_list_in_mme:
                if "bearers" in ue_in_mme:
                    for bearer in ue_in_mme["bearers"]:
                        chart_name='_'.join(["UE", bearer["ip"], "total_bytes"])
                        #We add the chart name in the ORDER list
                        if chart_name not in  ORDER:
                            ORDER.append(chart_name)
                        #We create the chart. For titles and units we get the info from the titles_for_charts and units_for_charts dictionaries
                        if chart_name not in self.charts:
                            CHARTS[chart_name]={\
                                'options': [None, ue_in_mme["imsi"], "B", "Total Bytes", "UE_STATS_MME", 'line']}#,\
                        #Now we add the newly created chart to the charts to be displayed.
                        params = [chart_name] + CHARTS[chart_name]['options']
                        self.charts.add_chart(params)
                        #Once the chart has been created we populate it with dimensions (i.e. data to be displayed)
                        dimension_id ='_'.join(["UE", bearer["ip"], "dl_total_bytes"])
                        if dimension_id not in self.charts[chart_name]:
                            self.charts[chart_name].add_dimension([dimension_id,"downlink total bytes",None,None,None])
                            self.data[dimension_id] = bearer["dl_total_bytes"]

                        dimension_id ='_'.join(["UE", bearer["ip"], "ul_total_bytes"])
                        if dimension_id not in self.charts[chart_name]:
                            self.charts[chart_name].add_dimension([dimension_id,"uplink total bytes",None,None,None])
                            self.data[dimension_id] = bearer["ul_total_bytes"]

            else:
                self.debug("=> MME UE list is Empty !")


    def UE_Bitrate(self, gNodeB_res_json, mme_res_json):
        if "ue_list" in gNodeB_res_json and len(gNodeB_res_json["ue_list"]) > 0:
            ue_list_in_gNodeB=gNodeB_res_json["ue_list"]

            for ue_in_gNodeB in ue_list_in_gNodeB:
                if "enb_ue_id" in ue_in_gNodeB:
                    enb_ue_id = ue_in_gNodeB["enb_ue_id"]
                    mme_ue_id = ue_in_gNodeB["mme_ue_id"]
                elif "ran_ue_id" in ue_in_gNodeB:
                    enb_ue_id = ue_in_gNodeB["ran_ue_id"]
                    mme_ue_id = ue_in_gNodeB["amf_ue_id"]
                    if "cells" in ue_in_gNodeB:
                        if "ue_list" in mme_res_json and len(mme_res_json["ue_list"]) > 0:
                            ue_list_in_mme=mme_res_json["ue_list"]
                            for ue_in_mme in ue_list_in_mme:
                                if(("enb_ue_id" in ue_in_mme and "mme_ue_id" in ue_in_mme and enb_ue_id == ue_in_mme["enb_ue_id"] and mme_ue_id == ue_in_mme["mme_ue_id"]) or
                                   ("ran_ue_id" in ue_in_mme and "amf_ue_id" in ue_in_mme and enb_ue_id == ue_in_mme["ran_ue_id"] and mme_ue_id == ue_in_mme["amf_ue_id"])):


                                    for cell in ue_in_gNodeB["cells"]:
                                        chart_name='_'.join(["UE", ue_in_mme["imsi"], "bitrate"])
                                        #We add the chart name in the ORDER list
                                        if chart_name not in  ORDER:
                                            ORDER.append(chart_name)
                                        #We create the chart. For titles and units we get the info from the titles_for_charts and units_for_charts dictionaries
                                        if chart_name not in self.charts:
                                            CHARTS[chart_name]={\
                                                'options': [None, ue_in_mme["imsi"], "bps", "Bitrate", "UE_STATS_GNODEB", 'line']}#,\
                                        #Now we add the newly created chart to the charts to be displayed.
                                        params = [chart_name] + CHARTS[chart_name]['options']
                                        self.charts.add_chart(params)
                                        #Once the chart has been created we populate it with dimensions (i.e. data to be displayed)
                                        dimension_id ='_'.join(["UE", ue_in_mme["imsi"], "dl_bitrate"])
                                        if dimension_id not in self.charts[chart_name]:
                                            self.charts[chart_name].add_dimension([dimension_id,"downlink bitrate",None,None,None])
                                            self.data[dimension_id] = cell["dl_bitrate"] 
                                            self.debug("*************************here")
 

                                        dimension_id ='_'.join(["UE", ue_in_mme["imsi"], "ul_bitrate"])
                                        if dimension_id not in self.charts[chart_name]:
                                            self.charts[chart_name].add_dimension([dimension_id,"uplink bitrate",None,None,None])
                                            self.data[dimension_id] = cell["ul_bitrate"] 
                                            self.debug("*************************here")

                        else:
                            self.debug("=> MME UE list is Empty !")
        else:
            self.debug("=> gNodeB UE list is Empty!")


    def UE_transmissions(self, gNodeB_res_json, mme_res_json):
        if "ue_list" in gNodeB_res_json and len(gNodeB_res_json["ue_list"]) > 0:
            ue_list_in_gNodeB=gNodeB_res_json["ue_list"]
            for ue_in_gNodeB in ue_list_in_gNodeB:
                if "enb_ue_id" in ue_in_gNodeB:
                    enb_ue_id = ue_in_gNodeB["enb_ue_id"]
                    mme_ue_id = ue_in_gNodeB["mme_ue_id"]
                elif "ran_ue_id" in ue_in_gNodeB:
                    enb_ue_id = ue_in_gNodeB["ran_ue_id"]
                    mme_ue_id = ue_in_gNodeB["amf_ue_id"]
                    if "cells" in ue_in_gNodeB:
                        if "ue_list" in mme_res_json and len(mme_res_json["ue_list"]) > 0:
                            ue_list_in_mme=mme_res_json["ue_list"]
                            for ue_in_mme in ue_list_in_mme:
                                if(("enb_ue_id" in ue_in_mme and "mme_ue_id" in ue_in_mme and enb_ue_id == ue_in_mme["enb_ue_id"] and mme_ue_id == ue_in_mme["mme_ue_id"]) or
                                   ("ran_ue_id" in ue_in_mme and "amf_ue_id" in ue_in_mme and enb_ue_id == ue_in_mme["ran_ue_id"] and mme_ue_id == ue_in_mme["amf_ue_id"])):

                                    for cell in ue_in_gNodeB["cells"]:
                                        chart_name='_'.join(["UE", ue_in_mme["imsi"], "transmissions"])
                                        #We add the chart name in the ORDER list
                                        if chart_name not in  ORDER:
                                            ORDER.append(chart_name)
                                        #We create the chart. For titles and units we get the info from the titles_for_charts and units_for_charts dictionaries
                                        if chart_name not in self.charts:
                                            CHARTS[chart_name]={\
                                                'options': [None, ue_in_mme["imsi"], "# of Transport blocks", "Transmissions", "UE_STATS_GNODEB", 'line']}#,\
                                        #Now we add the newly created chart to the charts to be displayed.
                                        params = [chart_name] + CHARTS[chart_name]['options']
                                        self.charts.add_chart(params)
                                        #Once the chart has been created we populate it with dimensions (i.e. data to be displayed)
                                        dimension_id ='_'.join(["UE", ue_in_mme["imsi"], "dl_tx"])
                                        if dimension_id not in self.charts[chart_name]:
                                            self.charts[chart_name].add_dimension([dimension_id,"downlink tx",None,None,None])
                                            self.data[dimension_id] = cell["dl_tx"]

                                        dimension_id ='_'.join(["UE", ue_in_mme["imsi"], "ul_tx"])
                                        if dimension_id not in self.charts[chart_name]:
                                            self.charts[chart_name].add_dimension([dimension_id,"uplink tx",None,None,None])
                                            self.data[dimension_id] = cell["ul_tx"]
                        else:
                            self.debug("=> MME UE list is Empty !")
        else:
            self.debug("=> gNodeB UE list is Empty!")


    def UE_retransmissions(self, gNodeB_res_json, mme_res_json):
        if "ue_list" in gNodeB_res_json and len(gNodeB_res_json["ue_list"]) > 0:
            ue_list_in_gNodeB=gNodeB_res_json["ue_list"]
            for ue_in_gNodeB in ue_list_in_gNodeB:
                if "enb_ue_id" in ue_in_gNodeB:
                    enb_ue_id = ue_in_gNodeB["enb_ue_id"]
                    mme_ue_id = ue_in_gNodeB["mme_ue_id"]
                elif "ran_ue_id" in ue_in_gNodeB:
                    enb_ue_id = ue_in_gNodeB["ran_ue_id"]
                    mme_ue_id = ue_in_gNodeB["amf_ue_id"]
                    if "cells" in ue_in_gNodeB:
                        if "ue_list" in mme_res_json and len(mme_res_json["ue_list"]) > 0:
                            ue_list_in_mme=mme_res_json["ue_list"]
                            for ue_in_mme in ue_list_in_mme:
                                if(("enb_ue_id" in ue_in_mme and "mme_ue_id" in ue_in_mme and enb_ue_id == ue_in_mme["enb_ue_id"] and mme_ue_id == ue_in_mme["mme_ue_id"]) or
                                   ("ran_ue_id" in ue_in_mme and "amf_ue_id" in ue_in_mme and enb_ue_id == ue_in_mme["ran_ue_id"] and mme_ue_id == ue_in_mme["amf_ue_id"])):

                                    for cell in ue_in_gNodeB["cells"]:
                                        chart_name='_'.join(["UE", ue_in_mme["imsi"], "Retransmissions"])
                                        #We add the chart name in the ORDER list
                                        if chart_name not in  ORDER:
                                            ORDER.append(chart_name)
                                        #We create the chart. For titles and units we get the info from the titles_for_charts and units_for_charts dictionaries
                                        if chart_name not in self.charts:
                                            CHARTS[chart_name]={\
                                                'options': [None, ue_in_mme["imsi"], "# of Transport blocks", "Retransmissions", "UE_STATS_GNODEB", 'line']}#,\
                                        #Now we add the newly created chart to the charts to be displayed.
                                        params = [chart_name] + CHARTS[chart_name]['options']
                                        self.charts.add_chart(params)
                                        #Once the chart has been created we populate it with dimensions (i.e. data to be displayed)
                                        dimension_id ='_'.join(["UE", ue_in_mme["imsi"], "dl_retx"])
                                        if dimension_id not in self.charts[chart_name]:
                                            self.charts[chart_name].add_dimension([dimension_id,"downlink retx",None,None,None])
                                            self.data[dimension_id] = cell["dl_tx"]

                                        dimension_id ='_'.join(["UE", ue_in_mme["imsi"], "ul_retx"])
                                        if dimension_id not in self.charts[chart_name]:
                                            self.charts[chart_name].add_dimension([dimension_id,"uplink retx",None,None,None])
                                            self.data[dimension_id] = cell["ul_retx"]
                        else:
                            self.debug("=> MME UE list is Empty !")
        else:
            self.debug("=> gNodeB UE list is Empty!")

    def UE_pucch_SNR(self, gNodeB_res_json, mme_res_json):
        if "ue_list" in gNodeB_res_json and len(gNodeB_res_json["ue_list"]) > 0:
            ue_list_in_gNodeB=gNodeB_res_json["ue_list"]
            for ue_in_gNodeB in ue_list_in_gNodeB:
                if "enb_ue_id" in ue_in_gNodeB:
                    enb_ue_id = ue_in_gNodeB["enb_ue_id"]
                    mme_ue_id = ue_in_gNodeB["mme_ue_id"]
                elif "ran_ue_id" in ue_in_gNodeB:
                    enb_ue_id = ue_in_gNodeB["ran_ue_id"]
                    mme_ue_id = ue_in_gNodeB["amf_ue_id"]
                    if "cells" in ue_in_gNodeB:
                        if "ue_list" in mme_res_json and len(mme_res_json["ue_list"]) > 0:
                            ue_list_in_mme=mme_res_json["ue_list"]
                            for ue_in_mme in ue_list_in_mme:
                                if(("enb_ue_id" in ue_in_mme and "mme_ue_id" in ue_in_mme and enb_ue_id == ue_in_mme["enb_ue_id"] and mme_ue_id == ue_in_mme["mme_ue_id"]) or
                                   ("ran_ue_id" in ue_in_mme and "amf_ue_id" in ue_in_mme and enb_ue_id == ue_in_mme["ran_ue_id"] and mme_ue_id == ue_in_mme["amf_ue_id"])):

                                    for cell in ue_in_gNodeB["cells"]:
                                        chart_name='_'.join(["UE", ue_in_mme["imsi"], "pucch_SNR"])
                                        #We add the chart name in the ORDER list
                                        if chart_name not in  ORDER:
                                            ORDER.append(chart_name)
                                        #We create the chart. For titles and units we get the info from the titles_for_charts and units_for_charts dictionaries
                                        if chart_name not in self.charts:
                                            CHARTS[chart_name]={\
                                                'options': [None, ue_in_mme["imsi"], "dB", "Physical Uplink Control Channel (PUCCH)", "UE_STATS_GNODEB", 'line']}#,\
                                        #Now we add the newly created chart to the charts to be displayed.
                                        params = [chart_name] + CHARTS[chart_name]['options']
                                        self.charts.add_chart(params)
                                        #Once the chart has been created we populate it with dimensions (i.e. data to be displayed)
                                        dimension_id ='_'.join(["UE", ue_in_mme["imsi"], "pucch_snr"])
                                        if dimension_id not in self.charts[chart_name]:
                                            self.charts[chart_name].add_dimension([dimension_id,"pucch SNR",None,None,None])
                                            if "pucch1_snr" in cell:
                                                self.data[dimension_id] = cell["pucch1_snr"]
                                            elif "pucch_snr" in cell:
                                                self.data[dimension_id] = cell["pucch_snr"]
                        else:
                            self.debug("=> MME UE list is Empty !")
        else:
            self.debug("=> gNodeB UE list is Empty!")


    def UE_pusch_SNR(self, gNodeB_res_json, mme_res_json):
        if "ue_list" in gNodeB_res_json and len(gNodeB_res_json["ue_list"]) > 0:
            ue_list_in_gNodeB=gNodeB_res_json["ue_list"]
            for ue_in_gNodeB in ue_list_in_gNodeB:
                if "enb_ue_id" in ue_in_gNodeB:
                    enb_ue_id = ue_in_gNodeB["enb_ue_id"]
                    mme_ue_id = ue_in_gNodeB["mme_ue_id"]
                elif "ran_ue_id" in ue_in_gNodeB:
                    enb_ue_id = ue_in_gNodeB["ran_ue_id"]
                    mme_ue_id = ue_in_gNodeB["amf_ue_id"]
                    if "cells" in ue_in_gNodeB:
                        if "ue_list" in mme_res_json and len(mme_res_json["ue_list"]) > 0:
                            ue_list_in_mme=mme_res_json["ue_list"]
                            for ue_in_mme in ue_list_in_mme:
                                if(("enb_ue_id" in ue_in_mme and "mme_ue_id" in ue_in_mme and enb_ue_id == ue_in_mme["enb_ue_id"] and mme_ue_id == ue_in_mme["mme_ue_id"]) or
                                   ("ran_ue_id" in ue_in_mme and "amf_ue_id" in ue_in_mme and enb_ue_id == ue_in_mme["ran_ue_id"] and mme_ue_id == ue_in_mme["amf_ue_id"])):

                                    for cell in ue_in_gNodeB["cells"]:
                                        chart_name='_'.join(["UE", ue_in_mme["imsi"], "pusch_SNR"])
                                        #We add the chart name in the ORDER list
                                        if chart_name not in  ORDER:
                                            ORDER.append(chart_name)
                                        #We create the chart. For titles and units we get the info from the titles_for_charts and units_for_charts dictionaries
                                        if chart_name not in self.charts:
                                            CHARTS[chart_name]={\
                                                'options': [None, ue_in_mme["imsi"], "dB", "Physical Uplink Shared Channel (PUSCH) SNR", "UE_STATS_GNODEB", 'line']}#,\
                                        #Now we add the newly created chart to the charts to be displayed.
                                        params = [chart_name] + CHARTS[chart_name]['options']
                                        self.charts.add_chart(params)
                                        #Once the chart has been created we populate it with dimensions (i.e. data to be displayed)
                                        dimension_id ='_'.join(["UE", ue_in_mme["imsi"], "pusch_snr"])
                                        if dimension_id not in self.charts[chart_name]:
                                            self.charts[chart_name].add_dimension([dimension_id,"pucch1 SNR",None,None,None])
                                            self.data[dimension_id] = cell["pusch_snr"]
                        else:
                            self.debug("=> MME UE list is Empty !")
        else:
            self.debug("=> gNodeB UE list is Empty!")


    def UE_ul_path_loss(self, gNodeB_res_json, mme_res_json):
        if "ue_list" in gNodeB_res_json and len(gNodeB_res_json["ue_list"]) > 0:
            ue_list_in_gNodeB=gNodeB_res_json["ue_list"]
            for ue_in_gNodeB in ue_list_in_gNodeB:
                if "enb_ue_id" in ue_in_gNodeB:
                    enb_ue_id = ue_in_gNodeB["enb_ue_id"]
                    mme_ue_id = ue_in_gNodeB["mme_ue_id"]
                elif "ran_ue_id" in ue_in_gNodeB:
                    enb_ue_id = ue_in_gNodeB["ran_ue_id"]
                    mme_ue_id = ue_in_gNodeB["amf_ue_id"]
                    if "cells" in ue_in_gNodeB:
                        if "ue_list" in mme_res_json and len(mme_res_json["ue_list"]) > 0:
                            ue_list_in_mme=mme_res_json["ue_list"]
                            for ue_in_mme in ue_list_in_mme:
                                if(("enb_ue_id" in ue_in_mme and "mme_ue_id" in ue_in_mme and enb_ue_id == ue_in_mme["enb_ue_id"] and mme_ue_id == ue_in_mme["mme_ue_id"]) or
                                   ("ran_ue_id" in ue_in_mme and "amf_ue_id" in ue_in_mme and enb_ue_id == ue_in_mme["ran_ue_id"] and mme_ue_id == ue_in_mme["amf_ue_id"])):

                                    for cell in ue_in_gNodeB["cells"]:
                                        chart_name='_'.join(["UE", ue_in_mme["imsi"], "ul_path_loss"])
                                        #We add the chart name in the ORDER list
                                        if chart_name not in  ORDER:
                                            ORDER.append(chart_name)
                                        #We create the chart. For titles and units we get the info from the titles_for_charts and units_for_charts dictionaries
                                        if chart_name not in self.charts:
                                            CHARTS[chart_name]={\
                                                'options': [None, ue_in_mme["imsi"], "dB", "Uplink Path Loss", "UE_STATS_GNODEB", 'line']}#,\
                                        #Now we add the newly created chart to the charts to be displayed.
                                        params = [chart_name] + CHARTS[chart_name]['options']
                                        self.charts.add_chart(params)
                                        #Once the chart has been created we populate it with dimensions (i.e. data to be displayed)
                                        dimension_id ='_'.join(["UE", ue_in_mme["imsi"], "ul_path_loss"])
                                        if dimension_id not in self.charts[chart_name]:
                                            self.charts[chart_name].add_dimension([dimension_id,"uplink path loss",None,None,None])
                                            self.data[dimension_id] = cell["ul_path_loss"]
                        else:
                            self.debug("=> MME UE list is Empty !")

        else:
            self.debug("=> gNodeB UE list is Empty!")
