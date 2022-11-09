import paho.mqtt.client as mqtt
import json
import random
import yaml
import sensors.temperatureSensors as TS

TOPIC_NAME_SEND = "temp_data"
TOPIC_NAME_RECIEVE = "temp_req"


TOPIC_NAME_REQUEST = "heartbeat_request"
TOPIC_NAME_STATUS = "heartbeat_status"

sensors = None

# TODO make node red send out a message like "temp request" or something
# or, send out for which sensor we want, 
def temp_request_trigger(client, user_data, msg):
    decoded_msg = msg.payload.decode() 

    decoded_msg = json.loads(decoded_msg) 

    print("We got a message")
    if(msg.topic == TOPIC_NAME_RECIEVE):
        print("Temperature request recieved")
        #OBtain the sensor object from the client
        sensors = user_data["sensors"]

        #If temperature sensors are available, we publish them
        if(sensors):
            
            publication_data = json.dumps(sensors.readSensors())
            if(publication_data):
                print("Sending sensor data")
                client.publish(TOPIC_NAME_SEND, publication_data)

    elif(msg.topic == TOPIC_NAME_REQUEST):
        print("Heartbeat request received")
        client.publish(TOPIC_NAME_STATUS, '{"heartbeat_temperature":1}')
        pass
        # result = SENSORS.readSensors()
        # print(result)

    
    


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


    with open("./config/config.yaml") as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)
    config = dict(config)
    
    mapping = config.get('TEMP_MAP')
    sensors = TS.Sensors(mapping) 
    

    #You can pass the client arguments and access it in your "on message"
    client = mqtt.Client(userdata={"sensors":sensors})
    client.on_connect = on_connect_response 
    client.on_message = temp_request_trigger
    client.on_publish = on_publish

    client.connect("localhost", 1883)
    client.loop_forever()

    
    # make button send out request for temperature (publish)
    # script publish to temp_data

if __name__ == "__main__":
    main()