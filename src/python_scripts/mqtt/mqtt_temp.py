import paho.mqtt.client as mqtt
import json
import random

TOPIC_NAME_SEND = "temp_data"
TOPIC_NAME_RECIEVE = "temp_req"


# TODO make node red send out a message like "temp request" or something
# or, send out for which sensor we want, 
def temp_request_trigger(client, user_data, msg):
    decoded_msg = msg.payload.decode() 

    decoded_msg = json.loads(decoded_msg) 

    print("We got a message")
    print(decoded_msg)

    for pins in decoded_msg:
        print(pins)
        print(decoded_msg[pins])

    # PUBLISH HERE
    client.publish(TOPIC_NAME_SEND, str(random.randrange(0, 32)))


def on_connect_response(client, user_data, flags, rc):
    print("CONNACK server response: " + str(rc))
    # subscribe to the request for data aka listen for a request
    client.subscribe(TOPIC_NAME_RECIEVE)


def on_publish(client, user_data, msg):
    pass
    



def main():
    client = mqtt.Client()
    client.on_connect = on_connect_response 
    client.on_message = temp_request_trigger
    client.on_publish = on_publish

    client.connect("localhost", 1883)
    client.loop_forever()
    
    # make button send out request for temperature (publish)
    # script publish to temp_data

if __name__ == "__main__":
    main()