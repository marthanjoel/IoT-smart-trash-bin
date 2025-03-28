import json
import time
from MyMqttBase2 import MyMQTT
import requests

class QuantityCheck():
    def __init__(self, quantity_check_info, service_info):
        
        self.info = json.load(open(quantity_check_info, "r"))
        
        self.clientID = self.info["name"]
        self.serviceType = self.info["ServiceType"]
        self.topicS1 = self.info["topicS1"]
        self.topicS2 = self.info["topicS2"]
        self.topicP = self.info["topicP"]

        self.service_info = json.load(open(service_info, "r"))
                
        request_url = 'http://' + str(self.service_info["info"]["IP"]) + ':' + str(self.service_info["info"]["port"]) + '/broker'
        request_url1 = 'http://' + str(self.service_info["info"]["IP"]) + ':' + str(self.service_info["info"]["port"]) + '/res_cat'
        
        request_string = requests.get(request_url)
        request_string1 = requests.get(request_url1)
        
        subscribe_data = {}
        
        subscribe_data["name"] = self.clientID
        subscribe_data["ServiceType"] = self.serviceType
        subscribe_data["topic"] = self.topicP
        
        self.headers = {"Content-Type": "application/json"}
        
        requests.put('http://' + str(self.service_info["info"]["IP"]) + ':' + str(self.service_info["info"]["port"]), json = subscribe_data, headers=self.headers)
        
        self.resourceCatalog = request_string1.json()["info"]["IP"]
        self.res_port = request_string1.json()["info"]["port"]
        
        self.broker = request_string.json()["IP"]
        self.port = request_string.json()["port"]
        
        self.client = MyMQTT(self.clientID, self.broker, self.port, self)
        
    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topicS1)
        self.client.mySubscribe(self.topicS2)
    
    def stop(self):
        self.client.unsubscribe(self.topicS1)
        self.client.unsubscribe(self.topicS2)
        time.sleep(3)
        self.client.stop()
        
    def notify(self, topic, payload):
        messageReceived = json.loads(payload)
        bn = messageReceived["bn"]
        id = bn.split('/')[1]
        
        if topic.split("/")[0:2] == self.topicS1.split("/")[0:2]:
            # ultrasonic
            
            returnMessage = {}
            
            returnMessage["name"] = self.clientID
            returnMessage["time"] = str(time.time())
            returnMessage["measurementName"] = messageReceived["e"]["n"]
            
            trashbin_url = "http://" + self.resourceCatalog + ":" + str(self.res_port) + f"/searchByID?param={str(id)}"
            trashbin_info = requests.get(trashbin_url)
            max_capacity = trashbin_info.json()["max_capacity"]
            returnMessage["entity"] = trashbin_info.json()["entity"]
            
            returnMessage["TrashBinID"] = id
            
            value = messageReceived["e"]["v"]
            
            if float(value) < float(max_capacity) * 0.3:
                returnMessage["condition"] = "low"
            elif float(value) < float(max_capacity) * 0.7:
                returnMessage["condition"] = "normal"
            else:
                returnMessage["condition"] = "alert"
            
            publish_topic = self.topicP + f"/{str(id)}"
            
            self.publish(publish_topic, returnMessage)
            
            
        elif topic == self.topicS2:
            #weight 
            
            returnMessage = {}
            
            returnMessage["name"] = self.clientID
            returnMessage["time"] = str(time.time())
            returnMessage["measurementName"] = messageReceived["e"]["n"]
            
            trashbin_url = "http://" + self.resourceCatalog + ":" + str(self.res_port) + f"/searchByID?param={str(id)}"
            trashbin_info = requests.get(trashbin_url)
            max_weight = trashbin_info.json()["max_weight"]
            returnMessage["entity"] = trashbin_info.json()["entity"]
            
            returnMessage["TrashBinID"] = id
            
            value = messageReceived["e"]["v"]
            
            if float(value) < float(max_weight) * 0.3:
                returnMessage["condition"] = "low"
            elif float(value) < float(max_weight) * 0.7:
                returnMessage["condition"] = "normal"
            else:
                returnMessage["condition"] = "alert"
            
            self.publish(self.topicP, returnMessage)
        
        else:
            print("Error on msg received, topic not recognized")
       
       
    def publish(self, topic, msg):
        self.client.myPublish(topic, msg)
        print("published\n" + json.dumps(msg) + '\nOn topic: ' + f'{topic}') 
       

if __name__ == '__main__':
    time.sleep(5)
    QuantityCheck_obj = QuantityCheck('quantity_check_info.json', 'service_info.json')

    QuantityCheck_obj.start()
    
    while True:
        time.sleep(3)

