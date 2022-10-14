import time
import os
import schedule
import threading
import yaml
import pymongo
import kfg
import datetime
import json
import traceback
import temperatureSensors as TS
import relay
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import Twin, TwinProperties, QuerySpecification, QueryResult
from azure.iot.device import Message
from azure.iot.device import IoTHubDeviceClient

HEARTBEAT_INTERVAL_MINUTES = 1
DATABASE_INTERVAL_MINUTES = 1
mongodb_connection_str = ""
mongodb_client = None
g_relay = None
RECEIVED_MESSAGES = 0

GLOBAL_CONFIG = None

def getTime(): 
    clock = time.gmtime() 
    return f"[{clock.tm_mon}/{clock.tm_mday}/{clock.tm_year} - {clock.tm_hour}:{clock.tm_min}:{clock.tm_sec}]"

def kfg_data(multimeter: kfg.KFG, device_client:IoTHubDeviceClient) -> None:

    device_name = multimeter.getName()
    read_data = multimeter.getData(update=False)
    i = 0
    while read_data == None:
        if i > 10: 
            msg = Message("ERROR: Could not read KFG (unplugged?)")
            msg.content_encoding = "utf-8"
            msg.content_type = "applications/json"
            device_client.send_message(msg)
            print(getTime(), "Error: Device may be unplugged, could not read. Error msg sent.")
            return
        print(getTime(),"Didnt get data trying again")
        read_data = multimeter.getData(update=False)
        i += 1
        time.sleep(2)
    if i < 10: 
        msg = Message("{} readings".format(device_name))
        msg.content_encoding = "utf-8"
        msg.content_type = "applications/json"
        msg.custom_properties = {device_name : read_data}
#        print(getTime(),"Sending telemetry data..")
        try:
            device_client.send_message(msg)
 #           print(getTime(),device_name, "telemetry data sent!")
            pass
        except Exception:
            print(getTime(),"Unexpected error couldnt send message")
            traceback.print_exc()
    else: 
        i = 0 

def kfg_data_mongo(multimeter:kfg.KFG, mongodb_client:pymongo.MongoClient):
 #   print(getTime(),"data mongo start")
    read_data = multimeter.getData(update=False)
    if read_data == None: 
        print(getTime(), "KFG_MONGO ERROR: Device disconnected?")
        return
    currTime = datetime.datetime.now()
    month = currTime.strftime("%B")
    currTime = ("%s %s, %s | %s:%s:%s" % (month, currTime.day, currTime.year, currTime.hour, currTime.minute, currTime.second))
    read_data['Time'] = currTime

    collection = mongodb_client["test"].multimeter
  #  print(getTime(),'Inserting into database')
    insert_id = collection.insert_one({'KFG_Data' : read_data}).inserted_id
  #  print(getTime(),'Inserted data id:', insert_id)

#Device twin update for KFG
def kfg_heart_beat(multimeter: kfg.KFG, device_name: str):
#    print(getTime(),"kfg HB start.")
    try: 
        data = multimeter.getData()
        if data != None: 
            status_data = {'status_code': data.get('Output_Status'), 'State': "ON" if data.get('Voltage') > 0 else "OFF"}
        else: 
            status_data = {'status_code': "UNKNOWN", 'State': "OFFLINE"}
    except Exception as e:
        print(e)  
        print(getTime(),"Heart beat error: couldnt get values")
        return

    send_heart_beat(connection_str=GLOBAL_CONFIG.get('IOTHUB_CONNECTION_STRING'), sensor_name=multimeter.getName(), device_id=GLOBAL_CONFIG.get('DEVICE_ID'), status_data=status_data )


#Twin connectin string for IoT Hub
def send_heart_beat(connection_str, sensor_name, device_id, status_data):
    try:
        iot_reg_manager = IoTHubRegistryManager(connection_str)

        # make a tag for Device twin
        last_data = {sensor_name + "_data": status_data}
        twin = iot_reg_manager.get_twin(device_id)
        twin_patch = Twin(tags=last_data, properties=TwinProperties(desired={'power_level': 1}))
        twin = iot_reg_manager.update_twin(device_id, twin_patch, twin.etag)

        #TEST CODE FOR DEVICE TWIN Mongo
        try: 
            currTime = datetime.datetime.now()
            month = currTime.strftime("%B")
            currTime = ("%s %s, %s | %s:%s:%s" % (month, currTime.day, currTime.year, currTime.hour, currTime.minute, currTime.second))
            collection = mongodb_client["test"].device_twin
            insert_id = collection.insert_one({'Device_Twin_Data' : twin.tags, 'Time': currTime}).inserted_id
        except Exception: 
            print(Exception)
            return
        
        #end

 #       print(getTime(),sensor_name, ": HEARTBEAT SENT")
    except Exception as ex:
        print(getTime(),"Unexpected error {0}".format(ex))
        print(getTime(),sensor_name, ": Something went wrong. Sending off heartbeat")
        try:
            iot_reg_manager = IoTHubRegistryManager(connection_str)
            last_data = {sensor_name + "_data" : 'OFFLINE',
                        'Status': 'OFFLINE'
                        }
            twin = iot_reg_manager.get_twin(device_id)
            twin_patch = Twin(tags=last_data, properties=TwinProperties(desired={'power_level': 0}))
            twin = iot_reg_manager.update_twin(device_id, twin_patch, twin.etag)
        except Exception as ex:
            print("Unexpected error {0}".format(ex))
            print(getTime(),"Couldnt send heartbeat for", sensor_name, "!")
        return
    except KeyboardInterrupt:
        print("Keyboard interrupt detected stopping detection!")

    return None

def temperature_heart_beat(sensors):
  #  print(getTime(),"temp HB start")
    config = sensors.getConfig()
    sensors.readSensors()
    send_heart_beat(connection_str = config.get('IOTHUB_CONNECTION_STRING'), sensor_name=sensors.getName(),device_id=config.get('DEVICE_ID'), status_data=sensors.getStatus())
    pass

def temperature_data_mongo(sensors:TS.Sensors, mongodb_client:pymongo.MongoClient):
  #  print(getTime(),"temp db start")
    config= sensors.getConfig()
    sensors.readSensors()

    collection = mongodb_client["test"].tasks
   # print(getTime(),'Inserting Temp_Sensors into database')
    insert_id = collection.insert_one({'Temperature_Sensors' : sensors.getTemps()}).inserted_id
   # print(getTime(),'Inserted data id:', insert_id) 
    


def relay_data_mongo(relay:relay.Relay, mongodb_client: pymongo.MongoClient): 
   # print(getTime(),"relay mongo start")
    currTime = datetime.datetime.now()
    month = currTime.strftime("%B")
    currTime = ("%s %s, %s | %s:%s:%s" % (month, currTime.day, currTime.year, currTime.hour, currTime.minute, currTime.second))

    collection = mongodb_client["test"].relay
    print(getTime(),"Inserting Relay State into database")
    insert_id = collection.insert_one( {'Relay_States' : g_relay.getRelayState(), 
                                        'Time': currTime }).inserted_id
    
  #  print(getTime(),"Inserted relay data id:", insert_id)

def message_handler(message: Message):
    global RECEIVED_MESSAGES
    RECEIVED_MESSAGES += 1
    print("")
    print(getTime(),"Message received:")

    # print data from both system and application (custom) properties
    received_message = vars(message).get('data').decode()

    relay_set = received_message.split(',') 
    if relay_set[1] == "ON" and g_relay.getName() is not None: 
        g_relay.setRelayState(relay_set[0], 1)
    elif relay_set[1] == "OFF": 
        g_relay.setRelayState(relay_set[0], 0)    

    send_heart_beat(GLOBAL_CONFIG.get('IOTHUB_CONNECTION_STRING'), g_relay.getName(), GLOBAL_CONFIG.get('DEVICE_ID'), g_relay.getRelayState())
    print(received_message)
    print("Messages received:", RECEIVED_MESSAGES)
    print("")
    print("updated state:", g_relay.getRelayState()) 
    return received_message

def relay_heart_beat(relay, config): 
  #  print(getTime(),"Relay HB start")
    send_heart_beat(connection_str = config.get('IOTHUB_CONNECTION_STRING'), sensor_name=relay.getName(),device_id=config.get('DEVICE_ID'), status_data=relay.getRelayState())

def loop_thread(schedule):
    while True:
        schedule.run_pending()
        time.sleep(5)

def send_telemetry(config:dict, kfg:kfg.KFG, sensors:TS.Sensors, relay:relay.Relay):
    connection_str = config.get('IOTHUB_DEVICE_CONNECTION_STRING')

    device_client = IoTHubDeviceClient.create_from_connection_string(connection_string=connection_str)

    try:
        print(getTime(),"Connecting to IoT hub...")
        # relay.setRelayState("1", 1)
        device_client.connect()
        device_client.on_message_received = message_handler
        print(getTime(),"Connected...Starting Telemetry.")
        while True:
            time.sleep(DATABASE_INTERVAL_MINUTES * 60)
            if kfg.getName() is not None: 
                kfg_data(kfg, device_client=device_client)

    except KeyboardInterrupt: 
        print("Shutting down")
    except Exception:
        print(str(Exception))
    finally: 
        relay.cleanUp()
        device_client.shutdown() 
        # device_client.disconnect() 

if __name__ == "__main__":
    loop_schedule = schedule.Scheduler()
    print(os.getcwd())
    
    kfg = kfg.KFG(name="KFG_1")
    g_relay = relay.Relay() 

    if kfg.getName() is None:
        print("Could not find kfg")

    with open("./config/config.yaml") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    config = dict(config)
    GLOBAL_CONFIG = config
    kfg.setConfig(config)
    
    #print("Relay state:", g_relay.getRelayState())
    mapping = config.get('TEMP_MAP')
    sensors = TS.Sensors(mapping) 

    mongodb_connection_str = config.get('MONGO_DB_CONNECTION_STRING')



    mongodb_client = pymongo.MongoClient(mongodb_connection_str)
    try:
        mongodb_client.server_info()
    except pymongo.errors.ServerSelectionTimeoutError:
        raise


    #Device twin heartbeats 
    if kfg.getName() is not None: 
        print("Found kfg")
        loop_schedule.every(HEARTBEAT_INTERVAL_MINUTES).minutes.do(kfg_heart_beat, kfg, kfg.getName())
        loop_schedule.every(DATABASE_INTERVAL_MINUTES).minutes.do(kfg_data_mongo, kfg, mongodb_client)
    if sensors.getStatus() is not None:
        print("Found some sensors") 
        loop_schedule.every(HEARTBEAT_INTERVAL_MINUTES).minutes.do(temperature_heart_beat, sensors)
        loop_schedule.every(DATABASE_INTERVAL_MINUTES).minutes.do(temperature_data_mongo, sensors, mongodb_client)
    
    if g_relay.getName() is not None:
        print("Found relays") 
        loop_schedule.every(DATABASE_INTERVAL_MINUTES).minutes.do(relay_data_mongo, g_relay, mongodb_client) 
        loop_schedule.every(HEARTBEAT_INTERVAL_MINUTES).minutes.do(relay_heart_beat, g_relay, config)


    #Runn all scheduled jobs. 
    t = threading.Thread(target=loop_thread, args=(loop_schedule,))

    #Telemetry receiving and sending messages. 
    s = threading.Thread(target=send_telemetry, args=(GLOBAL_CONFIG, kfg, sensors, g_relay,  ))
    try: 
        t.start()
        s.start()

        t.join()
        s.join()
    except Exception:
        pass
    finally:  
        g_relay.cleanUp()
