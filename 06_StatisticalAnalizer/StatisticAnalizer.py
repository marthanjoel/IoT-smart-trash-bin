import json
import requests
import cherrypy
import numpy as np

class StatisticAnalizer():
    exposed = True
    def __init__(self, statistical_info, service_info):
        
        self.info = json.load(open(statistical_info, "r"))
        
        self.clientID = self.info["name"]
        self.service_info = json.load(open(service_info, "r"))
        self.serviceType = self.info["ServiceType"] 

        subscribe_data = {}
        
        subscribe_data["name"] = self.clientID
        subscribe_data["ServiceType"] = self.serviceType
        subscribe_data["info"] = self.info["info"]
        
        print(subscribe_data)

        self.headers = {"Content-Type": "application/json"}
        
        requests.put('http://' + self.service_info["info"]["IP"] + ':' + self.service_info["info"]["port"], json = subscribe_data, headers=self.headers)
        
    def GET(self, *uri, **params):
        # Making GET request to the specified URL
        
        if(params["ID"] != None):
            TrashBin_ID = params["ID"]
        else:
            raise cherrypy.HTTPError(500, "Error retrieving data from the user")
        
        #search ThingSpeak adaptor data
        
        response = requests.get('http://' + self.service_info["info"]["IP"] + ':' + str(self.service_info["info"]["port"]) +"/get_service?Service_name=ThingSpeakAdaptor")

        # Check if the request was successful
        if response.status_code != 200:
            raise cherrypy.HTTPError(500, "Error retrieving data from the API")

        # Parse the JSON response
        json_data = response.json()
        
        thingspeak_ip = json_data["info"]["IP"]
        thingspeak_port = json_data["info"]["port"]
        
        response = requests.get("http://" + thingspeak_ip + ":" + str(thingspeak_port) + "/GetData?TrashBin_ID=" +TrashBin_ID)

        if response.status_code != 200:
            raise cherrypy.HTTPError(500, "Error retrieving data from the API")

        # Parse the JSON response
        json_data = response.json()
        
        print(json_data)
        
        valid_data = {
            "field1": [],
            "field2": [],
            "field3": [],
            "field4": [],
            "field5": [],
            "field6": [],
            "field7": [],
            "field8": []
            }
        
                
        for element in json_data["feeds"]:
            for i in range(8):
                if(element[f"field{i+1}"] != None):
                    valid_data[f"field{i+1}"].append(float(element[f"field{i+1}"]))
                    
        def count_variance(avg, list):
            
            times = 0
            
            print(list)
            
            for element in list:
                if float(element) >= float(avg):
                    times += 1 
            return times/len(list)
            
                            
        return_json = {
            
            "QualityCheck" : {
                "LastValue" : valid_data["field1"][-1] if valid_data["field1"] else 0 ,
                "AlertPercentage" : count_variance(1, valid_data["field1"]) * 100 if valid_data["field1"]  else 0
            },
            
            "QuantityCheck" : {
                "LastValue" : valid_data["field2"][-1] if valid_data["field2"] else 0,
                "AlertPercentage" : count_variance(1, valid_data["field2"]) * 100 if valid_data["field2"] else 0
            },
            
            "Temperature": {
                "LastValue": valid_data["field4"][-1] if valid_data["field4"] else 0 ,
                "Max": max(valid_data["field4"]) if valid_data["field4"] else 0,
                "Min": min(valid_data["field4"]) if valid_data["field4"] else 0,
                "Average": np.mean(valid_data["field4"]) if valid_data["field4"] else 0,
                "Variance" : count_variance(np.mean(valid_data["field4"]), valid_data["field4"]) if valid_data["field4"] else 0
            },
            
            "Humidity": {
                "LastValue": valid_data["field5"][-1] if valid_data["field5"] else 0 ,
                "Max": max(valid_data["field5"]) if valid_data["field5"] else 0,
                "Min": min(valid_data["field5"]) if valid_data["field5"] else 0,
                "Average": np.mean(valid_data["field5"]) if valid_data["field5"] else 0,
                "Variance" : count_variance(np.mean(valid_data["field5"]), valid_data["field5"]) if valid_data["field5"] else 0
            },
            
            "Ultrasonic": {
                "LastValue": valid_data["field6"][-1] if valid_data["field6"] else 0 ,
                "Max": max(valid_data["field6"]) if valid_data["field6"] else 0,
                "Min": min(valid_data["field6"]) if valid_data["field6"] else 0,
                "Average": np.mean(valid_data["field6"]) if valid_data["field6"] else 0,
                "Variance" : count_variance(np.mean(valid_data["field6"]), valid_data["field6"]) if valid_data["field6"] else 0
            },
            
            "Weight": {
                "LastValue": valid_data["field7"][-1] if valid_data["field7"] else 0 ,
                "Max": max(valid_data["field7"]) if valid_data["field7"] else 0,
                "Min": min(valid_data["field7"]) if valid_data["field7"] else 0,
                "Average": np.mean(valid_data["field7"]) if valid_data["field7"] else 0,
                "Variance" : count_variance(np.mean(valid_data["field7"]), valid_data["field7"]) if valid_data["field7"] else 0
            },
            
            "Gas": {
                "LastValue": valid_data["field8"][-1] if valid_data["field8"] else 0 ,
                "Max": max(valid_data["field8"]) if valid_data["field8"] else 0,
                "Min": min(valid_data["field8"]) if valid_data["field8"] else 0,
                "Average": np.mean(valid_data["field8"]) if valid_data["field8"] else 0,
                "Variance" : count_variance(np.mean(valid_data["field8"]), valid_data["field8"]) if valid_data["field8"] else 0
            }
                    
        }
                
        print(f"Sent data {json.dumps(return_json)}")
        
        return json.dumps(return_json)
    
    def POST(self, *uri, **params):
        pass

    def PUT(self, *uri, **params):
        pass
    
    def DELETE(self):
        pass
    

if __name__ == "__main__":
    service_info = 'statistical_info.json'
    settings = json.load(open(service_info, 'r'))
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    webService = StatisticAnalizer("statistical_info.json", "service_info.json")
    cherrypy.tree.mount(webService,'/',conf)
    cherrypy.config.update({'server.socket_host': settings['info']["IP"]})
    cherrypy.config.update({"server.socket_port": int(settings['info']["port"])})
    cherrypy.engine.start()
