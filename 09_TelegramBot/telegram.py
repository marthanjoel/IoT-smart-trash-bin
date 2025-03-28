import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
from MyMqttBase2 import MyMQTT
import time as time
import datetime

THINGSPEAK_CHANNLES = 4

# THIS CODE IS MADE TO DEAL WITH ONE SINGLE ENTITY (EXAMPLE: POLITO OR UNITO)
# MANAGEMENT, YOU CAN'T MANAGE MULTIPLE ENTITIES SIMULTANEOUSLY WITH THE 
# SAME TELEGRAM CHAT

class MyBot:
    
    #token: 6540917080:AAHLGf4fHY_49sK4rcXcvmmxSoZIkxeP_cc
    def __init__(self,token, settings, service_info):
    # Local token
        self.tokenBot=token
        # Bot token
        #self.tokenBot=requests.get("http://catalogIP/telegram_token").json()["telegramToken"]
        #create an instance of TelegramBot associated to the specified token
        self.bot=telepot.Bot(self.tokenBot)
        #start a loop to listen chat message from self.bot chat, where
        #self.on_chat_message is a function we have to define to manage 
        #chat messages. Then we run it as a thread, so in parallel to the main
        #program (this one)
        MessageLoop(self.bot,{'chat': self.on_chat_message, 'callback_query': self.on_callback_query}).run_as_thread()
        # I have added to MessageLoop also callback_query to deal with 
        # Inline keyboard messages. Note that MessageLoop is authomatically 
        # able to get if a message belongs to 'chat', 'callback_query' or 
        # anything else, and then it call the function associated to 
        # that specific kind of message.


        # SERVICE SUBSCRIPTION

        self.service_info = json.load(open(service_info, "r"))

        self.ClientID = settings["name"]
        self.serviceType = settings["ServiceType"] # REST, MQTT
        self.topic = settings["topic"] # topic
        self.info = settings["info"] # IP, Port: just to respect the REST strucutre

        subscribe_data = {}
        subscribe_data["name"] = self.ClientID
        subscribe_data["ServiceType"] = self.serviceType
        subscribe_data["topic"] = self.topic
        subscribe_data["info"] = self.info 
        

        headers = {"Content-Type": "application/json"}      
        requests.put('http://' + self.service_info["info"]["IP"] + ':' + self.service_info["info"]["port"], json = subscribe_data, headers=headers)
        
        # BROKER, RESOURCE CATALOG AND STATISTICAL ANALYZER INFO REQUEST

        request_url_broker = 'http://' + self.service_info["info"]["IP"] + ':' + self.service_info["info"]["port"] + '/broker'
        request_url_res = 'http://' + self.service_info["info"]["IP"] + ':' + self.service_info["info"]["port"] + '/res_cat'
        request_url_stat = 'http://' + self.service_info["info"]["IP"] + ':' + str(self.service_info["info"]["port"]) + '/get_service?Service_name=StatisticalAnalizer'

        request_string_broker = requests.get(request_url_broker)
        request_string_res = requests.get(request_url_res)
        request_data_stat = requests.get(request_url_stat)
        
        self.broker = request_string_broker.json()["IP"] #.json() converts the json in a python data
        self.broker_port = request_string_broker.json()["port"]
        
        self.resourceCatalog = request_string_res.json()["info"]["IP"]
        self.res_port = request_string_res.json()["info"]["port"]
        
        self.statIP = request_data_stat.json()["info"]["IP"]
        self.statPort = request_data_stat.json()["info"]["port"]       
    
     
        # TELEGRAM TOPICS SUBSCRIPTION 
        
        self.topic_sub = settings["topic_sub"] 

        # MQQ TOPIC SUBSCRIPTION AND NOTIFICATION

        self.client = MyMQTT(self.ClientID, self.broker, self.broker_port, self)

        # USEFUL ATTRIBUTES FOR MESSAGE MANAGEMENT
        self.current_chat = {} # key: chat_ID , value: state of the conversation
        self.chat_entity = {} # key: chat_ID, value: selected entity
        self.state_list = [1,2,4] #list of chat state that need the updated ENTITIES portion  
        self.chat_add_check = {} # just to guide the addition bin procedure
        self.chatID_alert = {} # chatID for list just for alert used in notify and on_callback_query
        self.chatID_bin_addition = {} # bin to be added with the Addition procedure


    def start(self):
        self.client.start()
        time.sleep(3)  # Timer of 3 second (to deal with asynchronous)
        self.client.mySubscribe(self.topic_sub[0])
    
    def stop(self):
        self.client.unsubscribe(self.topic_sub[0])
        time.sleep(3)
        self.client.stop()

    def notify(self, topic, payload):
        messageReceived = json.loads(payload)
        
        returnedMessage = ""
        
        returnedMessage += "Time: " + str(datetime.datetime.fromtimestamp(float(messageReceived["time"])))
        returnedMessage += "\nTrashBin_ID: " + messageReceived["TrashBin_ID"]       # AGGIUNGERE UN'OPZIONE SULL'ENTITY IN RETURNED MESSAGE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
        returnedMessage += "\nMeasurement: " + messageReceived["measurement"]
        returnedMessage += "\nStatus: " + messageReceived["condition"]
       
        #print(returnedMessage)
        request_entity = 'http://' + self.resourceCatalog + ':' + str(self.res_port) + f'/searchByID?param={messageReceived["TrashBin_ID"]}'
        returned_entity = requests.get(request_entity)
        entity = returned_entity.json()["entity"]
    
        # try except needed because if a user selects alert off during the
        # for iterations, the dictionary self.chatID_alert changes 
        # and this raises an error.
        try:
            for user, user_entity in self.chatID_alert.items():
            
                if entity == user_entity:
                    self.bot.sendMessage(user, text = returnedMessage)
        except:
            pass


    # --------------------------------------------------------------------------    

    def on_chat_message(self,msg):
        global THINGSPEAK_CHANNLES
        # glance(msg) extracts msg information about content_type(text,foto or
        # audio), chat_type(private or public) and chat_ID (ID of the chat).
        # The flavor option specifies the type of information you want to 
        # retrieve from the message
        # I have added the argument "index" to manage on chat messages linked to
        # a specific request, for example realted to a previous keyboard
        # selection

        content_type, chat_type ,chat_ID = telepot.glance(msg, flavor = 'chat')
        message=msg['text']
        #print(self.current_chat[chat_ID])

        if chat_ID not in self.current_chat.keys(): # Here if it is a new chat
            self.current_chat[chat_ID] = 0 

        if self.current_chat[chat_ID] in self.state_list: # I need the updated Entities for each of these states
            request_url_data_stat_entities = 'http://' + self.resourceCatalog + ':' + str(self.res_port) + '/get_entities'
            entities = requests.get(request_url_data_stat_entities)
            self.entities_info = entities.json() # Entities dictionary in resource_catalog.json 
        
        if message == "/start":

            request_url_data_stat_entities = 'http://' + self.resourceCatalog + ':' + str(self.res_port) + '/get_entities'
            entities = requests.get(request_url_data_stat_entities)
            self.entities_info = entities.json() # Entities dictionary in resource_catalog.json 

            lis = []
            for entity in self.entities_info.keys():
                lis.append(entity)
            intro_message = "Available Area Name: " + str(lis)
            intro_message += "\n-Write your Area Name: " 
            self.bot.sendMessage(chat_ID,intro_message)
            self.current_chat[chat_ID] = 1

            # if before typing /start you were with another entity, here you 
            # are automatically removed by the alert list of the previous entity
            if chat_ID in self.chatID_alert.keys():
                del self.chatID_alert[chat_ID]
                

        elif self.current_chat[chat_ID] == 1 and message.lower() not in self.entities_info.keys(): # here only if the Area name is not present
            self.bot.sendMessage(chat_ID,"No valid Area, write /start to see the available ones and start again.")
            self.current_chat[chat_ID] = 0


        elif self.current_chat[chat_ID] == 1 and message.lower() in self.entities_info.keys():
            if chat_ID not in self.entities_info[message.lower()]["Users"]["user_ID"]:
                #print(self.entities_info[message.lower()]["Users"]["user_ID"])
                self.bot.sendMessage(chat_ID,"Type the password to acces the Area: ")
                self.current_chat[chat_ID] = 2
                self.chat_entity[chat_ID] = message.lower()
            else:
                self.bot.sendMessage(chat_ID, text = "You are an authorized user! please type /menu")
                self.current_chat[chat_ID] = 3
                self.chat_entity[chat_ID] = message.lower()


        elif self.current_chat[chat_ID] == 2: #here only if chat_ID is not already authorized
            if message == self.entities_info[self.chat_entity[chat_ID]]['Users']['password']:
                
                self.bot.sendMessage(chat_ID, text = "password accepted! YOU ARE IN :-)\nPlease type /menu")
                self.current_chat[chat_ID] = 3

                # Add the new user
                subscribe_data = {}
                subscribe_data["user_ID"] = chat_ID
                subscribe_data["entity"] = self.chat_entity[chat_ID]
                headers = {"Content-Type": "application/json"}      
                requests.put('http://' + self.resourceCatalog + ':' + str(self.res_port) + '?len=notzero', json = subscribe_data, headers=headers)
        
            
            else:
                self.bot.sendMessage(chat_ID, text = "Wrong password. Please try again now or type /start to change Area and start again")
                self.current_chat[chat_ID] = 2



        elif message.lower() == '/menu' and self.current_chat[chat_ID] == 3:
            # You will be always here once you set the state to 3, unless something go wrong or you decide to exit
            self.inline_option(chat_ID)



        elif self.current_chat[chat_ID] == 4:

            # I can ask information only for my entity bins
            bin_id = message
            authorized_entity = self.chat_entity[chat_ID]

            request_url_bins = 'http://' + self.resourceCatalog + ':' + str(self.res_port) + '/printAll'
            request_string_bins = requests.get(request_url_bins)
            total_bins = request_string_bins.json()
            check = False
            number_check = False

            try:
                number = int(bin_id)
                number_check = True
            except:
                number_check = False

            if number_check == True:
                for element in total_bins:
                    if int(bin_id) == element["ID"] and authorized_entity.lower() == element["entity"]:
                        check = True
            
            if number_check == True and check == True:
                try:
                    answer = requests.get('http://' + self.statIP + ':' + str(self.statPort) + "/?ID="+str(bin_id))
                    #print(answer)
                    bin_info = answer.json()
                    returned_message = "Specific bin " + bin_id + " information:\n_____\n"
                    
                    returned_message += "- Quality check:\nLast value " + str(bin_info["QualityCheck"]["LastValue"])
                    returned_message += "\nAlert percentage " + str(bin_info["QualityCheck"]["AlertPercentage"])
                    
                    returned_message += "\n_____\n-Quantity check:\nLast value " + str(bin_info["QuantityCheck"]["LastValue"])
                    returned_message += "\nAlert percentage " + str(bin_info["QuantityCheck"]["AlertPercentage"])
                    
                    returned_message += "\n_____\n-Temperature:\nLast value " + str(bin_info["Temperature"]["LastValue"])
                    returned_message += "\nMax " + str(bin_info["Temperature"]["Max"]) + "\nMin " + str(bin_info["Temperature"]["Min"])
                    returned_message += "\nAverage " + str(bin_info["Temperature"]["Average"]) + "\nVariance " + str(bin_info["Temperature"]["Variance"])

                    returned_message += "\n_____\n-Humidity:\nLast value " + str(bin_info["Humidity"]["LastValue"])
                    returned_message += "\nMax " + str(bin_info["Humidity"]["Max"]) + "\nMin " + str(bin_info["Humidity"]["Min"])
                    returned_message += "\nAverage " + str(bin_info["Humidity"]["Average"]) + "\nVariance " + str(bin_info["Humidity"]["Variance"])

                    returned_message += "\n_____\n-Ultrasonic:\nLast value " + str(bin_info["Ultrasonic"]["LastValue"])
                    returned_message += "\nMax " + str(bin_info["Ultrasonic"]["Max"]) + "\nMin " + str(bin_info["Ultrasonic"]["Min"])
                    returned_message += "\nAverage " + str(bin_info["Ultrasonic"]["Average"]) + "\nVariance " + str(bin_info["Ultrasonic"]["Variance"])
                    
                    returned_message += "\n_____\n-Weight:\nLast value " + str(bin_info["Weight"]["LastValue"])
                    returned_message += "\nMax " + str(bin_info["Weight"]["Max"]) + "\nMin " + str(bin_info["Weight"]["Min"])
                    returned_message += "\nAverage " + str(bin_info["Weight"]["Average"]) + "\nVariance " + str(bin_info["Weight"]["Variance"])

                    returned_message += "\n_____\n-Gas:\nLast value " + str(bin_info["Gas"]["LastValue"])
                    returned_message += "\nMax " + str(bin_info["Gas"]["Max"]) + "\nMin " + str(bin_info["Gas"]["Min"])
                    returned_message += "\nAverage " + str(bin_info["Gas"]["Average"]) + "\nVariance " + str(bin_info["Gas"]["Variance"])

                    
                    self.bot.sendMessage(chat_ID, text = returned_message)
                    self.inline_option(chat_ID)
                    self.current_chat[chat_ID] = 3
                
                except:
                    #print(json.dumps(bin_info))
                    self.bot.sendMessage(chat_ID, "ERROR retrieving data about the trashbin. Please try again" )
                    # You keep visualizing the Inlinekeyboard
                    self.inline_option(chat_ID)
                    self.current_chat[chat_ID] = 3

            else:
                self.bot.sendMessage(chat_ID, "No valid trashbin. Please try again" )
                # You keep visualizing the Inlinekeyboard
                self.inline_option(chat_ID)
                self.current_chat[chat_ID] = 3


        # Here to add a new bin, then everything have to go back to the keyboard and state 3
        elif self.current_chat[chat_ID] == 5:

           
            # IF YOU WANT TO QUIT
            if message.lower() == 'exit':
                    
                # you do not get in if you want to exit before typing the ID
                # so no error if you are not in chat_add_check 
                if chat_ID in self.chat_add_check.keys(): 
                    del self.chat_add_check[chat_ID]

                self.inline_option(chat_ID)
                self.current_chat[chat_ID] = 3
                
            
            elif chat_ID not in self.chat_add_check.keys(): # this to skip this firt if procedure after the first time
                self.chat_add_check[chat_ID] = 1
                self.chatID_bin_addition[chat_ID] = {}
                self.chatID_bin_addition[chat_ID]["entity"] = self.chat_entity[chat_ID].lower() # you can only add in you authorized entity
                self.chatID_bin_addition[chat_ID]["location"] = message
                self.bot.sendMessage(chat_ID, text = "Type the max capacity volume (m^3):" )

            elif self.chat_add_check[chat_ID] == 1:
                #this try-except is needed because here we need a message that can be converted in float,
                # so it avoids the possible float(message) conversion
                try:
                    self.chatID_bin_addition[chat_ID]["max_capacity"] = float(message)
                    self.bot.sendMessage(chat_ID, text = "Type the max weight (Kg):" )
                    self.chat_add_check[chat_ID] = 2
                except:
                    self.bot.sendMessage(chat_ID, text = "ERROR: capacity can only be a NUMBER. Please repeat correctly the process of addition" )
                    del self.chat_add_check[chat_ID] # PROCESS COMPLETED
                    self.inline_option(chat_ID)
                    self.current_chat[chat_ID] = 3

            elif self.chat_add_check[chat_ID] == 2:
               
               #try-except for the same reasons of the capacity one
                try:
                    self.chatID_bin_addition[chat_ID]["max_weight"] = float(message)
                    print(self.chatID_bin_addition[chat_ID])

                    result = None
                    headers = {"Content-Type": "application/json"}      
                    result = requests.put('http://' + self.resourceCatalog + ':' + str(self.res_port), json = self.chatID_bin_addition[chat_ID], headers=headers)
                    if result == 404:
                        self.bot.sendMessage(chat_ID, text = "ERROR in addition. Please try again" )
                        self.inline_option(chat_ID)
                        self.current_chat[chat_ID] = 3
                    else:
                        print(result.json())
                        result_json_id = result.json()["id"]

                        result_json = result.json()
                        print(result_json)

                        self.bot.sendMessage(chat_ID, text = f"Addition Completed! Catalog updated, you were given ID={result_json_id}")
                        self.inline_option(chat_ID)
                        self.current_chat[chat_ID] = 3
               
                except:
                    self.bot.sendMessage(chat_ID, text = "ERROR: weight can only be a NUMBER. Please repeat correctly the process of addition" )
                    self.inline_option(chat_ID)
                    self.current_chat[chat_ID] = 3
                
                del self.chat_add_check[chat_ID] # PROCESS COMPLETED
                

                
            else:
                self.bot.sendMessage(chat_ID, text = "No valid typing! Repeat the process from /menu")
                self.inline_option(chat_ID)
                self.current_chat[chat_ID] = 3



        elif self.current_chat[chat_ID] == 6:
                    
                    check_number = False
                    try:
                        bin_id = int(message)
                        check_number = True
                    except:
                        check_number = False

                    entity = self.chat_entity[chat_ID].lower() # you can only remove in your authorized entity
                    result = None
                    
                    # try is needed because if the bin_id is not present, the bin_info line would rise an error
                    if check_number == True:
                        try:
                            request_url_bin = 'http://' + self.resourceCatalog + ':' + str(self.res_port) + f'/searchByID?param={str(bin_id)}'
                            request_string_bin = requests.get(request_url_bin)
                            bin_info = request_string_bin.json()

                            # If you are here, it means the trashbin is in the catalog (in general, not only for a specific entity)

                            if entity == bin_info["entity"]:
                                #you are here if the ID is present and the entity is the same
                                headers = {"Content-Type": "application/json"}      
                                result = requests.delete("http://" + self.resourceCatalog + ":" + str(self.res_port) + "/" + str(bin_id) + "/" + str(bin_id), headers=headers)

                                self.bot.sendMessage(chat_ID, text = "Deletion completed SUCCESSFULLY. Please try again")
                                self.inline_option(chat_ID)
                                self.current_chat[chat_ID] = 3

                            else:
                                # you are here if the id is present but your entity is not the same
                                self.bot.sendMessage(chat_ID, text = "No authorized trashbin. Please try again")
                                self.inline_option(chat_ID)
                                self.current_chat[chat_ID] = 3

                        except:
                            # you are here if the trashbin is not present in the catalog beacuse the searchByID function of the Resource Catalog did not found the ID
                            self.bot.sendMessage(chat_ID, text = "Absent trashbin. Please try again")
                            self.inline_option(chat_ID)
                            self.current_chat[chat_ID] = 3
                        
                    else:
                        self.bot.sendMessage(chat_ID, text = "No valid typing for removal. Please try again")
                        self.inline_option(chat_ID)
                        self.current_chat[chat_ID] = 3
                        


        else:
            intro = "/start for general information and start the procedure"
            self.bot.sendMessage(chat_ID, text = "No valid message or wrong typing. Try again typing " + intro)
            self.current_chat[chat_ID] = 0

    # --------------------------------------------------------------------------

    # Function to deal with callback_query messages: They are those type of
    # messages the user sends through an inline keyboard button
    def on_callback_query(self,msg):
        
        # query_id: unique id associated to the callback query
        # from_id: equivalent to chat_id
        # query_data: data associated to the callback_query. It is set in 
        # the inline option function.
    
        # Different options according to different query_data

         # answerCallbackQuery create a small window that appears on top of the 
        # chat, anabling the users to visualize a specific text. Note that it 
        # is not the answer itself, but can be useful for the user to be sure 
        # of having selected the right option. This window disappears in 
        # few seconds
        
        query_id, from_id, query_data = telepot.glance(msg, flavor="callback_query")

        if query_data == "Alert_on":
            if from_id not in self.chatID_alert.keys():
                self.bot.answerCallbackQuery(query_id, text='Selected option: ' + query_data)
                self.chatID_alert[from_id] = self.chat_entity[from_id]
                self.bot.sendMessage(from_id, text = "Alert On")
            else:
                self.bot.sendMessage(from_id, text = "Alert already on. Please turn it off or change option" )
                self.inline_option(from_id) # you go back to the Inline keyboard


        elif query_data == 'Alert_off':
            if from_id in self.chatID_alert.keys():
                self.bot.answerCallbackQuery(query_id, text='Selected option: ' + query_data)
                del self.chatID_alert[from_id]
                self.bot.sendMessage(from_id, text = "Alert Off")
            else:
                self.bot.sendMessage(from_id, text = "Alert already off. Please turn it on or change option" )
                self.inline_option(from_id) # you go back to the Inline keyboard


        elif query_data == 'spec_bin':
            self.bot.answerCallbackQuery(query_id, text='Selected option: ' + query_data)
            self.bot.sendMessage(from_id, text = "specify bin ID: ")
            self.current_chat[from_id] = 4

        elif query_data == 'add':
            self.bot.answerCallbackQuery(query_id, text='Selected option: ' + query_data)

             #here I'm checking if we have still some channel from the thingspeak
             # ------ start check ---- 
            
            request_url_bins = 'http://' + self.resourceCatalog + ':' + str(self.res_port) + '/printAll'
            request_string_bins = requests.get(request_url_bins)
            total_bins = request_string_bins.json()
            counter = 0
            
            for element in total_bins:
                counter += 1

            if counter >= THINGSPEAK_CHANNLES:
                self.bot.sendMessage(from_id, text = "No more space for a new trashbin! select another option from /menu")
                self.inline_option(from_id)
                self.current_chat[from_id] = 3

            # ------- end check -----

            else:
                self.bot.sendMessage(from_id, text = "Follow the next instructions or type EXIT anytime to quit:\n")
                self.bot.sendMessage(from_id, text = "Type the location in entity " + self.chat_entity[from_id].upper() + ":")
                self.current_chat[from_id] = 5  

        elif query_data == 'remove':
            self.bot.answerCallbackQuery(query_id, text='Selected option: ' + query_data)
            self.bot.sendMessage(from_id, text = "Type trashbin ID you want to remove" )
            self.current_chat[from_id] = 6  

        elif query_data == "display":
            try:
                request_url_allbins = 'http://' + self.resourceCatalog + ':' + str(self.res_port) + '/printAll'
                request_string_allbins = requests.get(request_url_allbins)
                all_bins = request_string_allbins.json()

                display_bins = []
                counter_bins = 0 # non so se counter bins possa dare problemi nel caso in cui due utenti lo premano in frazioni di secondo vicine
                for bin in all_bins:
                    if self.chat_entity[from_id] == bin["entity"]:
                        counter_bins += 1
                        display_bins.append(bin)

                if counter_bins > 0:
                    display_message = "Active bins:\n_____\n"
                    for bin in display_bins:
                        display_message += "ID " + str(bin["ID"])
                        display_message += "\nLocation " + bin["location"]
                        display_message += "\nCapacity " + str(bin["max_capacity"])
                        display_message += "\nWeight " + str(bin["max_weight"])
                        display_message += "\nLast update " + str(datetime.datetime.fromtimestamp(float(bin["last_update"])))
                        display_message += "\n_____\n"
                    self.bot.sendMessage(from_id, text=display_message)
                    self.inline_option(from_id)
                    self.current_chat[from_id] = 3
                else:
                    self.bot.sendMessage(from_id, text="No active trashbins")
                    self.inline_option(from_id)
                    self.current_chat[from_id] = 3
                    
            except:
                self.bot.sendMessage(from_id, text="Error retrieving data. Please try later")
                self.inline_option(from_id)
                self.current_chat[from_id] = 3


               





    def inline_option(self,chat_id):
        # It creates the markup keyboard. It appears in the chat and the 
        # user can selects different option visualized as button thanks to the
        # InlineKeyboardButton function. Here we can specify the text
        # to be associated to each button and also the callback_data related
        # to that button selection. The callback_data is useful to reply 
        # in a specific way to each selection thanks to the on_callback_query
        # function.
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Specific bin information', callback_data='spec_bin')],
        [InlineKeyboardButton(text='Alert On', callback_data='Alert_on')],
        [InlineKeyboardButton(text='Alert Off', callback_data='Alert_off')],
        [InlineKeyboardButton(text='Add a new trashbin', callback_data='add')],
        [InlineKeyboardButton(text='Remove an existing trashbin', callback_data='remove')],
        [InlineKeyboardButton(text='Display all the trashbins', callback_data='display')]
        ])

        # usual sendMessage function, but here we use also the attribute 
        # "reply_markup" to replay with a keyboard.
        self.bot.sendMessage(chat_id, 'Select one of the following options:', reply_markup=keyboard)


if __name__ == "__main__":
    time.sleep(15) 
    telegram_info = "telegram_settings.json"
    settings = json.load(open(telegram_info, 'r'))
    
    # Token del bot Telegram
    token = '6540917080:AAHLGf4fHY_49sK4rcXcvmmxSoZIkxeP_cc'
    
    # Crea un'istanza del bot Telegram
    my_bot = MyBot(token,settings,'service_info.json')
    my_bot.start()

    # Avvia il loop dei messaggi
    while True:
        time.sleep(5)
        pass

    #POSSIBLE ADDITIONAL FEATURES
    # - add a new entity from the bot (I did not add this feature for security reasons, only programmers can add a new entity)
    # - add a new section in the catalog json about locations. Logically you can add a trashbin only in a real and valid location.
   