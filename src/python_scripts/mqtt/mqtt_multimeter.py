import paho.mqtt.client as mqtt
import json
import random as rand

TOPIC_NAME_RECIEVE = "multimeter_request"
TOPIC_NAME_SEND = "multimeter_reading"

def multimeter_read(client, user_data, msg):
    #Payload gets the actual content of the m/ui/essage, decoding it converts it from a byte array to JSON object
    decoded_msg = msg.payload.decode() 
    #Turns the JSON string into a python dictionary for easy map parsing
    decoded_msg = json.loads(decoded_msg) 
    print("We got a message")
    print(decoded_msg)
    for pins in decoded_msg:
        print(pins)
        print(decoded_msg[pins])
    voltage = str(round(12 + rand.random(),2))
    result = client.publish(TOPIC_NAME_SEND, voltage)

    print(result.rc)    
    # if result != 0:
    #     print("Topic has sent")
    # else:
    #     print("Topic failed to send")    


def on_connect_response(client, user_data, flags, rc):
    print("CONNACK server response: "+str(rc))
    client.subscribe(TOPIC_NAME_RECIEVE)

def on_publish(client, userdata, mid):
    print(userdata)
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
