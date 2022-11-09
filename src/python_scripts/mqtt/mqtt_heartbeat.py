import paho.mqtt.client as mqtt
import json
import random

# A script determines that everything is alive. Sends a request to every topic and sees if its alive, if it is not then do something in the gui
# that says that something is not working in the gui


TOPIC_NAME_SEND = "heartbeat_send" # A string to listen out for. Do a mqtt in to listen
TOPIC_NAME_RECEIVE = "heartbeat_receive" 

def relay_trigger(client, user_data, msg):
    """Activates when the topic is sent too

    Args:
        client (Any): mqtt_client
        user_data (_type_): _description_
        msg (_type_): _description_
    """
    #Payload gets the actual content of the message, decoding it converts it from a byte array to JSON object
    decoded_msg = msg.payload.decode() 
    #Turns the JSON string into a python dictionary for easy map parsing
    decoded_msg = json.loads(decoded_msg) 
    print("We got a message")
    print(decoded_msg)
    for pins in decoded_msg:
        print(pins)
        print(decoded_msg[pins])

    # Need to publish 
    # Subscribe is listen and publish is send out

    # TODO: First need to iterate though all of the topics and check if they are okay, if they are or not, post on node-red
    # Lets make a list for now to simulate it
    
    topicDict =	{
    "topicOne": 0,
    "topicTwo": 1,
    "topicThree": 1
    }
    #PUBLISH HERE
    client.publish(TOPIC_NAME_RECEIVE, str(random.randint(0,2)))




def on_connect_response(client, user_data, flags, rc):
    print("CONNACK server response: "+str(rc))
    client.subscribe(TOPIC_NAME_SEND)


def main():
    client = mqtt.Client()
    client.on_connect = on_connect_response
    # When we recieve a message from a topic i subscripted too, it will call that function.
    client.on_message = relay_trigger

    client.connect("localhost", 1883)
    client.loop_forever()
    

if __name__ == "__main__":
    main()
