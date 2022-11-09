import paho.mqtt.client as mqtt
import json
import random as rand

TOPIC_NAME_RECIEVE = "multimeter_request" #listen out for this and respond back with mm reading data
TOPIC_NAME_SEND = "multimeter_status"
HEARTBEAT_TOPIC_SEND = "heartbeat_status" 
HEARTBEAT_TOPIC_RECIEVE = "heartbeat_request" #listen for this and respond back with status\

dict = {
    'Communication_address': 1,
    'Checksum': 108,
    'Voltage': 2361, # in V
    'Current': 150, # in A
    'Remaining_Capacity': 55304,# in Ah
    'Precentage_Left_200Ah': 486385,
    'Cumulative_Capacity': 1263242,# in Ah
    'Watt_hour': 1905378,# in kw.h
    'Running_Time': 122, #in seconds
    'temp_c': 0,
    'Ambient_Temp': 0,
    'Power': 0,
    'Current_Direction': 0,
    'Battery_Life': 2193,
    'Internal_Resistance_Battery': 11797
}

def multimeter_read(client, user_data, msg):
    """_summary_
    Checks for heartbeat 
    Args:
        client (_type_): _description_
        user_data (_type_): _description_
        msg (_type_): _description_
    """

    key = {
        "heartbeat_multimeter":"1"
    }
    
    decoded_msg = msg.payload.decode() 
    #Turns the JSON string into a python dictionary for easy map parsing
    # decoded_msg = json.loads(decoded_msg) 
    # print("We got a message")
    print(decoded_msg)

    # print(msg.topic)
    if 'heartbeat_request' in decoded_msg:
        print("Still alive homie")
        client.publish(HEARTBEAT_TOPIC_SEND, str(key))

    if 'multimeter_request' in decoded_msg:
        data_to_publish = json.dumps(dict)
        voltage = str(round(12 + rand.random(),2))
        print(voltage)
        result = client.publish(TOPIC_NAME_SEND, data_to_publish)



def on_connect_response(client, user_data, flags, rc):
    print("CONNACK server response: "+str(rc))
    client.subscribe(TOPIC_NAME_RECIEVE)
    client.subscribe(HEARTBEAT_TOPIC_RECIEVE)

def on_publish(client, userdata, mid):
    # print(userdata)
    pass

#publish a message when the topic is received

def main():
    client = mqtt.Client()
    client.on_connect = on_connect_response 
    client.on_message = multimeter_read
    client.on_publish = on_publish

    client.connect("localhost", 1883)
    client.loop_forever()
    

if __name__ == "__main__":
    main()
