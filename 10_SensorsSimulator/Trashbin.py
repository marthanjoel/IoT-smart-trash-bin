from MyMqttBase2 import MyMQTT
import json
import time as time
import requests
import random

class TrashBin():
    def __init__(self, trashbin_info, service_info, TrashBin_ID, location):
        
        self.info = json.load(open(trashbin_info, "r"))
        
        self.clientID = TrashBin_ID
        self.location = self.info["location"]
        self.sensors = self.info["sensors"]
        self.topicP1 = self.info["topicP1"] + f"/{TrashBin_ID}"
        self.topicP2 = self.info["topicP2"] + f"/{TrashBin_ID}"
        self.topicP3 = self.info["topicP3"] + f"/{TrashBin_ID}"
        self.topicP4 = self.info["topicP4"] + f"/{TrashBin_ID}"
        self.topicP5 = self.info["topicP5"] + f"/{TrashBin_ID}"
        self.topicS = self.info["topicS"]
        self.max_capacity = self.info["max_capacity"]
        self.max_weight = self.info["max_weight"]

        self.service_info = json.load(open(service_info, "r"))
                
        request_url = 'http://' + self.service_info["info"]["IP"] + ':' + self.service_info["info"]["port"] + '/broker'
        request_url1 = 'http://' + self.service_info["info"]["IP"] + ':' + self.service_info["info"]["port"] + '/res_cat'
        
        request_string = requests.get(request_url)
        request_string1 = requests.get(request_url1)
        
        subscribe_data = {}
        
        subscribe_data["ID"] = self.clientID
        subscribe_data["location"] = self.location
        subscribe_data["lastUpdate"] = time.time()
        subscribe_data["sensors"] = self.sensors
        subscribe_data["max_capacity"] = self.max_capacity
        subscribe_data["max_weight"] = self.max_weight
        
        headers = {"Content-Type": "application/json"}
                
        print(request_string1.json())
        self.resourceCatalog = request_string1.json()["info"]["IP"]
        self.res_port = request_string1.json()["info"]["port"]
        
        requests.put('http://' + self.resourceCatalog + ':' + str(self.res_port), json = subscribe_data, headers=headers)
        
        self.broker = request_string.json()["IP"]
        self.port = request_string.json()["port"]
        
        self.client = MyMQTT(self.clientID, self.broker, self.port, self)
        
    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topicS)
            
    def stop(self):
        self.client.unsubscribe(self.topicS)
        time.sleep(3)
        self.client.stop()
        
    def notify(self, topic, payload):
        payload = json.loads(payload.decode("utf-8"))
        if topic == self.topicS:
            print(payload)
            if payload["status"] == "ON":
                print("LED ON")
            elif payload["status"] == "OFF":
                print("LED OFF")
            else:
                pass
                
    def publish(self, topic, msg):
        self.client.myPublish(topic, msg)
        print("published\n" + json.dumps(msg) + '\nOn topic: ' + f'{topic}') 
        
    def On(self):
        
        while True:
        
            humidity_data = {
                
                "bn": f"humiditySensor/{self.clientID}",
                "e": {
                    "v" : random.randint(0, 15),
                    "u" : "g/kg",
                    "n" : "humidity",
                    "t" : time.time()
                }
            }
            
            gas_data = {
                "bn": f"GasSensor/{self.clientID}",
                "e": {
                    "v" : random.randint(0, 15),
                    "u" : "m^3",
                    "n" : "gas",
                    "t" : time.time()
                }
            }
            
            temperature_data = {
                "bn": f"temperatureSensor/{self.clientID}",
                "e": {
                    "v" : random.randint(0, 15),
                    "u" : "C°",
                    "n" : "temperature",
                    "t" : time.time()
                }
            }
            
            ultrasonic_data = {
                "bn": f"ultraSonicSensor/{self.clientID}",
                "e": {
                    "v" : random.randint(0, 200),
                    "u" : "m",
                    "n" : "ultraSonic",
                    "t" : time.time()
                }
            }
            
            weight_data = {
                "bn": f"weightSensor/{self.clientID}",
                "e": {
                    "v" : random.randint(0, 200),
                    "u" : "kg",
                    "n" : "weight",
                    "t" : time.time()
                }
            }
            
            
            self.publish(self.topicP1, humidity_data)
            self.publish(self.topicP2, gas_data)
            self.publish(self.topicP3, temperature_data)
            self.publish(self.topicP4, ultrasonic_data)
            self.publish(self.topicP5, weight_data)
            
            time.sleep(5)
    