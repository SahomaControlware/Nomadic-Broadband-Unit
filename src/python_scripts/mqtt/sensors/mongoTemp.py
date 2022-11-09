import getpass
import pymongo
import config as config
import time
from time import gmtime, strftime
import datetime
import temperatureSensors as tempSensors


from random import randint


CONNECTION_STRING = config.CONNECTION_STRING
DB_NAME = "test"
UNSHARDED_COLLECTION_NAME = "tasks"
SENSOR_NAME = "Sensor 1"
SAMPLE_FIELD_NAME = "temperature"

def insert_sample_document(collection, currReading):

    currTime = datetime.datetime.now()
    month = currTime.strftime("%B")
    currTime = ("%s %s, %s | %s:%s:%s" %(month, currTime.day, currTime.year, currTime.hour, currTime.minute, currTime.second))


    document_id = collection.insert_one({"Temperature": currReading, "userId": "1", "time": currTime}).inserted_id
    print("Inserted document with _id {}".format(document_id))
    return document_id


def main():

    client = pymongo.MongoClient(CONNECTION_STRING)
    try:
        client.server_info() # validate connection string
    except pymongo.errors.ServerSelectionTimeoutError:
        raise TimeoutError("Invalid API for MongoDB connection string or timed out when attempting to connect")

    collection = client[DB_NAME].tasks

    currReading = tempSensors.readSensor(0)

    insert_sample_document(collection, currReading)





if __name__ == '__main__':
    main()
