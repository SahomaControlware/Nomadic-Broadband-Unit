import paho.mqtt.client as mqtt
import json
import random as rand

TOPIC_NAME_RECIEVE = "multimeter_request" #listen out for this and respond back with mm reading data
TOPIC_NAME_SEND = "multimeter_status"
HEARTBEAT_TOPIC_SEND = "heartbeat_status" 
HEARTBEAT_TOPIC_RECIEVE = "heartbeat_request" #listen for this and respond back with status

TOPICS = [TOPIC_NAME_RECIEVE, HEARTBEAT_TOPIC_RECIEVE]

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
        voltage = str(round(12 + rand.random(),2))
        print(voltage)
        result = client.publish(TOPIC_NAME_SEND, voltage)

    #Payload gets the actual content of the m/ui/essage, decoding it converts it from a byte array to JSON object

    # for pins in decoded_msg:
    #     print(pins)
        # print(decoded_msg[pins])

    # print(result.rc)    
    # if result != 0:
    #     print("Topic has sent")
    # else:
    #     print("Topic failed to send")    


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
