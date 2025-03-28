import json
import time as time
from MyMqttBase2 import MyMQTT
import requests

class AlertCheck():

    def __init__(self, alert_check_info, service_info):
        
        self.info = json.load(open(alert_check_info, "r"))
        
        self.clientID = self.info["name"]
        self.serviceType = self.info["ServiceType"]
        self.topicS1 = self.info["topicS1"]
        self.topicS2 = self.info["topicS2"]
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
        self.client.mySubscribe(self.topicS1)
        self.client.mySubscribe(self.topicS2)
    
    def stop(self):
        self.client.unsubscribe(self.topicS1)
        self.client.unsubscribe(self.topicS2)
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
        returnedMessage["TrashBin_ID"] = messageReceived["TrashBinID"]
        returnedMessage["measurement"] = messageReceived["measurementName"]
        returnedMessage["condition"] = messageReceived["condition"]
        
        
        id = topic.split("/")[-1]
        
        publish_topic = self.topicP + f"/{id}"
        
        if messageReceived["condition"] == "alert":
            self.publish(publish_topic, returnedMessage)
        
if __name__ == '__main__':
    
    AlertCheck_obj = AlertCheck('alert_info.json', 'service_info.json')

    AlertCheck_obj.start()
    
    while True:
        time.sleep(3)
