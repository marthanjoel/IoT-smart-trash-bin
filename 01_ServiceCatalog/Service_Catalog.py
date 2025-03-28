import json
import cherrypy
import time

class ServiceCatalog():
    
    exposed = True
    
    def __init__(self, settings):
        
        self.settings = settings
        
        self.info = {
            "projectName" : self.settings["projectName"],
            "lastUpdate" : str(time.time()),
            "broker": {
                "IP" : self.settings["broker"]["IP"],
                "port" : self.settings["broker"]["port"]
            },
            
            "ServiceList" : []
        }
        
        json.dump(self.info, open("service_catalog.json", "w"))
        
        
    def SearchByName(self, name):
        
        file = json.load(open("service_catalog.json", "r"))
        
        for service in file["ServiceList"]:
            if service["name"] == name:
                return True
        
        return False
        
        
    def GET(self, *uri, **parameters):
        
        if len(uri) == 1:
            
            if uri[0] == "broker":
                return_value = self.settings["broker"]
                print(return_value)
                return json.dumps(return_value)
            
            elif uri[0] == 'get_service':
                name = parameters["Service_name"]
                
                file = json.load(open("service_catalog.json", "r"))
                
                for service in file["ServiceList"]:
                    if service["name"] == name:
                        return json.dumps(service)                   # Ritorniamo tutto il servizio
                
                raise cherrypy.HTTPError(404, "Service not found") 
            
            elif uri[0] == "res_cat":
                    
                file = json.load(open("service_catalog.json", "r"))
                
                for service in file["ServiceList"]:
                    if service["name"] == "ResourceCatalog":
                        return json.dumps(service) 
                raise cherrypy.HTTPError(400, "resource_catalog not registered yet")
                    
            else:
                error_string = "incorrect URI or PARAMETERS URI" + str(len(uri)) + "PAR" + str(len(parameters))
                raise cherrypy.HTTPError(400, error_string)
    
    def POST(self, *uri, **parameters):
        pass
    
    def PUT(self, *uri, **parameters):
         
        body = cherrypy.request.body.read().decode('utf-8')
        
        body_file = json.loads(body)
        
        name = body_file["name"]
        
        found = self.SearchByName(name)
        
        service = {}
        
        if found == True:
            
            file = json.load(open("service_catalog.json", "r"))
            
            file["lastUpdate"] = str(time.time())
            
            try:
                service["name"] = body_file["name"]
                service["ServiceType"] = body_file["ServiceType"]

                if "MQTT" in service["ServiceType"]:
                    service["topic"] = body_file["topic"]
                if "REST" in service["ServiceType"]:
                    service["info"] = {
                        "IP" : body_file["info"]["IP"],
                        "port" : body_file["info"]["port"]
                    } 
                
            except:
                raise cherrypy.HTTPError(404, "Information missing")
            
            for element in file["ServiceList"]:
                if element["name"] == name:
                    element.update(body_file)
            
            json.dump(file, open("service_catalog.json", "w"))
            
            return print(f"Updated the service: {body_file}")
        
        try:
            service["name"] = body_file["name"]
            service["ServiceType"] = body_file["ServiceType"]

            if "MQTT" in service["ServiceType"]:
                service["topic"] = body_file["topic"]
            if "REST" in service["ServiceType"]:
                service["info"] = {
                "IP" : body_file["info"]["IP"],
                "port" : body_file["info"]["port"]
                } 
                
        except:
            raise cherrypy.HTTPError(404, "Information missing")
        
        file = json.load(open("service_catalog.json", "r"))
        
        file["lastUpdate"] = str(time.time())
        file["ServiceList"].append(service)
        
        json.dump(file, open("service_catalog.json", "w"))
        print(f"Added new service {body_file}")
        
    def DELETE(self, *uri, **parameters):
        pass
        
        
if __name__ == "__main__":
    service_info = 'service_settings.json'
    settings = json.load(open(service_info, 'r'))
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }
    cherrypy.tree.mount(ServiceCatalog(settings), '/', conf)
    cherrypy.config.update(conf)
    cherrypy.config.update({'server.socket_host': settings['info']["IP"]})
    cherrypy.config.update({"server.socket_port": int(settings['info']["port"])})
    cherrypy.engine.start()
    cherrypy.engine.block()
