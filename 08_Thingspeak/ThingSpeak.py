import requests
import json
from MyMqttBase2 import MyMQTT
import time
import cherrypy

class Thingspeak_Adaptor():
    exposed = True
    def __init__(self, thingspeak_info, service_info):
        
        self.info = json.load(open(thingspeak_info, "r"))
        self.service_info = json.load(open(service_info, "r"))
    
        self.baseURL = self.info["ThingspeakURL"]
        self.api = self.info["APIKEY"]
                
        self.topicS1 = self.info["topicS1"] + "QualityCheck/#"
        self.topicS2 = self.info["topicS1"] + "QuantityCheck/#"
        self.topicS3 = self.info["topicS1"] + "AlertCheck/#"
        self.topicS4 = self.info["topicS2"] + "#"
        
        request_url = 'http://' + self.service_info["info"]["IP"] + ':' + str(self.service_info["info"]["port"]) + '/broker'
        request_string = requests.get(request_url)
        
        self.serviceType = self.info["ServiceType"] 
        self.clientID = self.info["name"]
        
        subscribe_data = {}
        
        subscribe_data["name"] = self.clientID
        subscribe_data["ServiceType"] = self.serviceType
        subscribe_data["topic"] = ""
        subscribe_data["info"] = self.info["info"]
        
        self.headers = {"Content-Type": "application/json"}
        
        requests.put('http://' + self.service_info["info"]["IP"] + ':' + str(self.service_info["info"]["port"]), json = subscribe_data, headers=self.headers)
        
        self.broker = request_string.json()["IP"]
        self.port = request_string.json()["port"]
        
        self.client = MyMQTT(self.clientID, self.broker, self.port, self)

    def start(self):
        self.client.start() 
        self.client.mySubscribe(self.topicS1)
        self.client.mySubscribe(self.topicS2)
        self.client.mySubscribe(self.topicS3)
        self.client.mySubscribe(self.topicS4)
            
    def stop(self):
        self.client.unsubscribe(self.topicS1)
        self.client.unsubscribe(self.topicS2)
        self.client.unsubscribe(self.topicS3)
        self.client.unsubscribe(self.topicS4)
        
        time.sleep(3)
        self.client.stop()
        
    def notify(self,topic, payload):
        message = json.loads(payload)
        id = topic.split("/")[-1]
        
        print(topic)
        
        if topic.split("/")[0:2] == self.topicS1.split("/")[0:2]:
            self.handleServiceNotification(message, id)
        elif topic.split("/")[0:2] == self.topicS4.split("/")[0:2]:
            self.handleSensorsNotification(message, id)
        else:
            print("Topic not recognized")
            
    def handleServiceNotification(self, message, id):
        print(message)
        decide_measurement = message["name"]
        value = message["condition"]
        if value is not None:
            if value == "normal":
                value = 0
            elif value == "low":
                value = -1
            elif value == "alert":
                value = 1
            print(f"Received {decide_measurement} with value {value}")
        self.processMeasurement(decide_measurement, value, id) # type: ignore
        
            
    def handleSensorsNotification(self, message_decoded, id):
        if "e" in message_decoded and "n" in message_decoded["e"] and "v" in message_decoded["e"]:
            decide_measurement = message_decoded["e"]["n"]
            value = float(message_decoded["e"]["v"])
            print(decide_measurement, value)
            self.processMeasurement(decide_measurement, value, id)
        print(decide_measurement, value)
    
    def processMeasurement(self, decide_measurement, value, id):
        message = {}
        if decide_measurement == "QualityCheck":
            print("\nQuality Check Message")
            message["field_number"] = 1
        elif decide_measurement == "QuantityCheck":
            print("\nQuantity Check Message")
            message["field_number"] = 2
        elif decide_measurement == "AlertCheck":
            print("\nAlert Check Message")
            message["field_number"] = 3
        elif decide_measurement == "temperature":
            print("\nTemperature Message")
            message["field_number"] = 4
        elif decide_measurement == "humidity":
            print("\Humidity Message")
            message["field_number"] = 5
        elif decide_measurement == "ultraSonic":
            print('Ultrasonic - Height Message')
            message["field_number"] = 6
        elif decide_measurement == "weight":
            print("\Weight Message")
            message["field_number"] = 7
        elif decide_measurement == "gas":
            print("\Gas Message")
            message["field_number"] = 8
        else:
            print("Error: Unknown measurement")
            return

        print(message)
        
        #retrieve writeAPI
        
        request_url = 'http://' + self.service_info["info"]["IP"] + ':' + str(self.service_info["info"]["port"]) + '/res_cat'
        request_string = requests.get(request_url)
        
        res_IP = request_string.json()["info"]["IP"]
        res_port = request_string.json()["info"]["port"]
        
        res_url = 'http://' + res_IP + ':' + str(res_port) + f'/searchByID?param={id}'
        res_data = requests.get(res_url)
        #print(res_data)
        writeAPI = res_data.json()["WriteAPI"]
        
        self.uploadThingspeak(message["field_number"], value, writeAPI)
        
        
    def uploadThingspeak(self, field_number, field_value, writeAPI):
        urlToSend = f'{self.baseURL}{writeAPI}&field{field_number}={field_value}'
        
        try:
            cond = True
            while cond:
                r = requests.get(urlToSend)
                if r.text != "0":
                    cond = False
                    print(f"{r.text} Message {field_number}: {field_value} successfully sent to Thingspeak")
        except Exception as e:
            print(f"Error uploading to Thingspeak: {e}")

    def GET(self, *uri, **params):
        if(len(uri) > 0):
            if(uri[0] == "NewTrashBin"):
                #creazione canale e restituzione ID 
                post_url = f"https://api.thingspeak.com/channels.json?api_key={self.api}&name=TrashBin&public_flag=true&field1=QualityCheck&field2=QuantityCheck&field3=AlertCheck&field4=Temperature&field5=Humidity&field6=Ultrasonic&field7=Weight&field8=Gas"
                answer = requests.post(post_url)
                print("\n\n")
                print(answer.json())
                print("\n\n")
                print(answer.json()["id"])
                return_json ={
                    "id" : answer.json()["id"],
                    "WriteAPI" : answer.json()["api_keys"][0]["api_key"],
                    "ReadAPI" : answer.json()["api_keys"][1]["api_key"],
                }
                return json.dumps(return_json)
            
            elif(uri[0] == "GetData"):
                
                try:
                    TrashBin_ID = params["TrashBin_ID"]
                    url = f"https://api.thingspeak.com/channels/{TrashBin_ID}/feed.json?results=100"
                    response = requests.get(url)

                    # Check if the request was successful
                    if response.status_code != 200:
                        raise cherrypy.HTTPError(500, "Error retrieving data from the API")

                    # Parse the JSON response
                    json_data = response.json()
                    
                    return json.dumps(json_data)
                except Exception as e:
                    print(f"Error contacting to Thingspeak: {e}")
                    
             
        else:
           raise cherrypy.HTTPError(500, "No Path detected")
       
    def DELETE(self, *uri,  **params):
        if(len(uri) > 0):
            response = requests.delete("https://api.thingspeak.com/channels/"+str(uri[0])+".json?api_key=" + self.api)
        else:
            raise cherrypy.HTTPError(500, "No channel on path")
        
if __name__ == "__main__":
    time.sleep(5)
    thingspeak_info = 'thingspeak_info.json'
    settings = json.load(open(thingspeak_info, 'r'))    
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    webService = Thingspeak_Adaptor('thingspeak_info.json', 'service_info.json')
    cherrypy.tree.mount(webService,'/',conf)
    cherrypy.config.update({'server.socket_host': settings['info']["IP"]})
    cherrypy.config.update({"server.socket_port": int(settings['info']["port"])})
    cherrypy.engine.start()
    webService.start()