from Trashbin import *
import threading

if __name__ == "__main__":
    
    service_info = json.load(open("service_info.json", "r"))
    res_url = 'http://' + service_info["info"]["IP"] + ':' + str(service_info["info"]["port"]) + '/res_cat'
    request_string1 = requests.get(res_url)
    
    res_ip = request_string1.json()["info"]["IP"]
    res_port = request_string1.json()["info"]["port"]
    
    result0 = {}
    
    instance = []
    
    while True:
        time.sleep(5)
        request_url = 'http://' + res_ip + ':' + str(res_port) + '/get_all'
        result = requests.get(request_url)
        result = result.json()
        j = 0
        
        if(result != result0):
            instance = []
            #nuovo trashbin aggiunto o eliminato
            print("Modifiche ricevute! Riavvio...")
            result0 = result
            
            if(result == None):
                print("No TrashBins")
            
            else:
    
                for i in range(len(result)):
                    j = 0
                    tb = TrashBin('trashbin_info.json', 'service_info.json', result[i]["ID"], result[i]["location"])
                    instance.append(tb)
                    # Modify lambda to accept tb as an argument, binding the current tb instance
                    thread = threading.Thread(target=lambda tb=tb: [tb.start(), tb.On()])
                    thread.start()
                    # time.sleep(5)
                    # thread.stop()

        else:
            pass
        
