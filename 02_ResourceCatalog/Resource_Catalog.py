import json
import cherrypy
import time
import requests

class ResourceCatalog():

    exposed = True

    def __init__(self,resource_catalog, settings, service_info):
        
        self.service_info = json.load(open(service_info, "r"))

        self.file_path = resource_catalog
        with open(self.file_path) as file:
            content = file.read()

       
        self.catalog = json.loads(content)
        self.name = "ResourceCatalog"
        self.serviceType = "REST"
        self.ip = settings["info"]["IP"]
        self.port = settings["info"]["port"]

        subscribe_data = {}
        
        subscribe_data["name"] = self.name
        subscribe_data["ServiceType"] = self.serviceType
        subscribe_data["info"] = {
            "IP" : self.ip,
            "port" : int(self.port)
        }
        
        print(subscribe_data)
        
        headers = {"Content-Type": "application/json"}      
        requests.put('http://' + self.service_info["info"]["IP"] + ':' + self.service_info["info"]["port"], json = subscribe_data, headers=headers)
        

    def searchByID(self,ID):

        for element in self.catalog["Devices"]:
            if element["ID"] == ID:
                return element
        
        return None
    
    def searchByLocation(self,location):
        
        devices = []

        for element in self.catalog["Devices"]:
            if element["location"] == location:
                devices.append(element)

        if len(devices) != 0:
            return devices
        else:
            return None
        
    def printAll(self):

        return self.catalog["Devices"]

        
    def GET(self,*path,**query):
        
        selection = path[0]

        if selection == "printAll":
            return json.dumps(self.printAll())
        
        elif selection == "get_all":           # NEW
            with open(self.file_path) as file:
                content = file.read()
                                            # -----------------------
       
            self.catalog = json.loads(content)
            
            return json.dumps(self.catalog["Devices"])

        elif selection == "searchByID":
            
            if len(query) == 0:
                raise cherrypy.HTTPError(400, "missing information")
            
            id = query["param"]
            id = int(id) 
            result = self.searchByID(id)
            if result != None:
                return json.dumps(result)
            else:
                raise cherrypy.HTTPError(400, "ID not present")
            
        elif selection == "searchByLocation":
            
            if len(query) == 0:
                raise cherrypy.HTTPError(400, "missing information")
            
            loc = query["param"]
            result = self.searchByLocation(loc)
            if result != None:
                return json.dumps(result)
            else:
                raise cherrypy.HTTPError(400, "Location not found")
        
        
        elif selection == "get_entities":
            return json.dumps(self.catalog["Entities"])
        
        
        else:
            raise cherrypy.HTTPError(400, "No valid selection")
        

        

    def PUT(self,*path,**query):

        # DEVICES
        if len(query) == 0:
            with open(self.file_path) as file:
                content = file.read()
            catalog = json.loads(content)
            
            body = cherrypy.request.body.read()
            body_file = json.loads(body)

            print(body_file)
            entity = body_file["entity"]

            last_update = str(time.time())

            new_device = {}

            # NEW
            #Create channel for thinghspeak -------------------------------------------------------
            
            print('http://' + self.service_info["info"]["IP"] + ':' + self.service_info["info"]["port"]+"/get_service?Service_name=ThingSpeakAdaptor")

            response = requests.get('http://' + self.service_info["info"]["IP"] + ':' + self.service_info["info"]["port"]+"/get_service?Service_name=ThingSpeakAdaptor")
            
            #print('http://' + self.service_info["info"]["IP"] + ':' + self.service_info["info"]["port"]+"/get_service?Service_name=ThingSpeakAdaptor")
            # Check if the request was successful
            if response.status_code != 200:
                raise cherrypy.HTTPError(500, "Error retrieving data from the API")

            # Parse the JSON response
            json_data = response.json()
            
            print(json_data)
            
            thingspeak_ip = json_data["info"]["IP"]
            thingspeak_port = json_data["info"]["port"]
            
            print("Contatot thingspeak")
            
            print("http://" + thingspeak_ip + ":" + str(thingspeak_port) + "/NewTrashBin")
            
            requests_url = "http://" + thingspeak_ip + ":" + str(thingspeak_port) + "/NewTrashBin" 
            
            response = requests.get(requests_url)
            
            print(response.json())

            # ------------------------------------------------------------------------------------
            
            try:
                new_device["ID"] = response.json()["id"]
                new_device["entity"] = body_file["entity"]
                new_device["location"] = body_file["location"]          
                new_device["max_capacity"] = body_file["max_capacity"]              # RICORDA DI AVER TOLTO 'sensors'. GLI ALTRI PROGRAMMI POTREBBERO NON FUNZIONARE
                new_device["max_weight"] = body_file["max_weight"]                  # ED AVER AGGIUNTO ENTITY
                new_device["last_update"] = last_update
                new_device["WriteAPI"] = response.json()["WriteAPI"]
                new_device["ReadAPI"] = response.json()["ReadAPI"]
            except:
                raise cherrypy.HTTPError(404, "Information missing")
            

            #Add trashbin -------------------------------
                
            catalog["Devices"].append(new_device)

            json.dump(catalog, open(self.file_path,"w"))
            self.catalog = catalog
            

            return response #response is a string ----------------
        

        #ENTITIES USERS
        else:

            with open(self.file_path) as file:
                content = file.read()
            catalog = json.loads(content)
            

            new_user = {}
            body = cherrypy.request.body.read()
            body_file = json.loads(body)
            print(body_file)

            id = body_file["user_ID"]
            entity = body_file["entity"].lower()

            try:
                new_user["user_ID"] = body_file["user_ID"]
                
            except:
                    raise cherrypy.HTTPError(404, "Information missing")
                
            catalog["Entities"][entity]["Users"]["user_ID"].append(new_user["user_ID"])
            json.dump(catalog, open(self.file_path,"w"))
            self.catalog = catalog

            return "Catalog updated for new user"

                      
                
    def DELETE(self,*path,**query):
        
        with open(self.file_path) as file:
            content = file.read()
        catalog = json.loads(content)
                
        id = int(path[0])
        
        # NEW -----------------------------------------
        #delete thingspeak channel
        
        response = requests.get('http://' + self.service_info["info"]["IP"] + ':' + self.service_info["info"]["port"]+"/get_service?Service_name=ThingSpeakAdaptor")

        # Check if the request was successful
        if response.status_code != 200:
            raise cherrypy.HTTPError(500, "Error retrieving data from the API")

        # Parse the JSON response
        json_data = response.json()
        
        thingspeak_ip = json_data["info"]["IP"]
        thingspeak_port = json_data["info"]["port"]
        
        requests_url = "http://" + thingspeak_ip + ":" + str(thingspeak_port) + "/" + str(id)
        print(requests_url)
        
        response = requests.delete(requests_url)

        # -----------------------------------------------------------------------

        for element in catalog["Devices"]:
            if element["ID"] == id:
                catalog["Devices"].remove(element)
                json.dump(catalog, open(self.file_path,"w"))
                self.catalog = catalog

                return print("Deletion completed")
        
        raise cherrypy.HTTPError(400,"ID not found")

        


if __name__ == "__main__":
    resource_info = "resource_settings.json"
    resource_catalog = "resource_catalog.json"
    settings = json.load(open(resource_info, 'r'))
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }
    cherrypy.tree.mount(ResourceCatalog(resource_catalog, settings, 'service_info.json'), '/', conf)
    cherrypy.config.update(conf)
    cherrypy.config.update({'server.socket_host': settings['info']["IP"]})
    cherrypy.config.update({"server.socket_port": int(settings['info']["port"])})
    cherrypy.engine.start()
    cherrypy.engine.block()

