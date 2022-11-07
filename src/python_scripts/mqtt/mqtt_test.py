import paho.mqtt.client as mqtt
import json

TOPIC_NAME = "relay"

def relay_trigger(client, user_data, msg):
    #Payload gets the actual content of the message, decoding it converts it from a byte array to JSON object
    decoded_msg = msg.payload.decode() 
    #Turns the JSON string into a python dictionary for easy map parsing
    decoded_msg = json.loads(decoded_msg) 
    print("We got a message")
    print(decoded_msg)
    for pins in decoded_msg:
        print(pins)
        print(decoded_msg[pins])


def on_connect_response(client, user_data, flags, rc):
    print("CONNACK server response: "+str(rc))
    client.subscribe(TOPIC_NAME)


def main():
    client = mqtt.Client()
    client.on_connect = on_connect_response 
    client.on_message = relay_trigger

    client.connect("localhost", 1883)
    client.loop_forever()
    

if __name__ == "__main__":
    main()
