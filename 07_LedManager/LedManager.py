import json
import time as time
from MyMqttBase2 import MyMQTT
import requests

class LedManager():

    def __init__(self, led_manager_info, service_info):
        
        self.info = json.load(open(led_manager_info, "r"))
        
        self.clientID = self.info["name"]
        self.serviceType = self.info["ServiceType"]
        self.topicS = self.info["topicS"]
        self.topicP = self.info["topicP"]

        self.service_info = json.load(open(service_info, "r"))
                
        request_url = 'http://' + self.service_info["info"]["IP"] + ':' + self.service_info["info"]["port"] + '/broker'
        request_url1 = 'http://' + self.service_info["info"]["IP"] + ':' + self.service_info["info"]["port"] + '/res_cat'
        
        request_string = requests.get(request_url)
        request_string1 = requests.get(request_url1)
        
        subscribe_data = {}
        
        subscribe_data["name"] = self.clientID
        subscribe_data["ServiceType"] = self.serviceType
        subscribe_data["topic"] = self.topicP
        
        headers = {"Content-Type": "application/json"}
        
        requests.put('http://' + self.service_info["info"]["IP"] + ':' + self.service_info["info"]["port"], json = subscribe_data, headers=headers)
        
        self.resourceCatalog = request_string1.json()["info"]["IP"]
        self.res_port = request_string1.json()["info"]["port"]
        
        self.broker = request_string.json()["IP"]
        self.port = request_string.json()["port"]
        
        self.client = MyMQTT(self.clientID, self.broker, self.port, self)
        
    def start(self):
        self.client.start()
        time.sleep(3)  # Timer of 3 second (to deal with asynchronous)
        self.client.mySubscribe(self.topicS)
    
    def stop(self):
        self.client.unsubscribe(self.topicS)
        time.sleep(3)
        self.client.stop()
        
    def publish(self, topic, msg):
        self.client.myPublish(topic, msg)
        print("published\n" + json.dumps(msg) + '\nOn topic: ' + f'{topic}') 
        
    def notify(self, topic, payload):
        messageReceived = json.loads(payload)
        
        returnedMessage = {}
        
        returnedMessage["name"] = self.clientID
        returnedMessage["time"] = str(time.time())

        id = topic.split("/")[-1]
        publish_topic = self.topicP + f"/{id}"

        if messageReceived["condition"] == "alert":
            returnedMessage["status"] = "ON"
            self.publish(publish_topic, returnedMessage)
        else:
            returnedMessage["status"] = "OFF"
            self.publish(publish_topic, returnedMessage)
        
if __name__ == '__main__':
    time.sleep(5)
    LedManager_obj = LedManager('led_manager_info.json', 'service_info.json')

    LedManager_obj.start()
    
    while True:
        time.sleep(3)
