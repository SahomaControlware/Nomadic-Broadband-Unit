import paho.mqtt.client as mqtt
import json
import random

TOPIC_NAME_SEND = "temp_data"
TOPIC_NAME_RECIEVE = "temp_req"


TOPIC_NAME_REQUEST = "heartbeat_request"
TOPIC_NAME_STATUS = "heartbeat_status"

# TODO make node red send out a message like "temp request" or something
# or, send out for which sensor we want, 
def temp_request_trigger(client, user_data, msg):
    decoded_msg = msg.payload.decode() 

    decoded_msg = json.loads(decoded_msg) 

    print("We got a message")
    if(msg.topic == TOPIC_NAME_RECIEVE):
        print("Temperature request recieved")
    elif(msg.topic == TOPIC_NAME_REQUEST):
        print("Heartbeat request received")

    # print(decoded_msg)

    # PUBLISH HERE
    client.publish(TOPIC_NAME_SEND, str(random.randrange(0, 32)))
    client.publish(TOPIC_NAME_STATUS, '{"heartbeat_temperature":1}')


def on_connect_response(client, user_data, flags, rc):
    print("CONNACK server response: " + str(rc))
    # subscribe to the request for data aka listen for a request
    client.subscribe(TOPIC_NAME_RECIEVE)
    # subscribe to the node red request and check if there has 
    # been a request for a heartbeat. If so, we will publish one
    client.subscribe(TOPIC_NAME_REQUEST)


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