import json
import time
from MyMqttBase2 import MyMQTT
import requests


class QualityCheck():
    def __init__(self, quality_check_info, service_info):
        
        self.info = json.load(open(quality_check_info, "r"))
        
        self.clientID = self.info["name"]
        self.service_info = json.load(open(service_info, "r"))
        
        self.topicS1 = self.info["topicS1"]
        self.topicS2 = self.info["topicS2"]
        self.topicS3 = self.info["topicS3"]       
        self.topicP = self.info["topicP"]
        self.serviceType = self.info["ServiceType"] 

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
        self.client.mySubscribe(self.topicS3)
    
    def stop(self):
        self.client.unsubscribe(self.topicS1)
        self.client.unsubscribe(self.topicS2)
        self.client.unsubscribe(self.topicS3)
        time.sleep(3)
        self.client.stop()
        
    def notify(self, topic, payload):
        messageReceived = json.loads(payload)
        bn = messageReceived["bn"]
        id = bn.split('/')[1]
        
        if topic.split("/")[0:2] == self.topicS1.split("/")[0:2]:
            # humidity
            
            returnMessage = {}
            
            returnMessage["name"] = self.clientID
            returnMessage["time"] = str(time.time())
            returnMessage["measurementName"] = messageReceived["e"]["n"]
            
            trashbin_url = "http://" + str(self.resourceCatalog) + ":" + str(self.res_port) + "/searchByID?param=" + str(id)
            trashbin_info = requests.get(trashbin_url)
            
            returnMessage["entity"] = trashbin_info.json()["entity"]
            
            returnMessage["TrashBinID"] = id
            
            value = messageReceived["e"]["v"]
            
            if float(value) < 5:
                returnMessage["condition"] = "low"
            elif float(value) < 10:
                returnMessage["condition"] = "normal"
            else:
                returnMessage["condition"] = "alert"
            
            publish_topic = self.topicP + f"/{str(id)}"

            self.publish(publish_topic, returnMessage)   
            
            
        elif topic.split("/")[0:2] == self.topicS2.split("/")[0:2]:
            #gas
            
            returnMessage = {}
            
            returnMessage["name"] = self.clientID
            returnMessage["time"] = str(time.time())
            returnMessage["measurementName"] = messageReceived["e"]["n"]
            
            trashbin_url = "http://" + str(self.resourceCatalog) + ":" + str(self.res_port) + "/searchByID?param=" + str(id)
            trashbin_info = requests.get(trashbin_url)
            
            returnMessage["entity"] = trashbin_info.json()["entity"]
            
            returnMessage["TrashBinID"] = id
            
            value = messageReceived["e"]["v"]
            
            if float(value) < 5:
                returnMessage["condition"] = "low"
            elif float(value) < 10:
                returnMessage["condition"] = "normal"
            else:
                returnMessage["condition"] = "alert"

            publish_topic = str(self.topicP) + str(id)

            self.publish(publish_topic, returnMessage)   
            
        elif topic.split("/")[0:2] == self.topicS3.split("/")[0:2]:
            #temperature
            
            returnMessage = {}
            
            returnMessage["name"] = self.clientID
            returnMessage["time"] = str(time.time())
            returnMessage["measurementName"] = messageReceived["e"]["n"]
            
            trashbin_url = "http://" + str(self.resourceCatalog) + ":" + str(self.res_port) + "/searchByID?param=" + str(id)
            trashbin_info = requests.get(trashbin_url)
            
            returnMessage["entity"] = trashbin_info.json()["entity"]
            
            returnMessage["TrashBinID"] = id
            
            value = messageReceived["e"]["v"]
            
            if float(value) < 5:
                returnMessage["condition"] = "low"
            elif float(value) < 10:
                returnMessage["condition"] = "normal"
            else:
                returnMessage["condition"] = "alert"
                
            publish_topic = self.topicP + str(id)

            self.publish(publish_topic, returnMessage)      
        
        else:
            print("Error on msg received, topic not recognized")
       
       
    def publish(self, topic, msg):
        self.client.myPublish(topic, msg)
        print("published\n" + json.dumps(msg) + '\nOn topic: ' + f'{topic}') 
       

if __name__ == '__main__':
    time.sleep(5)
    QualityCheck_obj = QualityCheck('quality_check_info.json', 'service_info.json')

    QualityCheck_obj.start()
    
    while True:
        time.sleep(3)
